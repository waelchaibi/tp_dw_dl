#!/bin/bash
set -e

if [ ! -d "$HOME/hadoop-data/namenode/current" ]; then
  hdfs namenode -format -nonInteractive
fi

rm -f /tmp/hadoop-*.pid
hdfs --daemon start namenode
hdfs --daemon start datanode

nohup jupyter lab --ip=0.0.0.0 --port=8888 --no-browser \
  --ServerApp.root_dir="$HOME/notebooks" \
  --IdentityProvider.token="${JUPYTER_TOKEN:-tp}" \
  > "$HOME/jupyter.log" 2>&1 &

export JAVA_HOME="$JAVA_HOME_NIFI"
exec /opt/nifi/bin/nifi.sh run
