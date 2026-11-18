#!/bin/bash
# UC-04 – commandes exécutées dans le conteneur
# docker compose exec -T lake bash -s <étape> < Jour2/UC04_preuves/uc04.sh
# Étapes : 6 découverte, 8 construction du flux, 9 exécution, 10 erreur, 11 provenance.
# Le fichier d'essai est une copie de income_band.dat. L'original et le dépôt UC-03 ne sont pas modifiés.
set -u
run() { echo; echo "\$ $*"; eval "$@" 2>&1; }
SRC=/data/retail_project/data/income_band/income_band.dat
WORK=/data/nifi/input/income_band.dat
DST=/retail-lake/raw/nifi
NIFI=https://localhost:8443
echo "# Étape $1 – $(date '+%Y-%m-%d %H:%M:%S %Z') – hôte $(hostname) – utilisateur $(whoami)"

api() {
  python3 - "$1" <<'PY'
import json, ssl, sys, time, urllib.error, urllib.parse, urllib.request

cmd = sys.argv[1]
base = "https://localhost:8443"
ctx = ssl._create_unverified_context()
client = "uc04"

def call(method, path, token=None, body=None, form=None, timeout=60):
    headers = {}
    data = None
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, context=ctx, timeout=timeout) as response:
            raw = response.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")
        raise SystemExit(f"HTTP {error.code} {method} {path}\n{detail}")

def creds():
    user = password = None
    with open("/opt/nifi/logs/nifi-app.log", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if "Generated Username [" in line and user is None:
                user = line.split("Generated Username [", 1)[1].split("]", 1)[0]
            elif "Generated Password [" in line and password is None:
                password = line.split("Generated Password [", 1)[1].split("]", 1)[0]
    if not user or not password:
        raise SystemExit("identifiants NiFi absents du journal")
    return user, password

def token():
    user, password = creds()
    raw = call("POST", "/nifi-api/access/token", form={"username": user, "password": password})
    if isinstance(raw, dict):
        raise SystemExit("jeton inattendu")
    return raw if isinstance(raw, str) else str(raw)

def token_text():
    user, password = creds()
    data = urllib.parse.urlencode({"username": user, "password": password}).encode()
    request = urllib.request.Request(
        base + "/nifi-api/access/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(request, context=ctx, timeout=60) as response:
        return response.read().decode()

def root_id(auth):
    flow = call("GET", "/nifi-api/flow/process-groups/root", auth)
    return flow["processGroupFlow"]["id"]

def processors(auth, group):
    listed = call("GET", f"/nifi-api/process-groups/{group}/processors", auth)
    return listed.get("processors", [])

def find_type(auth, name):
    document = call("GET", "/nifi-api/flow/processor-types", auth)
    found = [item for item in document.get("processorTypes", []) if item["type"].endswith("." + name)]
    if not found:
        raise SystemExit(f"processeur {name} introuvable")
    return found[0]

def create_processor(auth, group, type_name, label, x, properties, auto):
    kind = find_type(auth, type_name)
    body = {
        "revision": {"clientId": client, "version": 0},
        "component": {
            "type": kind["type"],
            "bundle": kind["bundle"],
            "name": label,
            "position": {"x": x, "y": 0},
            "config": {
                "properties": properties,
                "autoTerminatedRelationships": auto,
                "schedulingPeriod": "5 sec",
            },
        },
    }
    created = call("POST", f"/nifi-api/process-groups/{group}/processors", auth, body)
    errors = created["component"]["validationErrors"]
    print(f"{label} id={created['component']['id']} valide={not errors}")
    for error in errors:
        print("  validation:", error)
    return created

def by_name(items, name):
    for item in items:
        if item["component"]["name"] == name:
            return item
    return None

def run_state(auth, processor, state):
    revision = processor["revision"]
    body = {
        "revision": {"clientId": revision.get("clientId", client), "version": revision["version"]},
        "state": state,
        "disconnectedNodeAcknowledged": False,
    }
    try:
        call("PUT", f"/nifi-api/processors/{processor['component']['id']}/run-status", auth, body)
    except SystemExit as error:
        if state in str(error) and "already" in str(error).lower():
            print(f"{processor['component']['name']} déjà {state}")
            return
        raise
    print(f"{processor['component']['name']} -> {state}")

def refresh(auth, group, name):
    return by_name(processors(auth, group), name)

def reachable():
    request = urllib.request.Request(base + "/nifi-api/access/config")
    try:
        with urllib.request.urlopen(request, context=ctx, timeout=10) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code

if cmd == "wait":
    for _ in range(90):
        try:
            code = reachable()
            if code < 500:
                print(f"API NiFi joignable (HTTP {code})")
                sys.exit(0)
        except Exception:
            pass
        time.sleep(5)
    raise SystemExit("NiFi ne répond pas")

auth = token_text()
group = root_id(auth)

if cmd == "create":
    existing = processors(auth, group)
    if by_name(existing, "GetFile UC04"):
        print("flux déjà présent, création sautée")
    else:
        getfile = create_processor(
            auth, group, "GetFile", "GetFile UC04", 0,
            {
                "Input Directory": "/data/nifi/input",
                "Keep Source File": "false",
                "Recurse Subdirectories": "false",
            },
            [],
        )
        puthdfs = create_processor(
            auth, group, "PutHDFS", "PutHDFS UC04", 400,
            {
                "Hadoop Configuration Resources": "/opt/hadoop/etc/hadoop/core-site.xml,/opt/hadoop/etc/hadoop/hdfs-site.xml",
                "Directory": "/retail-lake/raw/nifi",
                "Conflict Resolution Strategy": "fail",
            },
            ["success"],
        )
        logattr = create_processor(
            auth, group, "LogAttribute", "LogAttribute echec UC04", 800,
            {"Log Level": "warn", "Log Payload": "false"},
            ["success"],
        )
        for source, destination, relation in (
            (getfile, puthdfs, "success"),
            (puthdfs, logattr, "failure"),
        ):
            body = {
                "revision": {"clientId": client, "version": 0},
                "component": {
                    "source": {"id": source["component"]["id"], "groupId": group, "type": "PROCESSOR"},
                    "destination": {"id": destination["component"]["id"], "groupId": group, "type": "PROCESSOR"},
                    "selectedRelationships": [relation],
                },
            }
            link = call("POST", f"/nifi-api/process-groups/{group}/connections", auth, body)
            print(f"connexion {source['component']['name']} --{relation}--> {destination['component']['name']} id={link['component']['id']}")
    print("GetFile (success) -> PutHDFS (success auto-terminée)")
    print("PutHDFS (failure) -> LogAttribute (success auto-terminée)")

elif cmd == "show":
    for item in processors(auth, group):
        component = item["component"]
        print(f"{component['name']} etat={component['state']} type={component['type'].rsplit('.', 1)[-1]}")
        for key, value in (component["config"]["properties"] or {}).items():
            if value is not None and key in {
                "Input Directory", "Keep Source File", "Recurse Subdirectories",
                "Hadoop Configuration Resources", "Directory", "Conflict Resolution Strategy",
                "Log Level", "Log Payload",
            }:
                print(f"  {key}={value}")
        for error in component.get("validationErrors") or []:
            print("  validation:", error)

elif cmd == "start":
    order = ["PutHDFS UC04", "LogAttribute echec UC04", "GetFile UC04"]
    for name in order:
        item = refresh(auth, group, name)
        if item["component"]["state"] != "RUNNING":
            run_state(auth, item, "RUNNING")
        else:
            print(f"{name} déjà RUNNING")

elif cmd == "stop":
    for item in processors(auth, group):
        if item["component"]["state"] == "RUNNING":
            run_state(auth, refresh(auth, group, item["component"]["name"]), "STOPPED")

elif cmd == "error":
    item = refresh(auth, group, "GetFile UC04")
    run_state(auth, item, "STOPPED")
    time.sleep(1)
    item = refresh(auth, group, "GetFile UC04")
    body = {
        "revision": {"clientId": client, "version": item["revision"]["version"]},
        "component": {
            "id": item["component"]["id"],
            "config": {"properties": {"Input Directory": "/data/nifi/absent"}},
        },
    }
    updated = call("PUT", f"/nifi-api/processors/{item['component']['id']}", auth, body)
    print("Input Directory réglé sur /data/nifi/absent")
    run_state(auth, updated, "RUNNING")
    time.sleep(8)
    board = call("GET", "/nifi-api/flow/bulletin-board?limit=30", auth)
    for bulletin in board.get("bulletinBoard", {}).get("bulletins", []):
        entry = bulletin["bulletin"]
        if "GetFile" in entry.get("sourceName", "") or "absent" in entry.get("message", ""):
            print(f"bulletin {entry.get('level')} {entry.get('sourceName')}: {entry.get('message')}")
    current = refresh(auth, group, "GetFile UC04")
    print(f"GetFile UC04 etat={current['component']['state']} validation={current['component'].get('validationStatus')}")
    for error in current["component"].get("validationErrors") or []:
        print("validation:", error)
    run_state(auth, current, "STOPPED")

elif cmd == "restore":
    item = refresh(auth, group, "GetFile UC04")
    run_state(auth, item, "STOPPED")
    time.sleep(1)
    item = refresh(auth, group, "GetFile UC04")
    body = {
        "revision": {"clientId": client, "version": item["revision"]["version"]},
        "component": {
            "id": item["component"]["id"],
            "config": {"properties": {"Input Directory": "/data/nifi/input"}},
        },
    }
    call("PUT", f"/nifi-api/processors/{item['component']['id']}", auth, body)
    print("Input Directory rétabli sur /data/nifi/input")
    for name in ("PutHDFS UC04", "LogAttribute echec UC04", "GetFile UC04"):
        current = refresh(auth, group, name)
        if current["component"]["state"] == "RUNNING":
            run_state(auth, current, "STOPPED")
    print("processeurs arrêtés, configuration d'origine rétablie")

elif cmd == "provenance":
    body = {"provenance": {"request": {"maxResults": 20}}}
    created = call("POST", "/nifi-api/provenance", auth, body)
    query = created["provenance"]
    request_id = query["id"]
    for _ in range(20):
        if query.get("finished"):
            break
        time.sleep(1)
        query = call("GET", f"/nifi-api/provenance/{request_id}", auth)["provenance"]
    for event in (query.get("results") or {}).get("provenanceEvents", []):
        attributes = {item["name"]: item["value"] for item in event.get("attributes", [])}
        filename = attributes.get("filename", "")
        print(
            f"{event.get('eventTime')} {event.get('eventType')} "
            f"composant={event.get('componentName')} "
            f"flowfile={event.get('flowFileUuid')} fichier={filename}"
        )
    call("DELETE", f"/nifi-api/provenance/{request_id}", auth)
else:
    raise SystemExit(f"commande inconnue: {cmd}")
PY
}

case "$1" in
6)
  run 'ls /opt/nifi/lib/nifi-api-*.jar /opt/nifi/lib/nifi-hadoop-nar-*.nar /opt/nifi/lib/nifi-hadoop-libraries-nar-*.nar'
  run 'grep ^nifi.ui.banner.text= /opt/nifi/conf/nifi.properties || true'
  run 'grep -E "^nifi.web.https.port=|^nifi.web.https.host=" /opt/nifi/conf/nifi.properties'
  api wait
  run 'jps'
  run "curl -k -s -o /dev/null -w '%{http_code}' $NIFI/nifi/"
  echo
  echo "Interface : https://localhost:8443/nifi"
  echo "Identifiants générés au premier démarrage : présents dans le journal, non recopiés ici."
  run 'grep -c "Generated Username" /opt/nifi/logs/nifi-app.log'
  run 'grep -c "Started Application" /opt/nifi/logs/nifi-app.log'
  ;;
8)
  run "ls -l $SRC"
  run "wc -l < $SRC"
  run "head -n 2 $SRC"
  run "cp $SRC $WORK"
  run "ls -l $SRC $WORK"
  run "hdfs dfs -mkdir -p $DST"
  run "hdfs dfs -ls -d $DST"
  echo
  echo "\$ api create"
  api create
  echo
  echo "\$ api show"
  api show
  ;;
9)
  echo
  echo "\$ api start"
  api start
  sleep 12
  echo
  echo "\$ api show"
  api show
  run "hdfs dfs -ls -h $DST"
  run "hdfs dfs -du -h $DST"
  run "hdfs dfs -stat 'taille=%b replication=%r droits=%A proprietaire=%u' $DST/income_band.dat"
  run "sha256sum < $SRC"
  run "hdfs dfs -cat $DST/income_band.dat | sha256sum"
  run "ls -l $WORK || echo 'copie de travail consommée par GetFile'"
  run "ls -l $SRC"
  ;;
10)
  echo
  echo "\$ api error"
  api error
  echo
  echo "\$ api restore"
  api restore
  echo
  echo "\$ api show"
  api show
  run "hdfs dfs -ls -h $DST"
  ;;
11)
  echo
  echo "\$ api provenance"
  api provenance
  echo
  echo "La provenance relie l'identifiant du FlowFile, le nom du fichier et l'heure de chaque événement."
  echo "RECEIVE correspond à la lecture locale, SEND au dépôt HDFS, ATTRIBUTES_MODIFIED aux attributs posés par PutHDFS, DROP à la fin du FlowFile."
  ;;
*)
  echo "étape inconnue: $1" >&2
  exit 1
  ;;
esac
