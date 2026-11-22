# Jour 4 – UC-08 (analyses) et UC-07 (architecture Azure)

## Contenu

| Élément | Emplacement |
|---|---|
| Dossier UC-08 | `UC08_analyses_visualisations.pdf` |
| Dossier UC-07 | `UC07_architecture_azure.pdf` |
| Chargement Bronze / Silver / Gold Iceberg | `../notebooks/TP4_00_chargement_lakehouse.ipynb` |
| KPI, statistiques, analyses, visualisations | `../notebooks/TP4_Retail_Intelligence.ipynb` |
| Résultats UC-08 (CSV) | `preuves/uc08/` |
| Visualisations | `visualisations/visualisation_{1,2,3}_*.png` |
| Schémas | `architecture/schema_architecture.png` (Azure proposé), `architecture/schema_parcours_b_local.png` (déployé) |
| Organisation ADLS Gen2 | `architecture/organisation_adls.md` |
| Matrice des permissions | `architecture/matrice_permissions.pdf` |
| Preuves parcours B | `preuves/uc07/parcours_b_local.txt` (script `uc07.sh`) |
| Simulation Azure | `preuves/uc07/simulation_azure.md` (non exécutée) |

## Parcours

Parcours B (local / open source) : MinIO + Iceberg REST + Spark + Trino, réellement déployés par `docker compose`.
Azure (ADLS Gen2, Data Factory, Synapse, Entra ID, Key Vault, Power BI) : étudié et simulé, **rien n'a été créé sur Azure**.

## Versions

| Composant | Version |
|---|---|
| Python | 3.12 (`/opt/venv`, uv) |
| Spark / PySpark | 4.1.4, `local[*]` |
| Iceberg | runtime 1.12.0, catalogue REST 1.10.1 |
| MinIO | RELEASE.2026-08-04 |
| Trino | 484 |
| Pandas / Matplotlib | 2.3.3 / 3.11.2 |

## Reproduction

```bash
docker compose up -d
docker compose exec lake jupyter nbconvert --to notebook --execute --inplace /home/etudiant/notebooks/TP4_00_chargement_lakehouse.ipynb
docker compose exec lake jupyter nbconvert --to notebook --execute --inplace /home/etudiant/notebooks/TP4_Retail_Intelligence.ipynb
bash Jour4/preuves/uc07/uc07.sh > Jour4/preuves/uc07/parcours_b_local.txt
uv run --no-project --with pikepdf python Jour4/build_docs.py
```

Jupyter : `http://localhost:8888/?token=tp`. Trino : `docker compose exec trino trino`.

## Limites

- Données TPCx-BB synthétiques : les résultats valident la méthode, pas une décision.
- Lot initial seulement ; décembre 2005 partiel.
- Identifiants MinIO par défaut, valables uniquement en local (ports publiés sur 127.0.0.1).
