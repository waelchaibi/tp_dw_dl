# Jour 3 – UC-06 : traitements PySpark

## Contenu

| Élément | Emplacement |
|---|---|
| Dossier technique | `UC06_traitements_PySpark.pdf` |
| Notebook d'exploration | `../notebooks/uc06_exploration.ipynb` (n'écrit rien) |
| Nettoyage, transformations, Silver, Gold, Parquet, qualité | `../notebooks/uc06_silver_gold.ipynb` |
| Gold produit (copie) | `data/gold/ventes_magasin_par_produit/` (Parquet) |
| Preuves extraites des notebooks | `preuves/{environnement,exploration,transformations,silver_gold,parquet,qualite}/` |
| Rejeu de contrôle du 22/11 | `preuves/rejeu_2026-11-22.txt` |
| Génération du PDF et des preuves | `build_docs.py` |

Les notebooks restent dans `notebooks/` : c'est le dossier racine de Jupyter dans le conteneur.

## Prérequis

- Docker, kit `retail_project/` dézippé à la racine du dépôt (ignoré par Git).
- `docker compose up -d` : HDFS (`hdfs://localhost:9000`) et Jupyter (`http://localhost:8888/?token=tp`).

## Versions observées

| | Exécution d'origine | Rejeu 22/11 |
|---|---|---|
| Python | 3.12.3 | 3.12.14 |
| Spark | 4.3.0 | 4.1.4 |
| Mode | `local[*]` | `local[*]` |

## Ordre d'exécution

1. `uc06_exploration.ipynb` : schémas, échantillons, vides, doublons, bornes.
2. `uc06_silver_gold.ipynb` : règles, jointure, Gold, écriture Parquet, relecture, contrôles.

En ligne de commande :

```bash
docker compose exec lake jupyter nbconvert --to notebook --execute --inplace /home/etudiant/notebooks/uc06_silver_gold.ipynb
```

## Entrées et sorties

| | Chemin |
|---|---|
| Entrées (lecture seule) | `/data/retail_project/data/store_sales/store_sales.dat`, `/data/retail_project/data/item/item.dat` |
| Silver | `hdfs:///retail-lake/silver/uc06/{store_sales,item}` |
| Gold | `hdfs:///retail-lake/gold/uc06/ventes_magasin_par_produit` |

`mode("overwrite")` ne vise que ces répertoires de sortie.

## Contrôles disponibles

9 contrôles (volume, complétude, unicité, validité, intégrité, cohérence) : 9 OK, 0 ligne écartée.

## Limites connues

- Lot initial seulement ; le lot refresh reste en Raw.
- Noms de colonnes déduits de la spécification TPCx-BB.
- Silver (63 Mo) non versionné : il est régénéré par le notebook.
- Parquet n'est pas une table transactionnelle (Iceberg au Jour 4).

## Régénérer le PDF

```bash
uv run --no-project --with pikepdf python Jour3/build_docs.py
```
