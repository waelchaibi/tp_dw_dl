ARG HADOOP_VERSION=3.5.0
ARG NIFI_VERSION=2.12.0

FROM alpine:3 AS hadoop
ARG HADOOP_VERSION
RUN apk add --no-cache tar \
    && wget -qO- https://downloads.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
       | tar -xz -C /opt \
    && mv /opt/hadoop-${HADOOP_VERSION} /opt/hadoop \
    # seul HDFS sert : doc, outils (SDK AWS…), YARN, MapReduce, client shadé et libs statiques retirés (~1 Go)
    && rm -rf /opt/hadoop/share/doc /opt/hadoop/share/hadoop/tools /opt/hadoop/share/hadoop/yarn \
              /opt/hadoop/share/hadoop/mapreduce /opt/hadoop/share/hadoop/client \
    && find /opt/hadoop/lib/native -name "*.a" -delete \
    && echo "export JAVA_HOME=/opt/java/17" >> /opt/hadoop/etc/hadoop/hadoop-env.sh

FROM alpine:3 AS nifi
ARG NIFI_VERSION
RUN apk add --no-cache unzip \
    && wget -q https://downloads.apache.org/nifi/${NIFI_VERSION}/nifi-${NIFI_VERSION}-bin.zip -O /tmp/nifi.zip \
    && unzip -q /tmp/nifi.zip -d /opt && mv /opt/nifi-${NIFI_VERSION} /opt/nifi && rm /tmp/nifi.zip \
    && for n in nifi-hadoop-nar nifi-hadoop-libraries-nar; do \
         ls /opt/nifi/lib | grep -q "^$n-" || wget -q -P /opt/nifi/lib \
           https://repo1.maven.org/maven2/org/apache/nifi/$n/${NIFI_VERSION}/$n-${NIFI_VERSION}.nar; \
       done \
    && sed -i -e 's|^nifi.web.https.host=.*|nifi.web.https.host=0.0.0.0|' \
              -e 's|^nifi.web.proxy.host=.*|nifi.web.proxy.host=localhost:8443|' /opt/nifi/conf/nifi.properties

FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      procps curl file less nano hostname \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 -s /bin/bash etudiant \
    && mkdir -p /opt/venv /opt/tp \
                /home/etudiant/hadoop-data/namenode /home/etudiant/hadoop-data/datanode \
                /home/etudiant/notebooks /home/etudiant/.cache/uv \
                /data/nifi/input /data/nifi/archive /data/nifi/error \
    && chown -R 1000:1000 /opt/venv /opt/tp /home/etudiant /data/nifi

COPY --from=eclipse-temurin:17-jdk /opt/java/openjdk /opt/java/17
COPY --from=eclipse-temurin:21-jre /opt/java/openjdk /opt/java/21
COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /uvx /usr/local/bin/
COPY --from=hadoop --chown=1000:1000 /opt/hadoop /opt/hadoop
COPY --from=nifi   --chown=1000:1000 /opt/nifi   /opt/nifi

ENV JAVA_HOME=/opt/java/17 \
    JAVA_HOME_HADOOP=/opt/java/17 \
    JAVA_HOME_NIFI=/opt/java/21 \
    HADOOP_HOME=/opt/hadoop \
    HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop \
    HADOOP_YARN_HOME=/opt/hadoop \
    HADOOP_MAPRED_HOME=/opt/hadoop \
    SPARK_HOME=/opt/venv/lib/python3.12/site-packages/pyspark \
    VIRTUAL_ENV=/opt/venv \
    PYSPARK_PYTHON=/opt/venv/bin/python \
    UV_PROJECT=/opt/tp \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_CACHE_DIR=/home/etudiant/.cache/uv \
    UV_PYTHON=/usr/local/bin/python3.12 \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    PATH=/opt/venv/bin:/opt/java/17/bin:/opt/hadoop/bin:/opt/hadoop/sbin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV PATH=$PATH:$SPARK_HOME/bin

USER etudiant
WORKDIR /home/etudiant

COPY --chown=1000:1000 pyproject.toml uv.lock /opt/tp/
RUN --mount=type=cache,target=/tmp/uv-cache,uid=1000,gid=1000 \
    UV_CACHE_DIR=/tmp/uv-cache uv sync --frozen

COPY --chown=1000:1000 docker/core-site.xml docker/hdfs-site.xml /opt/hadoop/etc/hadoop/
COPY --chmod=755 --chown=1000:1000 docker/entrypoint.sh /entrypoint.sh
RUN sed 's/\r$//' /entrypoint.sh > /tmp/e && cat /tmp/e > /entrypoint.sh && rm /tmp/e

EXPOSE 9870 8443 8888 4040
ENTRYPOINT ["/entrypoint.sh"]
