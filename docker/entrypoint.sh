#!/bin/bash
set -e

if [ ! -d "$HOME/hadoop-data/namenode/current" ]; then
  hdfs namenode -format -nonInteractive
fi

rm -f /tmp/hadoop-*.pid
hdfs --daemon start namenode
hdfs --daemon start datanode

export JAVA_HOME="$JAVA_HOME_NIFI"
exec /opt/nifi/bin/nifi.sh run
