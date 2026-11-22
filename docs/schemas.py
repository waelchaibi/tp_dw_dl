"""Schémas des livrables (Graphviz). Usage : python3 docs/schemas.py"""
import subprocess
from pathlib import Path

R = Path(__file__).resolve().parent.parent
POLICE = 'fontname="Liberation Sans"'


def rendre(dot, sortie):
    sortie = R / sortie
    sortie.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["dot", "-Tpng", "-Gdpi=170", "-o", str(sortie)], input=dot.encode(), check=True)
    print("écrit", sortie.relative_to(R))


FLUX_NIFI = f"""
digraph G {{
  rankdir=LR; graph [{POLICE}, fontsize=11, pad=0.2, nodesep=0.5, ranksep=0.55];
  node [{POLICE}, fontsize=11, shape=box, style="rounded,filled", fillcolor="#eef3fb", color="#1f4e9a"];
  edge [{POLICE}, fontsize=10, color="#444"];
  src [label="/data/nifi/input\\nincome_band.dat\\n(copie de travail)", shape=folder, fillcolor="#f5f5f5", color="#777"];
  subgraph cluster_pg {{ label="Canvas NiFi 2.12.0 (racine)"; style="rounded,dashed"; color="#999"; fontsize=10;
    get [label="GetFile UC04\\nInput Directory=/data/nifi/input\\nKeep Source File=false"];
    put [label="PutHDFS UC04\\nDirectory=/retail-lake/raw/nifi\\nConflict Resolution=fail"];
    log [label="LogAttribute echec UC04\\nLog Level=warn", fillcolor="#fdeeee", color="#b3261e"];
  }}
  hdfs [label="HDFS\\n/retail-lake/raw/nifi/", shape=cylinder, fillcolor="#e9f6ee", color="#17702d"];
  fin1 [label="auto-terminé", shape=plaintext, style="", fontsize=9, fontcolor="#666"];
  fin2 [label="auto-terminé\\n+ journal nifi-app.log", shape=plaintext, style="", fontsize=9, fontcolor="#666"];
  src -> get [label="lecture"];
  get -> put [label="success", penwidth=1.6];
  put -> hdfs [label="écriture", style=dashed, color="#17702d"];
  put -> fin1 [label="success", style=dotted];
  put -> log [label="failure", color="#b3261e", fontcolor="#b3261e"];
  log -> fin2 [label="success", style=dotted];
}}
"""

DATA_LAKE = f"""
digraph G {{
  rankdir=LR; graph [{POLICE}, fontsize=10, pad=0.15, nodesep=0.12, ranksep=0.35];
  node [{POLICE}, fontsize=10, shape=folder, style=filled, fillcolor="#eef3fb", color="#1f4e9a"];
  edge [color="#777", arrowhead=none];
  root [label="/retail-lake"];
  raw [label="raw"]; bronze [label="bronze"]; silver [label="silver"]; gold [label="gold"]; quality [label="quality"]; logs [label="logs"];
  tp [label="tpcxbb"]; ini [label="initial"]; ref [label="refresh"]; nifi [label="nifi"]; btp [label="tpcxbb"];
  ss1 [label="store_sales/\\nstore_sales.dat (88,5 Mo)", shape=note, fillcolor="#e9f6ee", color="#17702d"];
  ss2 [label="store_sales/\\nstore_sales.dat (900,6 Ko)", shape=note, fillcolor="#e9f6ee", color="#17702d"];
  ib [label="income_band.dat (327 o)\\ndéposé par NiFi (UC-04)", shape=note, fillcolor="#e9f6ee", color="#17702d"];
  root -> {{raw bronze silver gold quality logs}};
  raw -> tp; raw -> nifi; tp -> ini; tp -> ref; ini -> ss1; ref -> ss2; nifi -> ib; bronze -> btp;
}}
"""

AZURE = f"""
digraph G {{
  rankdir=TB; compound=true; newrank=true;
  graph [{POLICE}, fontsize=11, pad=0.2, nodesep=0.3, ranksep=0.42, labeljust=l];
  node [{POLICE}, fontsize=10, shape=box, style="rounded,filled,dashed", fillcolor="#eef3fb", color="#1f4e9a"];
  edge [{POLICE}, fontsize=9, color="#555"];
  tpc [label="Kit TPCx-BB · 23 tables .dat · lots initial + refresh", style="rounded,filled", fillcolor="#f5f5f5", color="#777"];
  comp [label="Données complémentaires\\n(aucune fournie)", fillcolor="#ffffff", color="#999", fontcolor="#777"];
  adf [label="Azure Data Factory\\ncopie, pipelines, déclencheurs"];
  subgraph cluster_adls {{ label="ADLS Gen2 · compte stretailintel · HNS activé · conteneur retail-intelligence"; style="rounded,dashed"; color="#1f4e9a";
    br [label="bronze/\\nfichiers reçus, inchangés"];
    sv [label="silver/\\nParquet nettoyé"];
    gd [label="gold/\\nindicateurs, analyses"];
    ql [label="quality/\\ndocumentation/"];
  }}
  subgraph cluster_syn {{ label="Azure Synapse Analytics (Synapse Studio)"; style="rounded,dashed"; color="#1f4e9a";
    sp [label="Spark Pool (PySpark)\\nnettoyage, jointures, agrégats"];
    sql [label="SQL serverless\\nrequêtes sur gold/"];
  }}
  pbi [label="Power BI · tableaux de bord KPI", fillcolor="#fff6e5", color="#b36b00"];
  sec [label="Sécurité transverse\\nEntra ID · Azure RBAC · ACL par répertoire\\nKey Vault · identités managées", fillcolor="#fdeeee", color="#b3261e"];
  leg [shape=plaintext, style="", label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="3">
    <tr><td bgcolor="#eef3fb">pointillé</td><td>proposé, non déployé</td></tr>
    <tr><td bgcolor="#f5f5f5">plein</td><td>réellement disponible</td></tr></table>>];
  tpc -> adf [label=" copie"]; comp -> adf [style=dotted];
  adf -> br [label=" dépôt daté"];
  br -> sp [label=" lecture"]; sp -> sv [label=" écriture"]; sp -> gd [label=" KPI"];
  gd -> sql; sql -> pbi [label=" import / DirectQuery"];
  sec -> ql [style=dotted, arrowhead=none, color="#b3261e", lhead=cluster_adls];
  {{rank=same; tpc; comp; leg}}
  {{rank=same; br; sv; gd; ql}}
  {{rank=same; adf; sec}}
}}
"""

LOCAL = f"""
digraph G {{
  rankdir=LR; newrank=true; graph [{POLICE}, fontsize=11, pad=0.2, nodesep=0.3, ranksep=0.5, labeljust=l];
  node [{POLICE}, fontsize=10, shape=box, style="rounded,filled", fillcolor="#e9f6ee", color="#17702d"];
  edge [{POLICE}, fontsize=9, color="#555"];
  tpc [label="retail_project/\\n(lecture seule)", fillcolor="#f5f5f5", color="#777"];
  subgraph cluster_lake {{ label="conteneur lake (Docker Compose)"; style=rounded; color="#17702d";
    nifi [label="NiFi 2.12.0\\nGetFile → PutHDFS"];
    hdfs [label="HDFS 3.5.0\\n/retail-lake/raw"];
    spark [label="Spark / PySpark 4.1.4\\nJupyter (notebooks)"];
  }}
  ice [label="Iceberg REST 1.10.1\\ncatalogue"];
  minio [label="MinIO (S3)\\nwarehouse/bronze|silver|gold\\nParquet + métadonnées Iceberg", shape=cylinder];
  trino [label="Trino 484\\nSQL sur iceberg.*"];
  mpl [label="Matplotlib / Pandas\\nvisualisations UC-08", fillcolor="#fff6e5", color="#b36b00"];
  orch [label="Airflow\\n(étudié, non déployé)", style="rounded,dashed", fillcolor="#ffffff", color="#999", fontcolor="#777"];
  tpc -> nifi; nifi -> hdfs; tpc -> spark [label="lecture .dat"]; spark -> ice [label="commit"]; ice -> minio [style=dotted];
  spark -> minio [label="Parquet"]; trino -> ice; trino -> minio [style=dotted]; spark -> mpl; orch -> spark [style=dotted];
}}
"""

if __name__ == "__main__":
    rendre(FLUX_NIFI, "Jour2/UC04_preuves/configuration/schema_flux_nifi.png")
    rendre(DATA_LAKE, "Jour2/UC03_preuves/data_lake/schema_arborescence.png")
    rendre(AZURE, "Jour4/architecture/schema_architecture.png")
    rendre(LOCAL, "Jour4/architecture/schema_parcours_b_local.png")
