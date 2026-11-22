"""PDF du Jour 2 : UC03_Hadoop_HDFS.pdf, UC04_ingestion_NiFi.pdf, README_Jour2.pdf.

uv run --no-project --with pikepdf python Jour2/build_docs.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "docs"))
from pdfgen import RACINE, build, encadre, fichier, img, le, note, ok, p, pre, sec, sous, t, ul  # noqa: E402

DATE = le(17)
P3 = "Jour2/UC03_preuves"
P4 = "Jour2/UC04_preuves"
CAP = f"{P4}/captures"


def capture(nom, legende, largeur=100):
    chemin = f"{CAP}/{nom}"
    return img(chemin, legende, largeur) if (RACINE / chemin).exists() else ""


# --------------------------------------------------------------------------- UC-03
uc03 = [
    sec("1. Environnement Hadoop",
        t(["Élément", "Valeur observée", "Preuve"], [
            ["Hadoop", "3.5.0 (binaire Apache)", "environnement/etape1"],
            ["Java", "OpenJDK 17 (Hadoop) ; Java 21 réservé à NiFi", "etape1"],
            ["Système", "Conteneur Docker <code>lake</code>, Ubuntu 24.04, utilisateur <code>etudiant</code>", "etape1"],
            ["Installation", "<code>/opt/hadoop</code>, configuration <code>/opt/hadoop/etc/hadoop</code>", "etape1"],
            ["fs.defaultFS", "<code>hdfs://localhost:9000</code>", "core-site.xml"],
            ["dfs.replication", "1", "hdfs-site.xml"],
            ["Stockage NameNode / DataNode", "<code>~/hadoop-data/namenode</code>, <code>~/hadoop-data/datanode</code> (volume Docker persistant)", "hdfs-site.xml"],
            ["Services (jps)", "NameNode, DataNode, NiFi", "etape1"],
            ["Interface NameNode", "<code>http://localhost:9870</code> (publiée sur 127.0.0.1 seulement)", "compose.yaml"],
            ["Journaux", "0 ligne ERROR / FATAL (NameNode et DataNode)", "etape1"],
        ], [24, 56, 20]),
        p("Mode <b>pseudo-distribué mono-nœud</b> : un NameNode et un DataNode sur la même machine. "
          "Le formatage n'est fait qu'au premier démarrage (<code>docker/entrypoint.sh</code>).")),
    sec("2. Composants HDFS",
        t(["Composant", "Rôle", "État observé"], [
            ["NameNode", "Espace de noms : arborescence, droits, liste des blocs de chaque fichier. Ne stocke pas les données.",
             "Actif, safe mode OFF"],
            ["DataNode", "Stocke les blocs sur disque, envoie heartbeats et rapports de blocs au NameNode.",
             "1 DataNode vivant (127.0.0.1:9866), rack /default-rack"],
            ["Bloc", "Unité de stockage et de réplication (128 Mo ici).", "store_sales.dat = 1 bloc"],
            ["Réplication", "Nombre de copies de chaque bloc.", "1 copie (mono-nœud)"],
        ], [17, 55, 28]),
        fichier(f"{P3}/hdfs/etape2_commandes_hdfs.txt", 1, 8)),
    sec("3. Commandes HDFS exécutées",
        t(["Commande", "But", "Résultat"], [
            ["<code>hdfs dfsadmin -report</code>", "État du cluster", "1 DataNode vivant, 559 Go libres"],
            ["<code>hdfs dfsadmin -safemode get</code>", "Écriture autorisée ?", "Safe mode is OFF"],
            ["<code>hdfs dfs -mkdir -p /retail-lake/...</code>", "Créer les zones", "10 répertoires"],
            ["<code>hdfs dfs -put</code>", "Déposer un fichier", "2 fichiers store_sales déposés"],
            ["<code>hdfs dfs -ls -R / -du -h / -df -h</code>", "Lister, mesurer", "88,5 Mo + 900,6 Ko"],
            ["<code>hdfs dfs -stat</code>", "Taille, réplication, bloc, droits", "92 764 700 o, r=1, rw-r--r--"],
            ["<code>hdfs dfs -cat | sha256sum</code>", "Relire et comparer", "Empreintes identiques"],
            ["<code>hdfs dfs -get</code> + <code>cmp</code>", "Récupération contrôlée", "IDENTIQUE"],
            ["<code>hdfs fsck -files -blocks</code>", "Santé du fichier", "HEALTHY, 0 bloc manquant"],
        ], [36, 30, 34]),
        note("Toutes les commandes sont dans <code>UC03_preuves/uc03.sh</code> ; chaque sortie est horodatée.")),
    sec("4. Arborescence du Data Lake",
        img(f"{P3}/data_lake/schema_arborescence.png", "Arborescence HDFS créée (etape3) et fichiers déposés (etape4, UC-04).", 62),
        t(["Zone", "Rôle", "Contenu actuel"], [
            ["raw/tpcxbb/initial, refresh", "Copie exacte des fichiers reçus, jamais modifiée", "store_sales.dat des deux lots"],
            ["raw/nifi", "Dépôts automatiques par NiFi (UC-04)", "income_band.dat"],
            ["bronze/tpcxbb", "Données lisibles, typées, sans filtre", "Vide (Jour 3)"],
            ["silver", "Données nettoyées, contrôlées", "Vide (Jour 3)"],
            ["gold", "Agrégats et KPI pour l'analyse", "Vide (Jour 3-4)"],
            ["quality", "Rapports de contrôle, lignes rejetées", "Vide"],
            ["logs", "Traces des traitements", "Vide"],
        ], [26, 44, 30])),
    sec("5. Inventaire des fichiers TPCx-BB utilisés",
        t(["Fichier", "Source (lecture seule)", "Destination HDFS", "Taille", "Lignes", "Structure"], [
            ["store_sales.dat (initial)", "/data/retail_project/data/store_sales/", "/retail-lake/raw/tpcxbb/initial/store_sales/",
             "92 764 700 o", "667 579", "23 champs, séparateur |, sans en-tête"],
            ["store_sales.dat (refresh)", "/data/retail_project/data_refresh/store_sales/", "/retail-lake/raw/tpcxbb/refresh/store_sales/",
             "922 171 o", "6 632", "idem"],
            ["income_band.dat", "/data/retail_project/data/income_band/", "/retail-lake/raw/nifi/ (via NiFi)", "327 o", "20",
             "3 champs, séparateur |"],
        ], [17, 22, 24, 12, 9, 16], cls="s"),
        p("Provenance : kit <code>retail_project.zip</code> fourni (TPCx-BB synthétique), monté en lecture seule dans le conteneur. "
          "Les originaux ne sont jamais modifiés.")),
    sec("6. Dépôt et vérifications",
        t(["Contrôle", "Méthode", "Résultat", ""], [
            ["Présence", "<code>hdfs dfs -ls -R</code>", "2 fichiers aux chemins attendus", ok()],
            ["Taille", "<code>hdfs dfs -stat %b</code> vs <code>stat -c %s</code>", "92 764 700 = 92 764 700", ok()],
            ["Intégrité initial", "sha256 local vs relu dans HDFS", "7e0a7f16…3d2e des deux côtés", ok()],
            ["Intégrité refresh", "sha256 local vs relu dans HDFS", "3c71c010…23df des deux côtés", ok()],
            ["Récupération", "<code>hdfs dfs -get</code> puis <code>cmp</code>", "IDENTIQUE", ok()],
            ["Lisibilité", "<code>hdfs dfs -cat | head -n 2</code>", "2 premières lignes = source", ok()],
            ["Permissions", "<code>hdfs dfs -stat %u:%g %A</code>", "etudiant:supergroup, rw-r--r--", ok()],
            ["Santé", "<code>hdfs fsck</code>", "HEALTHY, 1 bloc, réplication 1", ok()],
        ], [17, 36, 39, 8]),
        fichier(f"{P3}/data_lake/etape5_verification.txt", 22, 39)),
    sec("7. Difficultés et solutions",
        t(["Difficulté", "Cause", "Solution"], [
            ["Kit illisible dans le conteneur", "SELinux (Fedora) bloque le montage", "<code>security_opt: label=disable</code>, montage <code>:ro</code>"],
            ["<code>file: command not found</code> (etape4)", "Outil absent de l'image", "Structure vérifiée par <code>head</code> + <code>awk</code> ; <code>file</code> ajouté à l'image"],
            ["<code>cat: Unable to write to output stream</code>", "<code>head</code> ferme le tube après 2 lignes", "Message attendu, sans effet sur HDFS"],
            ["Reformatage destructeur", "<code>namenode -format</code> efface HDFS", "Formatage seulement si <code>namenode/current</code> absent"],
            ["Deux versions de Java", "Hadoop 3.5 : Java 17 ; NiFi 2.12 : Java 21", "Deux JDK, <code>JAVA_HOME</code> fixé par service"],
            ["<code>entrypoint.sh</code> refusé (CRLF)", "Fichier édité sous Windows", "Fins de ligne normalisées au build"],
        ], [30, 32, 38])),
    sec("Annexe – preuves UC-03",
        t(["Fichier", "Ce qu'il démontre"], [
            ["environnement/etape1_environnement.txt", "Version Hadoop, Java, configuration, services jps, rapport dfsadmin, journaux"],
            ["hdfs/etape2_commandes_hdfs.txt", "Safe mode, topologie, création de /retail-lake, espace disponible"],
            ["data_lake/etape3_arborescence.txt", "Création des zones raw, bronze, silver, gold, quality, logs"],
            ["data_lake/etape4_depot.txt", "Inspection du fichier source puis dépôt des deux lots"],
            ["data_lake/etape5_verification.txt", "Présence, taille, sha256, récupération, permissions, fsck"],
            ["data_lake/schema_arborescence.png", "Schéma de l'arborescence"],
            ["uc03.sh", "Script des commandes, rejouable étape par étape"],
        ], [42, 58])),
]

# --------------------------------------------------------------------------- UC-04
uc04 = [
    sec("1. Environnement NiFi",
        t(["Élément", "Valeur"], [
            ["Version", "Apache NiFi 2.12.0 (<code>nifi-api-2.12.0.jar</code>)"],
            ["Java", "21 (Hadoop reste en Java 17)"],
            ["Interface", "<code>https://localhost:8443/nifi</code>, HTTPS, certificat auto-signé"],
            ["Authentification", "Single user, identifiants générés au premier démarrage (non recopiés)"],
            ["Composants Hadoop", "<code>nifi-hadoop-nar</code> et <code>nifi-hadoop-libraries-nar</code> 2.12.0 ajoutés"],
            ["Configuration Hadoop lue", "<code>core-site.xml</code>, <code>hdfs-site.xml</code> de <code>/opt/hadoop/etc/hadoop</code>"],
            ["État", "API joignable, interface HTTP 200, <code>Started Application</code> dans le journal"],
            ["Sécurité", "Port publié sur 127.0.0.1 uniquement ; aucun secret dans le dépôt"],
        ], [26, 74]),
        capture("nifi_interface.png", "Interface NiFi et flux UC-04 sur le canvas (rejeu du 22/11/2026).")),
    sec("2. Concepts NiFi",
        t(["Concept", "Définition", "Dans notre flux"], [
            ["FlowFile", "Contenu + attributs (filename, path, uuid…)", "income_band.dat, uuid 27315ace…"],
            ["Processor", "Une opération sur les FlowFiles", "GetFile, PutHDFS, LogAttribute"],
            ["Connection", "Lien entre deux processeurs pour une relation", "GetFile→PutHDFS (success), PutHDFS→LogAttribute (failure)"],
            ["Queue", "File d'attente portée par une connexion", "Visible sur chaque connexion"],
            ["Process Group", "Conteneur qui regroupe un flux", "Groupe racine du canvas"],
            ["Controller Service", "Service partagé (pool, client…) utilisé par des processeurs", "Aucun : PutHDFS lit directement la conf Hadoop"],
            ["Provenance Repository", "Historique des événements de chaque FlowFile", "RECEIVE, SEND, ATTRIBUTES_MODIFIED, DROP"],
        ], [20, 42, 38])),
    sec("3. Flux d'ingestion GetFile → PutHDFS",
        img(f"{P4}/configuration/schema_flux_nifi.png", "Flux réalisé : la relation failure n'est pas supprimée, elle est journalisée.", 100),
        capture("nifi_flux.png", "Flux sur le canvas NiFi : processeurs, connexions et files d'attente."),
        note("Flux créé par l'API REST de NiFi (mêmes objets que l'interface), script <code>UC04_preuves/uc04.sh</code>, étape 8.")),
    sec("4. Paramètres des processeurs",
        sous("GetFile UC04",
             t(["Propriété", "Valeur", "Raison"], [
                 ["Input Directory", "<code>/data/nifi/input</code>", "Dossier d'arrivée, ne contient qu'une copie de travail"],
                 ["Keep Source File", "false", "Fichier consommé : pas de relecture en boucle"],
                 ["Recurse Subdirectories", "false", "Seul le dossier d'entrée est lu"],
                 ["Run schedule", "5 s", "Scrutation régulière"],
             ], [28, 30, 42])),
        sous("PutHDFS UC04",
             t(["Propriété", "Valeur", "Raison"], [
                 ["Hadoop Configuration Resources", "<code>/opt/hadoop/etc/hadoop/core-site.xml,…/hdfs-site.xml</code>", "Trouver le NameNode"],
                 ["Directory", "<code>/retail-lake/raw/nifi</code>", "Zone Raw, distincte du dépôt manuel UC-03"],
                 ["Conflict Resolution Strategy", "fail", "Jamais d'écrasement silencieux"],
             ], [28, 42, 30]))),
    sec("5. Relations success et failure",
        t(["Processeur", "Relation", "Traitement", "Effet"], [
            ["GetFile", "success", "→ PutHDFS", "Le fichier lu part vers HDFS"],
            ["PutHDFS", "success", "Auto-terminée", "Dépôt terminé, FlowFile clos"],
            ["PutHDFS", "failure", "→ LogAttribute (warn)", "Échec visible dans la file et dans nifi-app.log"],
            ["LogAttribute", "success", "Auto-terminée", "Après journalisation"],
        ], [20, 16, 28, 36])),
    sec("6. Scénario de test et résultats",
        t(["Étape", "Action", "Résultat"], [
            ["Préparer", "Copie de <code>income_band.dat</code> (327 o, 20 lignes) dans /data/nifi/input", "Original intact"],
            ["Destination", "<code>hdfs dfs -mkdir -p /retail-lake/raw/nifi</code>", "Répertoire créé"],
            ["Démarrer", "PutHDFS, LogAttribute, puis GetFile", "3 processeurs RUNNING"],
            ["Vérifier HDFS", "<code>hdfs dfs -ls -h</code>, <code>-stat</code>", "income_band.dat, 327 o, r=1"],
            ["Intégrité", "sha256 source vs <code>hdfs dfs -cat</code>", "7d8b1e18…d5a4 identiques " + ok()],
            ["Source", "<code>ls /data/nifi/input</code>", "Copie consommée (Keep Source File=false)"],
        ], [16, 50, 34]),
        capture("nifi_compteurs.png", "Compteurs In / Out des processeurs après le transfert."),
        fichier(f"{P4}/execution/etape9_execution.txt", 21, 34)),
    sec("7. Gestion des erreurs",
        sous("Test contrôlé : dossier source inexistant",
             fichier(f"{P4}/erreurs/etape10_erreur.txt", 3, 9),
             t(["Étape", "Constat"], [
                 ["Erreur", "Input Directory = <code>/data/nifi/absent</code>"],
                 ["Message", "<i>Directory does not exist</i> : processeur INVALID, il ne démarre pas"],
                 ["Diagnostic", "Erreur de configuration, détectée par la validation avant tout transfert"],
                 ["Correction", "Input Directory rétabli sur <code>/data/nifi/input</code>, processeur valide"],
             ], [20, 80])),
        sous("Test contrôlé : même fichier déposé deux fois (relation failure)",
             fichier(f"{P4}/erreurs/etape12_doublon.txt", 15, 33),
             t(["Étape", "Constat"], [
                 ["Erreur", "income_band.dat arrive à nouveau alors qu'il existe déjà dans <code>/retail-lake/raw/nifi</code>"],
                 ["Comportement", "PutHDFS (Conflict=fail) pénalise le FlowFile et le route vers <b>failure</b>"],
                 ["Diagnostic", "File failure → LogAttribute (warn) : nom, chemin et attributs écrits dans nifi-app.log"],
                 ["Résultat", "Le fichier HDFS n'est pas écrasé (même horodatage 17:28) ; aucun doublon créé"],
                 ["Compteurs", "Fenêtre de 5 min : 1 dépôt réussi (étape 9) + 2 arrivées du doublon"],
             ], [20, 80])),
        sous("Récapitulatif des erreurs rencontrées",
             t(["#", "Erreur", "Diagnostic", "Correction"], [
                 ["1", "PutHDFS introuvable", "NiFi 2.x ne livre plus les NAR Hadoop", "Ajout des 2 NAR Hadoop 2.12.0 à l'image"],
                 ["2", "Processeurs invalides à la création", "Relations non connectées, non auto-terminées", "Connexions success / failure, auto-terminaison"],
                 ["3", "Interface refusée depuis l'hôte", "Hôte HTTPS et en-tête proxy", "<code>web.https.host=0.0.0.0</code>, <code>proxy.host=localhost:8443</code>"],
                 ["4", "Mot de passe inconnu", "Généré au 1er démarrage", "Lu dans nifi-app.log, jamais versionné"],
                 ["5", "Dossier source absent (test)", "Validation GetFile", "Chemin rétabli"],
                 ["6", "Fichier déjà présent (test)", "Conflict=fail → failure, pénalité 30 s", "Fichier non écrasé, journalisé ; renommer ou archiver avant rejeu"],
             ], [5, 28, 33, 34], cls="s"))),
    sec("8. Provenance",
        t(["Heure (UTC)", "Événement", "Composant", "Signification"], [
            ["10:19:52.806", "RECEIVE", "GetFile UC04", "Fichier lu sur le disque local"],
            ["10:19:58.059", "SEND", "PutHDFS UC04", "Fichier écrit dans HDFS"],
            ["10:19:58.061", "ATTRIBUTES_MODIFIED", "PutHDFS UC04", "Attributs de dépôt ajoutés"],
            ["10:19:58.061", "DROP", "PutHDFS UC04", "Fin du FlowFile (success auto-terminée)"],
        ], [17, 23, 20, 40]),
        p("Même FlowFile <code>27315ace-4be8-4bdb-bdbe-ccfb479aa047</code>, même nom <code>income_band.dat</code>, 18/11/2026. "
          "L'identifiant, l'heure et le composant de chaque événement retracent le parcours : disque local → NiFi → HDFS."),
        capture("nifi_provenance.png", "Événements de provenance du FlowFile dans l'interface (rejeu du 22/11/2026).")),
    sec("9. Questions de recul",
        t(["#", "Question", "Réponse"], [
            ["1", "Rôle du NameNode ?", "Tenir l'arborescence, les droits et l'emplacement des blocs. Il ne stocke pas les données."],
            ["2", "NameNode vs DataNode ?", "Le NameNode gère les métadonnées ; les DataNodes stockent les blocs et se signalent à lui."],
            ["3", "Pourquoi des blocs ?", "Stocker des fichiers plus grands qu'un disque, lire en parallèle, répliquer bloc par bloc."],
            ["4", "Intérêt de la réplication ?", "Survivre à la perte d'un nœud et lire au plus près. Ici 1 copie : aucune tolérance."],
            ["5", "Pourquoi des zones ?", "Séparer brut, nettoyé et analytique : droits, qualité et rejeu par zone."],
            ["6", "Pourquoi garder Raw ?", "Preuve d'origine, audit, retraitement si une règle change."],
            ["7", "Rôle d'un FlowFile ?", "Porter le contenu et ses attributs d'un processeur à l'autre."],
            ["8", "Processor vs Connection ?", "Le processeur agit ; la connexion transporte une relation et porte la file d'attente."],
            ["9", "Pourquoi la provenance ?", "Savoir quoi, quand, où ; diagnostiquer et rejouer."],
            ["10", "Échec technique vs rejet métier ?", "Technique : le transfert échoue (HDFS, droits, conflit) → failure, on corrige et rejoue. Métier : le fichier arrive mais viole une règle → quarantaine, pas de rejeu."],
            ["11", "Relance sans contrôle ?", "Doublons, KPI gonflés ou écrasement. Ici : Conflict=fail et source consommée."],
            ["12", "Limites du mono-nœud ?", "Réplication 1, point unique de panne, pas de parallélisme, performances non représentatives."],
            ["13", "Copie locale ≠ dépôt HDFS ?", "Elle ne passe ni par le NameNode ni par un DataNode. Preuve : ls, stat, fsck, sha256 relu dans HDFS."],
            ["14", "Que garder pour reproduire ?", "Fichier et empreinte, chemins, date, versions, configuration des processeurs, identifiant FlowFile."],
        ], [5, 25, 70], cls="s")),
    sec("Annexe – preuves UC-04",
        t(["Fichier", "Ce qu'il démontre"], [
            ["execution/etape6_decouverte.txt", "Version, NAR Hadoop, port, état du service"],
            ["configuration/etape8_flux.txt", "Fichier de test, création du flux, propriétés"],
            ["configuration/schema_flux_nifi.png", "Schéma du flux"],
            ["execution/etape9_execution.txt", "Démarrage, dépôt HDFS, sha256, source consommée"],
            ["erreurs/etape10_erreur.txt", "Test d'erreur de configuration, message, correction"],
            ["erreurs/etape12_doublon.txt", "Doublon routé vers failure, compteurs, journal LogAttribute (22/11)"],
            ["provenance/etape11_provenance.txt", "Événements de provenance du FlowFile"],
            ["captures/rejeu_etape6/8/9.txt", "Rejeu du 22/11/2026 sur la stack actuelle : même flux, même sha256"],
            ["uc04.sh", "Script des étapes 6 à 11 (API REST NiFi)"],
        ], [42, 58])),
]

# --------------------------------------------------------------------------- README
readme = [
    sec("Contenu",
        pre("""
Jour2/
|-- UC03_Hadoop_HDFS.pdf
|-- UC03_preuves/        environnement/  hdfs/  data_lake/  uc03.sh
|-- UC04_ingestion_NiFi.pdf
|-- UC04_preuves/        configuration/  execution/  erreurs/  provenance/  captures/  uc04.sh
|-- README_Jour2.pdf
`-- build_docs.py        génère les trois PDF
""")),
    sec("Versions",
        t(["Composant", "Version", "Emplacement"], [
            ["Docker image <code>retail-lake</code>", "construite par <code>docker/Dockerfile</code>", "service <code>lake</code>"],
            ["Hadoop / HDFS", "3.5.0, Java 17", "<code>/opt/hadoop</code>"],
            ["NiFi", "2.12.0, Java 21", "<code>/opt/nifi</code>"],
            ["Kit TPCx-BB", "retail_project.zip fourni", "<code>./retail_project</code> → <code>/data/retail_project</code> (lecture seule)"],
        ], [32, 32, 36])),
    sec("Démarrage",
        pre("""
unzip retail_project.zip            # à la racine du dépôt, dossier ignoré par Git
docker compose up -d --build        # HDFS, NiFi (et Jupyter, MinIO, Trino pour les jours 3-4)
docker compose exec lake jps        # NameNode, DataNode, NiFi
"""),
        p("Interfaces : NameNode <code>http://localhost:9870</code>, NiFi <code>https://localhost:8443/nifi</code>. "
          "Identifiants NiFi : <code>docker compose exec lake grep Generated /opt/nifi/logs/nifi-app.log</code>.")),
    sec("Rejouer les preuves",
        pre("""
docker compose exec -T lake bash -s 1 < Jour2/UC03_preuves/uc03.sh   # étapes 1 à 5
docker compose exec -T lake bash -s 8 < Jour2/UC04_preuves/uc04.sh   # étapes 6, 8, 9, 10, 11
"""),
        note("<code>uc03.sh</code> est lancé de la même façon avec le numéro d'étape. Le formatage HDFS n'est jamais relancé.")),
    sec("Chemins HDFS et paramètres NiFi",
        t(["Élément", "Valeur"], [
            ["Racine", "<code>hdfs://localhost:9000/retail-lake</code>"],
            ["Dépôt manuel", "<code>/retail-lake/raw/tpcxbb/{initial,refresh}/store_sales/</code>"],
            ["Dépôt NiFi", "<code>/retail-lake/raw/nifi/</code>"],
            ["GetFile", "Input Directory <code>/data/nifi/input</code>, Keep Source File false, Recurse false"],
            ["PutHDFS", "Conf Hadoop <code>/opt/hadoop/etc/hadoop/*-site.xml</code>, Directory <code>/retail-lake/raw/nifi</code>, Conflict fail"],
            ["Dossiers locaux NiFi", "<code>/data/nifi/input</code>, <code>/data/nifi/archive</code>, <code>/data/nifi/error</code>"],
        ], [24, 76])),
    sec("Arrêt",
        pre("""
docker compose stop        # arrêt propre : NiFi puis HDFS (stop_grace_period 60 s)
docker compose down        # supprime les conteneurs, garde les volumes (HDFS, NiFi)
"""),
        encadre("Ne pas utiliser <code>docker compose down -v</code> : les volumes contiennent HDFS et le flux NiFi.")),
    sec("Parties facultatives",
        t(["Activité", "Statut", "Preuve"], [
            ["CO-03 Contrôles d'intégrité", "Réalisé", "sha256 et cmp local / HDFS (UC-03 etape5, UC-04 etape9)"],
            ["CO-01, CO-02, CO-04, CO-05", "Non réalisé", "—"],
            ["AV-01 à AV-05", "Non réalisé", "—"],
        ], [36, 18, 46])),
]

if __name__ == "__main__":
    build("Jour2/UC03_Hadoop_HDFS.pdf", "UC-03", "Hadoop, HDFS et création du Data Lake", "".join(uc03), DATE,
          "Jour 2 – UC-03", "Hadoop, HDFS, Data Lake, TPCx-BB")
    build("Jour2/UC04_ingestion_NiFi.pdf", "UC-04", "Ingestion et orchestration avec Apache NiFi", "".join(uc04), DATE,
          "Jour 2 – UC-04", "NiFi, GetFile, PutHDFS, provenance")
    build("Jour2/README_Jour2.pdf", "README Jour 2", "Reproduction de l'environnement et des preuves", "".join(readme), DATE,
          "Jour 2 – README", "reproduction, Docker, HDFS, NiFi")
