"""Génère les PDF des livrables : HTML -> Chrome headless -> métadonnées (auteur, date).

Usage : uv run --no-project --with pikepdf python JourN/build_docs.py
Prérequis : google-chrome (ou chromium) dans le PATH.
"""
import html
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pikepdf

AUTEUR = "Paul"
PROJET = "Retail Intelligence Platform – IPSSI"
CET = timezone(timedelta(hours=1))
RACINE = Path(__file__).resolve().parent.parent

CSS = """
@page { size: A4; margin: 18mm 17mm 18mm 17mm;
  @bottom-left { content: "%(pied)s"; font: 8pt 'Liberation Sans', Arial, sans-serif; color: #777; }
  @bottom-right { content: counter(page) " / " counter(pages); font: 8pt 'Liberation Sans', Arial, sans-serif; color: #777; } }
body { font-family: 'Liberation Sans', Arial, Helvetica, sans-serif; color: #111; margin: 0; font-size: 10pt; }
header.titre { border-bottom: 2pt solid #1f4e9a; padding-bottom: 6pt; margin-bottom: 14pt; }
header.titre h1 { font-size: 22pt; font-weight: 700; margin: 0 0 2pt 0; color: #1f4e9a; }
header.titre .sous { font-size: 12pt; color: #333; margin: 0 0 6pt 0; }
header.titre .meta { font-size: 9pt; color: #555; }
h2 { font-size: 13.5pt; color: #1f4e9a; margin: 16pt 0 6pt 0; break-after: avoid; page-break-after: avoid; }
h3 { font-size: 11pt; color: #333; margin: 10pt 0 4pt 0; break-after: avoid; page-break-after: avoid; }
section.saut { break-before: page; }
p { line-height: 1.32; margin: 0 0 6pt 0; color: #222; }
p.note { font-size: 8.5pt; color: #555; }
ul { margin: 0 0 6pt 0; padding-left: 16pt; } li { margin: 0 0 2pt 0; line-height: 1.3; }
table { border-collapse: collapse; width: 100%%; margin: 0 0 9pt 0; table-layout: fixed;
  font-family: Carlito, Calibri, 'Liberation Sans', Arial, sans-serif; font-size: 9.5pt; }
table.s { font-size: 8.5pt; }
thead { display: table-header-group; }
th, td { border: 0.75pt solid #9aa5b5; padding: 2.5pt 4pt; text-align: left; vertical-align: top; overflow-wrap: anywhere; }
th { background: #dbe4f3; font-weight: 700; }
tr { break-inside: avoid; page-break-inside: avoid; }
td.n, th.n { text-align: right; }
.ok { color: #17702d; font-weight: 700; } .ko { color: #b3261e; font-weight: 700; } .na { color: #8a5a00; font-weight: 700; }
code { font-family: 'Liberation Mono', 'DejaVu Sans Mono', monospace; font-size: 8.5pt; background: #f2f4f7; padding: 0 2pt; }
pre { font-family: 'Liberation Mono', 'DejaVu Sans Mono', monospace; font-size: 7.6pt; line-height: 1.25; background: #f5f6f8;
  border: 0.75pt solid #d5dae1; padding: 5pt 6pt; margin: 0 0 8pt 0; white-space: pre-wrap; overflow-wrap: anywhere; break-inside: avoid; }
pre.long { break-inside: auto; }
figure { margin: 4pt 0 10pt 0; break-inside: avoid; page-break-inside: avoid; text-align: center; }
figure img { max-width: 100%%; max-height: 120mm; border: 0.5pt solid #ccc; }
figcaption { font-size: 8.5pt; color: #444; margin-top: 3pt; text-align: left; }
.bloc { break-inside: avoid; page-break-inside: avoid; }
.encadre { border-left: 3pt solid #1f4e9a; background: #eef3fb; padding: 4pt 8pt; margin: 0 0 8pt 0; break-inside: avoid; }
"""


def esc(s):
    return html.escape(str(s))


def p(s, cls=""):
    return f'<p class="{cls}">{s}</p>'


def note(s):
    return p(s, "note")


def encadre(s):
    return f'<div class="encadre">{s}</div>'


def ul(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def t(head, rows, widths=None, cls="", num=()):
    """Tableau ; num = indices de colonnes alignées à droite. Le texte des cellules est déjà du HTML."""
    cg = "".join(f'<col style="width:{w}%">' for w in widths) if widths else ""
    h = "".join(f'<th class="{"n" if i in num else ""}">{c}</th>' for i, c in enumerate(head))
    b = "".join(
        "<tr>" + "".join(f'<td class="{"n" if i in num else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>"
        for r in rows
    )
    return f'<table class="{cls}"><colgroup>{cg}</colgroup><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


def pre(texte, long=False):
    return f'<pre class="{"long" if long else ""}">{esc(texte.strip(chr(10)))}</pre>'


def fichier(chemin, debut=None, fin=None, long=False):
    """Extrait d'un fichier de preuve (lignes debut..fin, 1-indexées)."""
    lignes = (RACINE / chemin).read_text(encoding="utf-8").splitlines()
    return pre("\n".join(lignes[(debut or 1) - 1:fin]), long)


def img(chemin, legende, largeur=100):
    src = (RACINE / chemin).resolve().as_uri()
    return f'<figure><img src="{src}" style="width:{largeur}%"><figcaption>{legende}</figcaption></figure>'


def sec(titre, *parts, saut=False, coupable=False):
    """Section ; insécable par défaut (déplacée entière sur la page suivante si elle tient sur une page)."""
    cls = " ".join(c for c, on in (("saut", saut), ("bloc", not coupable)) if on)
    return f'<section class="{cls}"><h2>{titre}</h2>' + "".join(parts) + "</section>"


def sous(titre, *parts):
    return f"<h3>{titre}</h3>" + "".join(parts)


def ok(s="OK"):
    return f'<span class="ok">{s}</span>'


def ko(s):
    return f'<span class="ko">{s}</span>'


def na(s):
    return f'<span class="na">{s}</span>'


def chrome():
    for nom in ("google-chrome", "chromium-browser", "chromium"):
        if shutil.which(nom):
            return nom
    raise SystemExit("Chrome ou Chromium introuvable")


def build(sortie, titre, sous_titre, corps, date, sujet, mots_cles=""):
    """Écrit le PDF `sortie` (relatif à la racine du dépôt) et fixe ses métadonnées."""
    sortie = RACINE / sortie
    sortie.parent.mkdir(parents=True, exist_ok=True)
    jour = date.strftime("%d/%m/%Y")
    pied = f"{titre} · {PROJET}".replace('"', "")
    doc = (
        f"<!DOCTYPE html><html lang='fr'><head><meta charset='utf-8'><title>{esc(titre)}</title>"
        f"<style>{CSS % {'pied': pied}}</style></head><body>"
        f"<header class='titre'><h1>{esc(titre)}</h1><div class='sous'>{esc(sous_titre)}</div>"
        f"<div class='meta'>{PROJET} · Auteur : {AUTEUR} · {jour}</div></header>"
        f"{corps}</body></html>"
    )
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "doc.html"
        brut = Path(tmp) / "doc.pdf"
        src.write_text(doc, encoding="utf-8")
        subprocess.run(
            [chrome(), "--headless=new", "--disable-gpu", "--no-sandbox", "--allow-file-access-from-files",
             "--no-pdf-header-footer", "--virtual-time-budget=5000", f"--print-to-pdf={brut}", src.as_uri()],
            check=True, capture_output=True,
        )
        with pikepdf.open(brut) as pdf:
            stamp = date.strftime("D:%Y%m%d%H%M%S+01'00'")
            pdf.docinfo["/Title"] = f"{titre} – {sous_titre}"
            pdf.docinfo["/Author"] = AUTEUR
            pdf.docinfo["/Subject"] = sujet
            pdf.docinfo["/Keywords"] = mots_cles
            pdf.docinfo["/Creator"] = "HTML + Chrome headless (docs/pdfgen.py)"
            pdf.docinfo["/CreationDate"] = stamp
            pdf.docinfo["/ModDate"] = stamp
            with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:
                meta.load_from_docinfo(pdf.docinfo)
                meta["xmp:CreateDate"] = date.isoformat()
                meta["xmp:ModifyDate"] = date.isoformat()
                meta["xmp:MetadataDate"] = date.isoformat()
            pdf.save(sortie)
    print("écrit", sortie.relative_to(RACINE))


def le(jour, heure=17, minute=30):
    """Date d'un jour de TP en novembre 2026, heure de Paris."""
    return datetime(2026, 11, jour, heure, minute, tzinfo=CET)
