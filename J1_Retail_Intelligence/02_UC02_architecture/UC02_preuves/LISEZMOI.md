# UC02_preuves

| Preuve | Titre | Ce qu'elle démontre |
| --- | --- | --- |
| `01_schema_architecture_flux.png` | Schéma d'architecture et des flux | Trajet des données : sources, ingestion, zones Bronze / Silver / Gold, usages, gouvernance |
| `02_tableaux_UC02.xlsx` | Tableaux de UC-02 | Comparaison des architectures, zones, composants, flux, gouvernance, correspondance local / Azure |
| `03_formats_volumes.txt` | Formats et volumes du kit | Mesures à l'origine des contraintes : 978 Mo, 24 fichiers, séparateur `\|`, plus grosses tables |
| `04_controles_qualite.txt` | Contrôles qualité | Champs vides, doublons, cohérence des clés, données personnelles dans `customer` |

Aucun composant (Hadoop, NiFi, Spark, Azure) n'est déployé au Jour 1 : les preuves 01 et 02 sont des éléments de conception, les preuves 03 et 04 sont des commandes réellement exécutées sur le kit.
