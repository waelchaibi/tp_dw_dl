#!/bin/bash
set -e

if [ ! -d "$HOME/hadoop-data/namenode/current" ]; then
  hdfs namenode -format -nonInteractive
fi

rm -f /tmp/hadoop-*.pid
hdfs --daemon start namenode
hdfs --daemon start datanode

# Aligne /opt/venv sur uv.lock du dépôt monté sur /opt/tp (librairies ajoutées depuis le build).
uv sync --frozen || echo "uv sync a échoué : environnement de l'image conservé" >&2

nohup jupyter lab --ip=0.0.0.0 --port=8888 --no-browser \
  --ServerApp.root_dir="$HOME/notebooks" \
  --IdentityProvider.token="${JUPYTER_TOKEN:-tp}" \
  > "$HOME/jupyter.log" 2>&1 &

export JAVA_HOME="$JAVA_HOME_NIFI"
exec /opt/nifi/bin/nifi.sh run
