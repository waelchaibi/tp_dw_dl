#!/bin/bash
# UC-07 – preuves du parcours B (local / open source), lancé depuis la racine du dépôt :
#   bash Jour4/preuves/uc07/uc07.sh > Jour4/preuves/uc07/parcours_b_local.txt
# Lecture seule : aucune table n'est modifiée. Aucun secret n'est affiché.
run() { echo; echo "\$ $*"; eval "$@" 2>&1; }
trino() { docker compose exec -T trino trino --output-format ALIGNED --execute "$1" 2>/dev/null; }
mc() { docker compose run --rm -T --entrypoint sh minio-init -c \
  "mc alias set local http://minio:9000 \$MINIO_ROOT_USER \$MINIO_ROOT_PASSWORD >/dev/null && $1" 2>/dev/null; }

echo "# UC-07 parcours B – $(date '+%Y-%m-%d %H:%M:%S %Z') – hôte $(hostname)"
run "docker compose ps --format '{{.Service}} {{.Image}} {{.Status}}'"
run "trino 'SELECT node_version FROM system.runtime.nodes'"
run "trino 'SHOW SCHEMAS FROM iceberg'"
run "trino 'SHOW TABLES FROM iceberg.gold'"
run "trino 'SELECT count(*) AS lignes, sum(nb_lignes) AS lignes_vente, sum(ca_net) AS ca_net FROM iceberg.gold.ventes_magasin_mensuelles'"
run "trino 'SELECT snapshot_id, operation, committed_at FROM iceberg.gold.\"ventes_magasin_mensuelles\$snapshots\" ORDER BY committed_at'"
run "trino 'SELECT file_format, count(*) AS fichiers, sum(file_size_in_bytes) AS octets FROM iceberg.gold.\"ventes_magasin_mensuelles\$files\" GROUP BY file_format'"
run "mc 'mc ls local/'"
run "mc 'mc ls local/warehouse/'"
run "mc 'mc du --depth 2 local/warehouse/'"
run "mc 'mc ls --recursive local/warehouse/gold/ | head -n 12'"
