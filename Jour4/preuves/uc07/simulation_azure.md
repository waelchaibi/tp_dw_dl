# Dossier de simulation Azure (UC-07)

**Aucune de ces commandes n'a été exécutée** : pas d'abonnement Azure autorisé pour le TP (parcours B). Elles décrivent ce qui serait fait, dans l'ordre, avec Azure CLI.

## 1. Ressources qui seraient créées

| Ressource | Nom | Paramètres |
|---|---|---|
| Groupe de ressources | `rg-retail-intel-dev` | France Central |
| Compte de stockage | `stretailinteldev` | StorageV2, Standard LRS, HNS activé, TLS 1.2, accès public blob désactivé |
| Conteneur | `retail-intelligence` | privé |
| Groupes Entra ID | `grp-data-eng`, `grp-analystes`, `grp-data-steward` | membres nominatifs |
| Data Factory | `adf-retail-intel-dev` | identité managée système |
| Synapse | `syn-retail-intel-dev` | Spark Pool petit, SQL serverless |
| Key Vault | `kv-retail-intel-dev` | secrets des sources externes |

## 2. Opérations envisagées

```bash
az group create -n rg-retail-intel-dev -l francecentral
az storage account create -n stretailinteldev -g rg-retail-intel-dev -l francecentral \
  --kind StorageV2 --sku Standard_LRS --hns true --min-tls-version TLS1_2 --allow-blob-public-access false
az storage fs create -n retail-intelligence --account-name stretailinteldev --auth-mode login
for d in bronze/tpcxbb silver gold/indicateurs gold/analyses quality documentation; do
  az storage fs directory create -n $d -f retail-intelligence --account-name stretailinteldev --auth-mode login
done
# Dépôt d'un fichier de démonstration autorisé (résultat du projet, sans donnée personnelle)
az storage fs file upload -s Jour4/preuves/uc08/kpi.csv -p gold/indicateurs/kpi/kpi.csv \
  -f retail-intelligence --account-name stretailinteldev --auth-mode login
# Moindre privilège : lecture seule de gold pour les analystes, par ACL
az storage fs access set -p gold -f retail-intelligence --account-name stretailinteldev --auth-mode login \
  --acl "user::rwx,group::r-x,other::---,group:<objectId grp-analystes>:r-x"
# Plan de gestion : lecture des ressources, sans accès aux données
az role assignment create --assignee <objectId grp-analystes> --role Reader \
  --scope /subscriptions/<id>/resourceGroups/rg-retail-intel-dev
```

## 3. Contrôles qui seraient réalisés

| Contrôle | Commande | Attendu |
|---|---|---|
| HNS actif | `az storage account show -n stretailinteldev --query isHnsEnabled` | `true` |
| Arborescence | `az storage fs file list -f retail-intelligence --account-name stretailinteldev --auth-mode login` | 6 répertoires |
| Fichier accessible | `az storage fs file show -p gold/indicateurs/kpi/kpi.csv …` | taille = fichier local |
| ACL | `az storage fs access show -p gold …` | `group:<analystes>:r-x` |
| Pas d'accès public | `az storage account show … --query allowBlobPublicAccess` | `false` |
| Coût | budget de 5 € avec alerte | aucune alerte |

## 4. Réalisé / proposé

| Élément | Statut |
|---|---|
| Ressources Azure ci-dessus | Proposé (simulation) |
| Organisation bronze / silver / gold | Réalisé en local (MinIO + Iceberg), proposé sur ADLS |
| Fichier de démonstration | `kpi.csv` réellement produit (UC-08), non déposé sur Azure |
| Fin d'exercice | `az group delete -n rg-retail-intel-dev` pour arrêter tout coût |
