"""Jour 3 : extrait les preuves des notebooks exécutés puis génère UC06_traitements_PySpark.pdf.

uv run --no-project --with pikepdf python Jour3/build_docs.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "docs"))
from pdfgen import RACINE, build, encadre, le, note, ok, p, sec, sous, t  # noqa: E402

DATE = le(18)
NB = RACINE / "notebooks"
PREUVES = RACINE / "Jour3" / "preuves"

# notebook, cellules, fichier de preuve, titre
EXTRAITS = [
    ("uc06_exploration.ipynb", [1], "environnement/versions_exploration.txt", "Versions, mode d'exécution, ressources"),
    ("uc06_silver_gold.ipynb", [1], "environnement/versions_traitement.txt", "Versions, defaultFS HDFS, chemins d'entrée et de sortie"),
    ("uc06_exploration.ipynb", [3, 5], "exploration/schemas_volumes.txt", "Largeur, lignes, octets, schémas texte, échantillons"),
    ("uc06_exploration.ipynb", [6, 7], "exploration/vides_doublons_bornes.txt", "Valeurs vides, doublons, clés, bornes"),
    ("uc06_silver_gold.ipynb", [3], "transformations/nettoyage_typage.txt", "Schéma typé, lignes écartées, doublons, profits négatifs"),
    ("uc06_silver_gold.ipynb", [5], "transformations/jointure_ventes_produits.txt", "Jointure vérifiée ventes → produits"),
    ("uc06_silver_gold.ipynb", [7], "silver_gold/gold_ventes_par_produit.txt", "Agrégation Gold par produit"),
    ("uc06_silver_gold.ipynb", [9], "parquet/ecriture_relecture.txt", "Écriture Parquet puis relecture : schéma, lignes, échantillon"),
    ("uc06_silver_gold.ipynb", [11], "parquet/comparaison_formats.txt", "Volumes plat / Parquet / CSV, chemins HDFS"),
    ("uc06_silver_gold.ipynb", [13], "qualite/bilan_controles.txt", "Bilan des 9 contrôles qualité"),
]


def sorties(cellule):
    texte = []
    for sortie in cellule.get("outputs", []):
        brut = "".join(sortie.get("text", "")) or "".join(sortie.get("data", {}).get("text/plain", ""))
        texte += [l for l in brut.splitlines() if not any(m in l for m in ("WARN", "log4j", "setLogLevel", "incubator"))]
    return texte


def extraire():
    for nom, cellules, cible, titre in EXTRAITS:
        cells = json.loads((NB / nom).read_text())["cells"]
        lignes = [f"# {titre}", f"# Source : notebooks/{nom}, cellule(s) {', '.join(map(str, cellules))} (sorties enregistrées)"]
        for i in cellules:
            lignes += ["", f"## cellule {i} – code", *"".join(cells[i]["source"]).splitlines(), "", f"## cellule {i} – sortie", *sorties(cells[i])]
        chemin = PREUVES / cible
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")
        print("preuve", chemin.relative_to(RACINE))



corps = [
    sec("Partie 1 – Environnement et inventaire des sources",
        sous("Environnement observé",
             t(["Élément", "Exécution d'origine (19/11)", "Rejeu de contrôle (22/11)"], [
                 ["Python", "3.12.3", "3.12.14 (conteneur <code>lake</code>)"],
                 ["Spark / PySpark", "4.3.0", "4.1.4"],
                 ["Java", "OpenJDK 17", "OpenJDK 17 (Temurin)"],
                 ["Mode", "<code>local[*]</code>, 12 cœurs", "<code>local[*]</code>"],
                 ["Entrées", "<code>/data/retail_project/data/{store_sales,item}</code> (lecture seule)", "idem"],
                 ["Sorties", "HDFS <code>/retail-lake/silver/uc06</code>, <code>/retail-lake/gold/uc06</code>", "idem + copie Gold dans <code>Jour3/data/gold</code>"],
                 ["Notebooks", "<code>notebooks/uc06_exploration.ipynb</code>, <code>uc06_silver_gold.ipynb</code>", "même code"],
             ], [18, 44, 38])),
        sous("Inventaire des deux sources",
             t(["Information", "store_sales.dat", "item.dat"], [
                 ["Emplacement", "data/store_sales/", "data/item/"],
                 ["Format", "Texte structuré, séparateur |, sans en-tête", "idem"],
                 ["Taille", "92 764 700 o", "6 799 286 o"],
                 ["Lignes / colonnes", "667 579 / 23", "17 820 / 22"],
                 ["Colonnes principales", "date, ticket, article, magasin, quantité, montants", "identifiant, catégorie, classe, prix, nom"],
                 ["Types", "entiers (clés, quantité), décimaux 2 chiffres (montants)", "entiers, texte, dates, décimaux"],
                 ["Clé candidate", "aucune simple : (ticket, article) non unique", "<code>i_item_sk</code> (17 820 distincts)"],
                 ["Granularité", "un article dans un ticket", "un article"],
                 ["Anomalies", "clés secondaires vides (≤ 0,07 %), profit négatif 74 %", "<code>i_rec_end_date</code> vide à 100 %"],
             ], [22, 42, 36])),
        note("Noms de colonnes : spécification TPCx-BB 1.7.0, appliqués seulement si la largeur observée correspond (23 et 22).")),
    sec("Partie 2 – Exploration et règles de nettoyage",
        sous("Constats d'exploration",
             t(["Question", "Réponse observée"], [
                 ["Structuré ?", "Oui : largeur fixe, séparateur |"],
                 ["Correctement typé ?", "Non à la lecture : tout est texte, schéma explicite ensuite"],
                 ["Valeurs nulles ?", "store_sales : ss_cdemo_sk 238, ss_hdemo_sk 295, ss_addr_sk 448, ss_promo_sk 158 ; item : i_rec_end_date 17 820"],
                 ["Doublons ?", "0 doublon exact dans les deux fichiers"],
                 ["Identifiants uniques ?", "i_item_sk et i_item_id : 17 820 distincts ; 89 100 tickets"],
                 ["Valeurs atypiques ?", "ss_net_profit &lt; 0 sur 495 971 lignes ; ss_net_paid de 0,00 à 9 999,82 (texte)"],
                 ["Adapté au Jour 1 ?", "Oui : CA net magasin par produit"],
             ], [24, 76]),
             encadre("Piège relevé : les bornes calculées sur du texte suivent l'ordre alphabétique. "
                     "La quantité maximale affichée est 99 ; sur la colonne typée (Jour 4) elle vaut 100.")),
        sous("Règles de nettoyage",
             t(["Anomalie", "Règle", "Action", "Justification"], [
                 ["Pas d'en-tête, tout en texte", "Largeur 23 / 22", "Schéma explicite, sinon arrêt", "Noms de la spécification, contrôlés"],
                 ["Valeur manquante", "Champ vide → null", "Conservé si facultatif", "Foyer, adresse, promotion peuvent manquer"],
                 ["Identifiant invalide", "Date, article, magasin, ticket, quantité, montant requis", "Ligne écartée et comptée", "Sinon pas une vente exploitable"],
                 ["Quantité ≤ 0", "<code>ss_quantity &gt; 0</code>", "Ligne écartée et comptée", "N'entre pas dans le CA"],
                 ["Doublon", "Ligne identique sur toutes les colonnes", "Supprimé et compté", "Définition claire : la ligne entière"],
                 ["Valeur atypique", "<code>ss_net_profit &lt; 0</code>", "Conservée", "Résultat de ligne, pas une erreur"],
                 ["Date incohérente", "<code>i_rec_end_date</code> null", "Conservée", "Aucune fin de version observée"],
                 ["Type mixte", "Libellés avec chiffres", "Laissés en texte", "Un nombre isolé ne change pas le type"],
             ], [19, 27, 22, 32], cls="s"))),
    sec("Partie 3 – Transformations et données Silver",
        t(["Transformation", "Détail", "Résultat"], [
            ["Typage", "LongType (clés), IntegerType (quantité), Decimal(7,2) (montants), DateType", "0 échec de lecture"],
            ["Filtrage", "Règles de la partie 2", "0 ligne écartée, 0 doublon"],
            ["Provenance", "Colonnes <code>source_fichier</code>, <code>source_lot</code>", "Chaque ligne garde son origine"],
            ["Jointure", "ventes.ss_item_sk = produits.i_item_sk, gauche, N → 1", "667 579 lignes avant et après, 0 orphelin"],
            ["Agrégation", "groupBy article : lignes, quantité, CA net, CA TTC, profit", "17 820 articles"],
        ], [17, 53, 30]),
        t(["Jeu Silver", "Chemin HDFS", "Lignes", "Colonnes", "Format"], [
            ["store_sales", "/retail-lake/silver/uc06/store_sales", "667 579", "25", "Parquet snappy"],
            ["item", "/retail-lake/silver/uc06/item", "17 820", "24", "Parquet snappy"],
        ], [16, 42, 14, 12, 16], num=(2, 3)),
        note("Convention : <code>/retail-lake/&lt;zone&gt;/&lt;cas d'usage&gt;/&lt;table&gt;</code>. Lot initial seulement ; le lot refresh reste en Raw.")),
    sec("Partie 4 – Données Gold et Parquet",
        sous("Gold : ventes_magasin_par_produit",
             t(["Élément", "Description"], [
                 ["Finalité", "CA net des ventes magasin par produit (question Direction commerciale, Jour 1)"],
                 ["Sources", "Silver store_sales + Silver item"],
                 ["Granularité", "Un article (<code>i_item_sk</code>)"],
                 ["Mesures", "nb_lignes, quantite, ca_net = Σ ss_net_paid, ca_net_ttc, profit_net"],
                 ["Résultat", "17 820 lignes, CA net total 1 150 529 586,37 (= contrôle Jour 1)"],
                 ["Limites", "Lot initial, unité monétaire inconnue, profit négatif inclus"],
             ], [18, 82])),
        sous("Écriture et relecture Parquet",
             t(["Jeu", "Lignes écrites", "Lignes relues", "Schéma conservé"], [
                 ["Silver ventes", "667 579", "667 579", ok("oui")],
                 ["Silver produits", "17 820", "17 820", ok("oui")],
                 ["Gold", "17 820", "17 820", ok("oui (decimal 17,2)")],
             ], [30, 22, 22, 26], num=(1, 2))),
        sous("Comparaison des formats",
             t(["Critère", "Plat / CSV", "JSON", "Parquet"], [
                 ["Organisation", "Ligne", "Document par ligne", "Colonne, compressée"],
                 ["Lisibilité", "Texte lisible", "Texte lisible", "Binaire, outil requis"],
                 ["Types", "Aucun", "Simples", "Schéma typé dans le fichier"],
                 ["Volume observé", "Ventes 92,8 Mo ; Gold CSV 1,88 Mo", "Absent des sources", "Ventes 57,0 Mo (−39 %) ; Gold 1,15 Mo (−39 %)"],
                 ["Usage", "Échange, sources", "API, semi-structuré", "Analyse, lecture de colonnes"],
                 ["Limite", "Typage à refaire", "Volumineux", "Pas ACID ni historique (Iceberg au Jour 4)"],
             ], [17, 27, 20, 36], cls="s"))),
    sec("Partie 5 – Contrôles qualité et documentation",
        t(["Contrôle", "Règle", "Résultat", ""], [
            ["Volume ventes", "Lignes Silver = lignes du fichier", "667 579 / 667 579", ok()],
            ["Volume produits", "Lignes Silver = lignes du fichier", "17 820 / 17 820", ok()],
            ["Complétude", "Champs requis non nuls", "0 ligne écartée", ok()],
            ["Unicité", "i_item_sk unique", "0 doublon", ok()],
            ["Validité quantité", "ss_quantity &gt; 0", "0 écart", ok()],
            ["Validité montant", "ss_net_paid non nul", "0 écart", ok()],
            ["Intégrité", "Chaque ss_item_sk trouve un i_item_sk", "0 orphelin", ok()],
            ["Cohérence Gold", "Σ lignes Gold = lignes jointes", "667 579", ok()],
            ["Cohérence profit", "Profits négatifs conservés", "495 971", ok("conservé")],
        ], [20, 38, 30, 12]),
        t(["Bilan", "Contenu"], [
            ["Règles respectées", "9 / 9"],
            ["Anomalies restantes", "Clés secondaires vides, profit négatif (connu, non corrigé)"],
            ["Données écartées", "Aucune"],
            ["Limites", "Lot initial seul ; noms de colonnes déduits ; intégrité vérifiée sur item seulement"],
        ], [24, 76]),
        p("Reproduction : voir <code>Jour3/README.md</code>. Rejeu du 22/11 dans le conteneur actuel : mêmes 9 résultats, même CA.")),
    sec("Annexe – preuves",
        t(["Fichier", "Ce qu'il démontre"], [
            *[[f"preuves/{c}", titre] for _, _, c, titre in EXTRAITS],
            ["preuves/rejeu_2026-11-22.txt", "Rejeu complet : versions et bilan qualité identiques"],
            ["data/gold/ventes_magasin_par_produit/", "Gold Parquet réellement produit (copie depuis HDFS)"],
        ], [44, 56], cls="s")),
]

if __name__ == "__main__":
    extraire()
    build("Jour3/UC06_traitements_PySpark.pdf", "UC-06", "Traitement et transformation des données avec Python / PySpark",
          "".join(corps), DATE, "Jour 3 – UC-06", "PySpark, Silver, Gold, Parquet, qualité")
