# J1 — Retail Intelligence Platform

Socle obligatoire du Jour 1 : UC-01 (besoin et exploration) et UC-02 (architecture).

Les dossiers complémentaire, avancé et contribution individuelle sont absents. L'énoncé permet de ne pas les remettre lorsque ces activités ne sont pas faites.

## Source

Les fichiers mesurés restent dans `retail_project/`. Ils ne sont pas déplacés : le Jour 1 ne demande pas de les charger dans HDFS.

- Lot initial : `retail_project/data` — 976,99 Mo hors doublons
- Delta : `retail_project/data_refresh` — 8,96 Mo
- Version du kit, date et outil de génération : non communiqué

## Livrables

```
01_UC01_besoin_exploration/
  cadrage_metier.pdf
  questions_decisionnelles.pdf
  dictionnaire_KPI.xlsx
  inventaire_sources.xlsx
  qualification_donnees.pdf
  limites_hypotheses.pdf
  preuves/
02_UC02_architecture/
  UC02_architecture.pdf
  UC02_preuves/
```

## Régénérer les mesures et les documents

Depuis `J1_Retail_Intelligence/scripts` :

```
python -m pip install -r requirements.txt
python inventaire.py
python generer_livrables.py
```

Les mesures ont été exécutées en Python sur le poste qui contient le kit. L'environnement de référence du parcours est Linux / Ubuntu. HDFS, NiFi, Spark et Azure sont conçus dans UC-02 et ne sont pas déployés.

## Statuts utilisés

Vérifié, Déduit, Hypothèse, Non disponible, À valider. Un nom de colonne déduit n'est posé que si la largeur du fichier égale celle du schéma de référence.
