"""PDF du Jour 4 : UC08_analyses_visualisations.pdf, UC07_architecture_azure.pdf, architecture/matrice_permissions.pdf.

Prérequis : notebooks/TP4_Retail_Intelligence.ipynb exécuté (CSV dans Jour4/preuves/uc08).
uv run --no-project --with pikepdf python Jour4/build_docs.py
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "docs"))
from pdfgen import RACINE, build, encadre, fichier, img, le, na, note, ok, p, pre, sec, sous, t  # noqa: E402

DATE = le(19)
UC08 = RACINE / "Jour4/preuves/uc08"


def lire(nom):
    with open(UC08 / nom, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def nb(x, dec=0):
    v = float(x)
    s = f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")
    return s


def m(x):
    return nb(float(x) / 1e6, 2) + " M"


kpi = lire("kpi.csv")
stats = lire("statistiques.csv")
annee = lire("repartition_par_annee.csv")
cat = lire("analyse2_ca_par_categorie.csv")
mag = lire("co01_comparaison_magasins.csv")

# --------------------------------------------------------------------------- UC-08
uc08 = [
    sec("Partie 1 – Sélection des données et vérification des KPI",
        sous("Jeux de données",
             t(["Jeu", "Zone", "Granularité", "Lignes", "Contrôles disponibles"], [
                 ["iceberg.silver.store_sales", "Silver", "un article d'un ticket", "667 579", "clés non nulles, quantité &gt; 0, 0 doublon, 0 orphelin"],
                 ["iceberg.silver.store_returns", "Silver", "un article retourné", "37 902", "clés non nulles, quantité &gt; 0"],
                 ["iceberg.silver.item / store / date_dim", "Silver", "article / magasin / jour", "17 820 / 12 / 109 573", "clé unique"],
                 ["iceberg.gold.ventes_magasin_mensuelles", "Gold", "magasin × mois", "720", "Σ lignes et Σ CA = Silver"],
                 ["iceberg.gold.ventes_magasin_par_produit", "Gold", "article", "17 820", "Σ lignes et Σ CA = Silver"],
                 ["iceberg.gold.retours_magasin_mensuels", "Gold", "magasin × mois de retour", "948", "—"],
             ], [31, 9, 20, 13, 27], cls="s"),
             p("Provenance : kit TPCx-BB, lot initial → Bronze → Silver (règles du Jour 3) → Gold, tables Apache Iceberg "
               "(fichiers Parquet) sur MinIO. Choix : seules données avec date, magasin et catégorie vérifiés par jointure.")),
        sous("Dictionnaire des KPI",
             t(["KPI", "Formule", "Champs / filtre", "Granularité", "Unité", "Limite"], [
                 ["CA net magasin", "SUM(ss_net_paid)", "store_sales, lot initial", "total, mois, magasin, catégorie", "monnaie du fichier", "hors taxes, hors web"],
                 ["Quantités vendues", "SUM(ss_quantity)", "ss_quantity &gt; 0", "idem", "unités", "≠ lignes, ≠ tickets"],
                 ["Nombre de tickets", "COUNT(DISTINCT ss_ticket_number)", "lot initial", "total, mois, magasin", "tickets", "1 ticket = 1 magasin (vérifié)"],
                 ["Panier moyen", "CA net / tickets", "—", "total, magasin, mois", "monnaie / ticket", "jamais par ligne"],
                 ["Retours", "SUM(sr_return_quantity), SUM(sr_return_amt)", "date de retour ≤ fin des ventes", "mois, magasin", "unités, monnaie", "date de retour ≠ date de vente"],
                 ["Taux de retour", "quantité retournée / quantité vendue", "même période", "période, magasin", "%", "approché"],
             ], [14, 22, 19, 17, 12, 16], cls="s"),
             p("Non retenus : marge (profit négatif sur 74 % des lignes, coûts non qualifiés), part du canal web (web_sales hors Silver)."))),
    sec("Partie 2 – KPI et statistiques descriptives",
        sous("KPI calculés",
             t(["KPI", "Valeur", "Unité", "Périmètre"],
               [[r["kpi"], nb(r["valeur"], 2 if "." in r["valeur"] else 0), r["unite"], r["perimetre"]] for r in kpi],
               [30, 20, 22, 28], num=(1,))),
        sous("Statistiques descriptives",
             t(["Niveau", "Mesure", "n", "Min", "Max", "Moyenne", "Médiane", "Somme"],
               [[r["niveau"], f"<code>{r['mesure']}</code>", nb(r["n"]), nb(r["min"], 2), nb(r["max"], 2), nb(r["moyenne"], 2),
                 nb(r["mediane"], 2), nb(r["somme"], 0)] for r in stats],
               [13, 16, 9, 10, 12, 12, 12, 16], cls="s", num=(2, 3, 4, 5, 6, 7)),
             note("Médiane &lt; moyenne pour les montants : distribution étirée vers les gros tickets. "
                  "Le minimum magasin × mois (0,50 M) vient de décembre 2005, mois partiel.")),
        sous("Répartition par année",
             t(["Année", "Mois", "CA net", "Tickets", "Quantité", "CA moyen / mois"],
               [[r["annee"], r["mois"], m(r["ca_net"]), nb(r["tickets"]), nb(r["quantite"]), m(r["ca_net_moyen_mensuel"])] for r in annee],
               [12, 10, 20, 16, 20, 22], num=(1, 2, 3, 4, 5)))),
    sec("Partie 3 – Analyses métier et visualisations",
        sous("Analyse 1 – Évolution du CA net dans le temps (Direction générale)",
             t(["Élément", "Contenu"], [
                 ["Données", "Gold ventes_magasin_mensuelles, somme des 12 magasins"],
                 ["Méthode", "CA par mois ; indice saisonnier = CA moyen du mois calendaire / moyenne (2001-2004)"],
                 ["Résultat", "19,36 M par mois, écart type 0,61 M (CV 3,2 %) ; max 2003-10 (20,63 M), min 2002-02 (17,59 M)"],
                 ["Interprétation", "L'indice suit le nombre de jours (février 93, mois de 31 jours ≈ 102) : CA journalier constant"],
                 ["Limite", "Décembre 2005 : 13 jours seulement ; données synthétiques"],
             ], [18, 82]),
             img("Jour4/visualisations/visualisation_1_ca_mensuel.png",
                 "Visualisation 1 – CA net mensuel. La chute finale est un mois partiel, pas une baisse d'activité.", 96)),
        sous("Analyse 2 – Catégories qui portent le CA (Direction commerciale)",
             t(["Catégorie", "Articles", "Part articles", "CA net", "Part CA"],
               [[r["i_category"], nb(r["articles"]), nb(r["part_articles_pct"], 1) + " %", m(r["ca_net"]), nb(r["part_ca_pct"], 1) + " %"] for r in cat],
               [32, 14, 16, 22, 16], cls="s", num=(1, 2, 3, 4)),
             p("Music et Books : 71,9 % du CA pour 75,6 % des articles. La part du CA suit la taille de l'assortiment. "
               "Les 4 articles 10000 à 10003 font 5,0 % du CA, chacun 367 à 441 fois le CA médian d'un article : artefact probable du générateur."),
             img("Jour4/visualisations/visualisation_2_ca_categorie.png", "Visualisation 2 – CA net par catégorie et part du total.", 80)),
        sous("Analyse complémentaire CO-01 – Comparaison des magasins",
             t(["Magasin", "État", "CA net", "Part", "Tickets", "Panier", "Taux retour"],
               [[r["s_store_name"], r["s_state"], m(r["ca_net"]), nb(r["part_ca_pct"], 2) + " %", nb(r["tickets"]),
                 nb(r["panier_moyen"], 0), nb(r["taux_retour_pct"], 2) + " %"] for r in mag],
               [20, 8, 18, 12, 13, 13, 16], cls="s", num=(2, 3, 4, 5, 6)),
             img("Jour4/visualisations/visualisation_3_magasins.png", "Visualisation 3 – CA net et panier moyen par magasin.", 96))),
    sec("Constats, limites et recommandations",
        t(["Constat", "Résultat observé", "Interprétation", "Limite", "Recommandation"], [
            ["1. Activité stable", "CA mensuel 19,36 M ± 3,2 %", "Rythme journalier constant, pas de saisonnalité", "Synthétique ; déc. 2005 partiel ; pas d'objectif",
             "Suivre le CA par jour ; exclure les mois partiels ; intégrer le lot refresh"],
            ["2. CA ∝ assortiment", "Music + Books = 71,9 % du CA, 75,6 % des articles", "La taille du catalogue explique la répartition",
             "Association, pas causalité ; marge non calculable", "Comparer le CA par article ; vérifier les articles 10000-10003"],
            ["3. Magasins homogènes", "94,0 à 99,0 M (écart 5,2 %), retours 2,16-2,51 %", "Aucun magasin ne décroche",
             "Ni surface ni effectif", "Ajouter surface et objectifs avant de classer"],
        ], [15, 22, 21, 20, 22], cls="s"),
        encadre("Données TPCx-BB synthétiques : les résultats valident la démarche, pas une décision réelle. "
                "Le CA (1 150 529 586,37) est identique aux contrôles des Jours 1 et 3.")),
    sec("Reproduction et preuves",
        pre("""
docker compose up -d
# 1. Bronze / Silver / Gold Iceberg
docker compose exec lake jupyter nbconvert --to notebook --execute --inplace /home/etudiant/notebooks/TP4_00_chargement_lakehouse.ipynb
# 2. KPI, statistiques, analyses, visualisations
docker compose exec lake jupyter nbconvert --to notebook --execute --inplace /home/etudiant/notebooks/TP4_Retail_Intelligence.ipynb
"""),
        t(["Fichier", "Contenu"], [
            ["notebooks/TP4_Retail_Intelligence.ipynb", "Notebook exécuté : schémas, contrôles, KPI, analyses, graphiques, questions de recul"],
            ["preuves/uc08/kpi.csv", "KPI calculés"],
            ["preuves/uc08/statistiques.csv, repartition_par_*.csv", "Statistiques descriptives"],
            ["preuves/uc08/analyse1_*.csv, analyse2_*.csv, co01_*.csv", "Résultats des analyses"],
            ["visualisations/visualisation_{1,2,3}_*.png", "Graphiques"],
        ], [44, 56], cls="s")),
]

# --------------------------------------------------------------------------- UC-07
uc07 = [
    sec("1. Parcours retenu",
        p("<b>Parcours B – local / open source</b> : pas d'abonnement Azure autorisé. L'architecture Azure est étudiée et "
          "simulée ; l'équivalent local est réellement déployé et utilisé par UC-08."),
        t(["Composant", "Statut", "Preuve"], [
            ["HDFS 3.5.0, NiFi 2.12.0", ok("Déployé"), "Jour 2"],
            ["Spark / PySpark 4.1.4, Jupyter", ok("Déployé"), "Jours 3 et 4"],
            ["MinIO (S3), Iceberg REST 1.10.1, Trino 484", ok("Déployé"), "preuves/uc07/parcours_b_local.txt"],
            ["Airflow, Nessie / Hive Metastore", na("Étudié"), "—"],
            ["ADLS Gen2, ADF, Synapse, Entra ID, Key Vault, Power BI", na("Proposé (simulation)"), "preuves/uc07/simulation_azure.md"],
        ], [44, 22, 34])),
    sec("2. Composants Azure",
        t(["Composant", "Rôle", "Dans le projet (proposé)"], [
            ["Abonnement", "Facturation et limite de quotas", "Abonnement pédagogique"],
            ["Groupe de ressources", "Regroupe et supprime les ressources ensemble", "<code>rg-retail-intel-dev</code>"],
            ["Compte de stockage", "Point d'accès au stockage, réplication, réseau", "<code>stretailinteldev</code>, StorageV2, LRS"],
            ["Conteneur", "Racine d'un système de fichiers", "<code>retail-intelligence</code>"],
            ["ADLS Gen2", "Compte de stockage + HNS : Data Lake compatible Hadoop (<code>abfss://</code>)", "Zones bronze, silver, gold"],
            ["Microsoft Entra ID", "Identités : utilisateurs, groupes, identités managées", "3 groupes, 2 identités managées"],
            ["Azure RBAC", "Droits sur les ressources (et données au niveau conteneur)", "Reader, Owner limité"],
            ["ACL", "Droits POSIX par répertoire et fichier", "Accès par zone"],
        ], [22, 44, 34]),
        p("Abonnement ⊃ groupe de ressources ⊃ compte de stockage (HNS) ⊃ conteneur ⊃ répertoires. Entra ID fournit les identités ; "
          "RBAC et ACL leur donnent des droits.")),
    sec("3. Hierarchical Namespace (HNS)",
        t(["Aspect", "Avec HNS (ADLS Gen2)", "Sans HNS (Blob / objet)"], [
            ["Répertoires", "Vrais répertoires", "Préfixes dans le nom de l'objet"],
            ["Renommer / supprimer un dossier", "Une opération atomique", "Copie puis suppression de chaque objet"],
            ["Permissions", "ACL POSIX par répertoire et fichier, héritage par défaut", "Niveau conteneur ou compte seulement"],
            ["Moteurs", "Pilote ABFS : Spark, Synapse, Hadoop", "API objet"],
            ["Usage", "Data Lake en zones, commits de tables", "Archives, médias"],
        ], [24, 40, 36]),
        note("Équivalent local : HDFS offre la même hiérarchie et les mêmes droits POSIX ; MinIO, stockage objet, n'en a pas.")),
    sec("4. Organisation ADLS Gen2",
        pre("""
retail-intelligence/
|-- bronze/tpcxbb/<table>/lot=<initial|refresh>/ingest_date=AAAA-MM-JJ/<table>.dat
|-- silver/{ventes,retours,produits,magasins,calendrier}/<table>/     Parquet (Iceberg)
|-- gold/indicateurs/kpi/  gold/analyses/<sujet>/                       Parquet, CSV
|-- quality/AAAA-MM-JJ/rapport_<uc>.csv
`-- documentation/
"""),
        t(["Zone", "Fonction", "Utilisateurs / traitements", "Conservation, traçabilité"], [
            ["bronze", "Fichiers reçus, inchangés", "ADF (écriture), Data Eng. (lecture)", "Immuable, 1 an, sha256"],
            ["silver", "Typé, nettoyé, contrôlé", "Spark Pool (écriture), Data Eng.", "Snapshots de table, colonnes _lot, _source_fichier"],
            ["gold", "KPI et analyses", "Spark Pool (écriture), analystes, Power BI", "Versionné par date de calcul"],
            ["quality", "Rapports de contrôle", "Traitements, Data Steward", "90 jours"],
            ["documentation", "Dictionnaire, schémas", "Tous (lecture)", "Git"],
        ], [14, 24, 32, 30], cls="s"),
        note("Détail : <code>Jour4/architecture/organisation_adls.md</code>. Les données personnelles restent en bronze.")),
    sec("5. Sécurité et permissions",
        t(["Mécanisme", "Ce qu'il contrôle", "Usage proposé"], [
            ["Entra ID", "Qui est l'utilisateur ou le service", "Groupes nominatifs, identités managées ADF et Synapse"],
            ["Azure RBAC", "Actions sur les ressources ; rôles données au niveau conteneur", "Reader pour voir les ressources ; aucun rôle données large"],
            ["ACL", "Lecture / écriture / parcours par répertoire", "Droits par zone (matrice ci-dessous)"],
            ["Authentification", "Jeton Entra ID (OAuth), pas de clé de compte", "<code>--auth-mode login</code>, clés partagées désactivées"],
            ["Secrets", "Mots de passe des sources externes", "Key Vault, jamais dans Git"],
        ], [18, 40, 42]),
        t(["Profil", "Bronze", "Silver", "Gold", "Quality"], [
            ["Pipeline ADF (identité managée)", "Écriture (-wx)", "Aucun", "Aucun", "Aucun"],
            ["Spark Synapse (identité managée)", "Lecture (r-x)", "Lecture / écriture", "Écriture", "Écriture"],
            ["Data Engineering", "Lecture", "Lecture / écriture", "Écriture contrôlée", "Lecture"],
            ["Analyste métier", "Aucun", "Lecture sans données personnelles", "Lecture (r-x)", "Aucun"],
            ["Data Steward", "Lecture", "Lecture", "Lecture", "Lecture / écriture"],
            ["Administrateur", "Gestion (RBAC), pas de lecture par défaut", "idem", "idem", "idem"],
        ], [26, 18, 20, 18, 18], cls="s"),
        note("Moindre privilège : RBAC donne l'accès aux ressources, l'ACL l'accès aux données d'une zone. Détail : <code>architecture/matrice_permissions.pdf</code>.")),
    sec("6. Azure Data Factory et Synapse",
        t(["Service", "Responsabilité", "Dans l'architecture"], [
            ["ADLS Gen2", "Stockage des données", "Zones bronze, silver, gold"],
            ["Azure Data Factory", "Intégration, copie, orchestration (pipelines, déclencheurs)", "Copie des fichiers TPCx-BB vers bronze, lance les traitements"],
            ["Azure Synapse Analytics", "Environnement d'analyse unifié", "Traitements et requêtes"],
            ["Synapse Studio", "Interface : notebooks, scripts SQL, supervision", "Développement des traitements"],
            ["Spark Pools", "Moteur distribué à la demande", "Bronze → Silver → Gold (code PySpark du Jour 3)"],
            ["SQL serverless / dédié", "SQL sur les fichiers du lac / entrepôt", "Requêtes sur gold, source Power BI"],
            ["Power BI", "Visualisation", "Tableaux de bord des KPI UC-08"],
        ], [22, 40, 38])),
    sec("7. Schémas d'architecture",
        img("Jour4/architecture/schema_architecture.png", "Architecture cible Azure (proposée, non déployée).", 92),
        img("Jour4/architecture/schema_parcours_b_local.png", "Parcours B réellement déployé (Docker Compose).", 82), coupable=True),
    sec("8. Mise en œuvre",
        sous("Réalisé en local (parcours B)",
             fichier("Jour4/preuves/uc07/parcours_b_local.txt", 33, 44),
             p("Trino lit les tables Gold Iceberg stockées dans MinIO : 720 lignes, 667 579 lignes de vente, CA identique. "
               "MinIO : bronze 209 Mio, silver 43 Mio, gold 821 Kio.")),
        sous("Simulation Azure",
             t(["Étape", "Contenu"], [
                 ["Ressources", "Groupe, compte HNS, conteneur, 3 groupes Entra, ADF, Synapse, Key Vault"],
                 ["Opérations", "Création, répertoires, dépôt de <code>kpi.csv</code>, ACL, rôle Reader (Azure CLI)"],
                 ["Contrôles", "isHnsEnabled, liste, taille, ACL, accès public désactivé, budget"],
                 ["Statut", "Non exécuté : <code>preuves/uc07/simulation_azure.md</code>"],
             ], [18, 82]))),
    sec("9. Comparaison Azure / open source",
        t(["Rôle", "Azure", "Retenu (local)", "État", "Limite de l'équivalence"], [
            ["Stockage du lac", "ADLS Gen2 + HNS", "MinIO (S3) ; HDFS au Jour 2", ok("déployé"), "MinIO sans HNS ni ACL POSIX"],
            ["Format de table", "Delta / Parquet dans Synapse", "Apache Iceberg + Parquet", ok("déployé"), "—"],
            ["Catalogue", "Synapse / Purview", "Iceberg REST (fixture)", ok("déployé"), "Catalogue de test, base SQLite"],
            ["Traitement", "Synapse Spark Pool", "Spark 4.1.4 local[*]", ok("déployé"), "Une machine, pas d'élasticité"],
            ["SQL analytique", "Synapse SQL serverless", "Trino 484", ok("déployé"), "Un seul nœud"],
            ["Ingestion, orchestration", "Data Factory", "NiFi (ingestion), Airflow", na("NiFi déployé, Airflow étudié"), "Pas de planification automatique"],
            ["Identités, droits", "Entra ID, RBAC, ACL", "Comptes Linux, ports sur 127.0.0.1", na("partiel"), "Pas d'identités par profil"],
            ["Secrets", "Key Vault", "Variables d'environnement", na("partiel"), "Identifiants MinIO par défaut, locaux"],
            ["Visualisation", "Power BI", "Matplotlib", ok("déployé"), "Graphiques statiques"],
        ], [16, 19, 21, 17, 27], cls="s"),
        p("Synapse réunit plusieurs fonctions dans un service géré ; en local il faut Spark, Trino, Iceberg, un catalogue et un orchestrateur pour les couvrir.")),
    sec("10. Justification et limites",
        t(["Choix", "Raison"], [
            ["Parcours B", "Pas d'abonnement autorisé ; aucune facturation possible"],
            ["Iceberg sur MinIO", "Tables versionnées (snapshots) lisibles par Spark et Trino"],
            ["ADLS Gen2 avec HNS", "Répertoires réels, ACL par zone, opérations atomiques"],
            ["Données personnelles en bronze seulement", "Moindre exposition"],
        ], [32, 68]),
        t(["Limite / contrainte", "Conséquence"], [
            ["Aucune ressource Azure créée", "Pas de capture Azure ; simulation documentée"],
            ["Mono-machine", "Performances et tolérance aux pannes non représentatives"],
            ["Coût Azure", "Faible pour quelques Mo (LRS) ; Spark Pool et Synapse dédiés à surveiller, budget et suppression du groupe"],
        ], [32, 68])),
]

# --------------------------------------------------------------------------- Matrice
matrice = [
    sec("Principe",
        t(["Niveau", "Mécanisme", "Règle"], [
            ["Ressource", "Azure RBAC", "Reader pour consulter ; Owner réservé à l'administrateur ; aucun rôle données au niveau conteneur pour les profils métier"],
            ["Données", "ACL POSIX", "Droits par zone ; ACL par défaut sur chaque répertoire pour l'héritage"],
            ["Identité", "Entra ID", "Groupes nominatifs ; identités managées pour ADF et Synapse"],
        ], [16, 18, 66])),
    sec("Matrice des rôles et permissions",
        t(["Profil", "RBAC (groupe de ressources)", "bronze/", "silver/", "gold/", "quality/"], [
            ["Pipeline ADF", "—", "-wx", "---", "---", "---"],
            ["Spark Synapse", "—", "r-x", "rwx", "rwx", "rwx"],
            ["grp-data-eng", "Reader", "r-x", "rwx", "rwx (contrôlé)", "r-x"],
            ["grp-analystes", "Reader", "---", "r-x (sans PII)", "r-x", "---"],
            ["grp-data-steward", "Reader", "r-x", "r-x", "r-x", "rwx"],
            ["Administrateur", "Owner", "gestion", "gestion", "gestion", "gestion"],
        ], [20, 20, 13, 17, 16, 14]),
        note("r = lire, w = écrire, x = parcourir le répertoire. « --- » : aucun accès par défaut. Statut : proposition, non déployée.")),
    sec("Contrôles prévus",
        t(["Contrôle", "Fréquence"], [
            ["Revue des membres des groupes", "Mensuelle"],
            ["Journaux d'accès du compte de stockage (diagnostic)", "Continue"],
            ["Vérification des ACL (<code>az storage fs access show</code>)", "À chaque nouvelle zone"],
        ], [70, 30])),
]

if __name__ == "__main__":
    build("Jour4/UC08_analyses_visualisations.pdf", "UC-08", "Analyse des données et visualisation", "".join(uc08), DATE,
          "Jour 4 – UC-08", "KPI, statistiques, visualisation, Iceberg")
    build("Jour4/UC07_architecture_azure.pdf", "UC-07", "Transposition de la plateforme sur Azure (parcours B)", "".join(uc07), DATE,
          "Jour 4 – UC-07", "Azure, ADLS Gen2, HNS, RBAC, ACL, Data Factory, Synapse")
    build("Jour4/architecture/matrice_permissions.pdf", "Matrice des permissions", "Zones ADLS Gen2 – proposition UC-07",
          "".join(matrice), DATE, "Jour 4 – UC-07", "RBAC, ACL, Entra ID, moindre privilège")
