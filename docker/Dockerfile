# TP Jour 2 – Hadoop 3.5.0 (Java 17) + NiFi 2.12.0 (Java 21), mono-nœud, mêmes chemins que le TP.
FROM ubuntu:24.04

ARG HADOOP_VERSION=3.5.0
ARG NIFI_VERSION=2.12.0

RUN apt-get update && apt-get install -y --no-install-recommends \
      openjdk-17-jdk-headless openjdk-21-jdk-headless \
      wget curl unzip ca-certificates procps net-tools python3 less nano file \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash etudiant

ENV JAVA_HOME_HADOOP=/usr/lib/jvm/java-17-openjdk-amd64 \
    JAVA_HOME_NIFI=/usr/lib/jvm/java-21-openjdk-amd64 \
    HADOOP_HOME=/opt/hadoop \
    HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop \
    PATH=$PATH:/opt/hadoop/bin:/opt/hadoop/sbin

RUN wget -q https://downloads.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz -O /tmp/hadoop.tgz \
    && tar -xzf /tmp/hadoop.tgz -C /opt && mv /opt/hadoop-${HADOOP_VERSION} /opt/hadoop && rm /tmp/hadoop.tgz \
    && rm -rf /opt/hadoop/share/doc \
    && chown -R etudiant:etudiant /opt/hadoop \
    && echo "export JAVA_HOME=$JAVA_HOME_HADOOP" >> /opt/hadoop/etc/hadoop/hadoop-env.sh

RUN wget -q https://downloads.apache.org/nifi/${NIFI_VERSION}/nifi-${NIFI_VERSION}-bin.zip -O /tmp/nifi.zip \
    && unzip -q /tmp/nifi.zip -d /opt && mv /opt/nifi-${NIFI_VERSION} /opt/nifi && rm /tmp/nifi.zip \
    && for n in nifi-hadoop-nar nifi-hadoop-libraries-nar; do \
         ls /opt/nifi/lib | grep -q "^$n-" || wget -q -P /opt/nifi/lib \
           https://repo1.maven.org/maven2/org/apache/nifi/$n/${NIFI_VERSION}/$n-${NIFI_VERSION}.nar; \
       done \
    && sed -i -e 's|^nifi.web.https.host=.*|nifi.web.https.host=0.0.0.0|' \
              -e 's|^nifi.web.proxy.host=.*|nifi.web.proxy.host=localhost:8443|' /opt/nifi/conf/nifi.properties \
    && chown -R etudiant:etudiant /opt/nifi

COPY --chown=etudiant:etudiant core-site.xml hdfs-site.xml /opt/hadoop/etc/hadoop/
COPY --chmod=755 entrypoint.sh /entrypoint.sh

RUN mkdir -p /home/etudiant/hadoop-data/namenode /home/etudiant/hadoop-data/datanode \
             /data/nifi/input /data/nifi/archive /data/nifi/error \
    && chown -R etudiant:etudiant /home/etudiant /data/nifi

USER etudiant
WORKDIR /home/etudiant
EXPOSE 9870 8443
ENTRYPOINT ["/entrypoint.sh"]
