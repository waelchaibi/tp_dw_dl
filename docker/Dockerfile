# TP – Hadoop 3.5.0 (Java 17) + NiFi 2.12.0 (Java 21) + Spark/PySpark (Java 17) + Jupyter, mono-nœud.
FROM ubuntu:24.04

ARG HADOOP_VERSION=3.5.0
ARG NIFI_VERSION=2.12.0

RUN apt-get update && apt-get install -y --no-install-recommends \
      openjdk-17-jdk-headless openjdk-21-jdk-headless \
      wget curl unzip ca-certificates procps net-tools python3 less nano file \
    && rm -rf /var/lib/apt/lists/* \
    && userdel -r ubuntu && useradd -m -u 1000 -s /bin/bash etudiant

ENV JAVA_HOME_HADOOP=/usr/lib/jvm/java-17-openjdk-amd64 \
    JAVA_HOME_NIFI=/usr/lib/jvm/java-21-openjdk-amd64 \
    HADOOP_HOME=/opt/hadoop \
    HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop \
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
    VIRTUAL_ENV=/opt/venv \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON=/usr/bin/python3.12 \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    PYSPARK_PYTHON=/opt/venv/bin/python \
    PATH=/opt/venv/bin:$PATH:/opt/hadoop/bin:/opt/hadoop/sbin

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

COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /uvx /usr/local/bin/
COPY pyproject.toml uv.lock /opt/tp/
RUN cd /opt/tp && uv sync --frozen --no-cache \
    && ln -s "$(/opt/venv/bin/python -c 'import pyspark, os; print(os.path.dirname(pyspark.__file__))')" /opt/spark \
    && chown -R etudiant:etudiant /opt/venv /opt/tp
ENV SPARK_HOME=/opt/spark \
    PATH=$PATH:/opt/spark/bin

COPY --chown=etudiant:etudiant docker/core-site.xml docker/hdfs-site.xml /opt/hadoop/etc/hadoop/
COPY --chmod=755 docker/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh

RUN mkdir -p /home/etudiant/hadoop-data/namenode /home/etudiant/hadoop-data/datanode \
             /data/nifi/input /data/nifi/archive /data/nifi/error \
             /home/etudiant/notebooks \
    && chown -R etudiant:etudiant /home/etudiant /data/nifi

USER etudiant
WORKDIR /home/etudiant
EXPOSE 9870 8443 8888 4040
ENTRYPOINT ["/entrypoint.sh"]
