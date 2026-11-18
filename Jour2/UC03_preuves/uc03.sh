#!/bin/bash
# UC-03 – commandes exécutées dans le conteneur (docker compose exec -T lake bash < uc03.sh <étape>)
run() { echo; echo "\$ $*"; eval "$@" 2>&1; }
SRC=/data/retail_project/data/store_sales/store_sales.dat
REF=/data/retail_project/data_refresh/store_sales/store_sales.dat
DST=/retail-lake/raw/tpcxbb/initial/store_sales
DSTR=/retail-lake/raw/tpcxbb/refresh/store_sales
echo "# Étape $1 – $(date '+%Y-%m-%d %H:%M:%S %Z') – hôte $(hostname) – utilisateur $(whoami)"
case "$1" in
1)
  run hadoop version
  run 'echo $HADOOP_HOME $HADOOP_CONF_DIR'
  run 'grep -v "^#" $HADOOP_HOME/etc/hadoop/hadoop-env.sh | grep JAVA_HOME'
  run cat '$HADOOP_CONF_DIR/core-site.xml'
  run cat '$HADOOP_CONF_DIR/hdfs-site.xml'
  run jps
  run hdfs dfsadmin -report
  run 'grep -c -E "ERROR|FATAL" $HADOOP_HOME/logs/*namenode*.log $HADOOP_HOME/logs/*datanode*.log'
  ;;
2)
  run hdfs dfsadmin -safemode get
  run hdfs dfsadmin -printTopology
  run hdfs dfs -ls /
  run hdfs dfs -mkdir -p /retail-lake
  run hdfs dfs -ls -d /retail-lake
  run hdfs dfs -ls /retail-lake
  run hdfs dfs -du -h /retail-lake
  run hdfs dfs -df -h /
  ;;
3)
  for d in raw/tpcxbb/initial raw/tpcxbb/refresh bronze/tpcxbb silver gold quality logs; do
    run hdfs dfs -mkdir -p /retail-lake/$d
  done
  run hdfs dfs -ls -R /retail-lake
  ;;
4)
  run ls -l $SRC
  run 'wc -l < '$SRC
  run 'head -n 2 '$SRC
  run "head -n 1 $SRC | awk -F'|' '{print NF \" colonnes, séparateur |\"}'"
  run file $SRC
  run hdfs dfs -mkdir -p $DST $DSTR
  run hdfs dfs -put $SRC $DST/
  run hdfs dfs -put $REF $DSTR/
  run hdfs dfs -ls -h $DST $DSTR
  run ls -l $SRC $REF
  ;;
5)
  run hdfs dfs -ls -R /retail-lake
  run hdfs dfs -du -h /retail-lake/raw/tpcxbb
  run hdfs dfs -stat "'%n taille=%b octets replication=%r bloc=%o proprietaire=%u:%g droits=%A modifie=%y'" $DST/store_sales.dat
  run 'stat -c "%n taille=%s octets" '$SRC
  run 'hdfs dfs -cat '$DST'/store_sales.dat | head -n 2'
  run 'sha256sum < '$SRC
  run 'hdfs dfs -cat '$DST'/store_sales.dat | sha256sum'
  run 'sha256sum < '$REF
  run 'hdfs dfs -cat '$DSTR'/store_sales.dat | sha256sum'
  run hdfs dfs -get $DST/store_sales.dat /tmp/store_sales_from_hdfs.dat
  run 'cmp '$SRC' /tmp/store_sales_from_hdfs.dat && echo IDENTIQUE'
  run rm /tmp/store_sales_from_hdfs.dat
  run hdfs fsck $DST/store_sales.dat -files -blocks
  ;;
esac
