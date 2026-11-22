# Organisation ADLS Gen2 proposée

Statut : **proposition, non déployée** (aucun abonnement Azure utilisé). Équivalent réellement déployé en local : bucket MinIO `warehouse/` (voir `../preuves/uc07/parcours_b_local.txt`).

| Ressource | Nom proposé |
|---|---|
| Groupe de ressources | `rg-retail-intel-dev` (France Central) |
| Compte de stockage | `stretailinteldev`, StorageV2, LRS, **HNS activé** |
| Conteneur (file system) | `retail-intelligence` |

```
retail-intelligence/
├── bronze/
│   └── tpcxbb/<table>/lot=<initial|refresh>/ingest_date=AAAA-MM-JJ/<table>.dat
├── silver/
│   ├── ventes/store_sales/        (Parquet / Iceberg)
│   ├── retours/store_returns/
│   ├── produits/item/
│   ├── magasins/store/
│   └── calendrier/date_dim/
├── gold/
│   ├── indicateurs/kpi/           kpi.csv, statistiques
│   └── analyses/                  ventes_magasin_mensuelles, ventes_magasin_par_produit, retours_magasin_mensuels
├── quality/AAAA-MM-JJ/            rapports de contrôle, lignes rejetées
└── documentation/                 dictionnaire KPI, schémas, README
```

| Zone | Fonction | Données | Utilisateurs / traitements | Nommage | Conservation et traçabilité |
|---|---|---|---|---|---|
| bronze | Copie exacte des fichiers reçus | 23 tables `.dat`, lots initial et refresh | Pipeline ADF (écriture), Data Engineering (lecture) | `tpcxbb/<table>/lot=…/ingest_date=…/` | Immuable, conservé 1 an, empreinte sha256 par fichier |
| silver | Données typées, nettoyées, contrôlées | ventes, retours, produits, magasins, calendrier | Spark Pool (écriture), Data Engineering | `<domaine>/<table>/`, colonnes `_lot`, `_source_fichier` | Réécrit à chaque traitement, historique par snapshot de table |
| gold | Agrégats et KPI pour l'analyse | KPI, analyses UC-08 | Spark Pool (écriture), analystes et Power BI (lecture) | `indicateurs/<kpi>/`, `analyses/<sujet>/` | Versionné par date de calcul, règles dans `documentation/` |
| quality | Résultats des contrôles | rapports CSV, lignes écartées | Traitements (écriture), Data Steward (lecture) | `AAAA-MM-JJ/rapport_<uc>.csv` | 90 jours |
| documentation | Référentiel | dictionnaire KPI, schémas | Tous (lecture) | libre | Versionné dans Git |

Données personnelles (`customer`, `customer_address`) : restent en bronze, non copiées en silver/gold ; aucun accès analyste.
