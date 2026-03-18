#!/usr/bin/env python3
"""
generate_sitemap.py
-------------------
Scansiona una cartella locale del sito e genera due file:
  - sitemap.xml        (sitemap standard per Googlebot e tutti i crawler)
  - sitemap-news.xml   (Google News sitemap, solo articoli divulgativi)

Uso:
    python3 generate_sitemap.py

Configura le variabili nella sezione CONFIG prima di eseguire.

──────────────────────────────────────────────────────────────────────
COME AGGIUNGERE UN NUOVO ARTICOLO ALLA NEWS SITEMAP
──────────────────────────────────────────────────────────────────────
Aggiungi un dizionario alla lista NEWS_ARTICLES in basso con i campi:
  - path:  percorso relativo al file HTML (es. "art-divulgativi/mio-articolo.html")
  - title: titolo dell'articolo (stringa)
  - date:  data ISO 8601 con timezone (es. "2025-12-20T00:00:00+01:00")
──────────────────────────────────────────────────────────────────────
"""

import os
import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG — modifica questi valori prima di eseguire
# ─────────────────────────────────────────────────────────────────────────────

# Cartella radice del sito: si posiziona automaticamente dove si trova questo script.
# Non serve modificare nulla — metti generate_sitemap.py nella root del sito e giralo.
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))

# Dominio base (senza slash finale)
BASE_URL = "https://www.ludovicopapalia.com"

# Nome della testata per la News sitemap (deve essere coerente con il Publisher Center)
NEWS_PUBLICATION_NAME = "Ludovico Papalia — Diritto Informatico"
NEWS_LANGUAGE = "it"

# File da escludere sempre (nomi esatti, case-sensitive)
EXCLUDE_FILES = {
    "404.html",
    "sitemap.xml",
    "sitemap-news.xml",
    "robots.txt",
    "llms.txt",
}

# Cartelle da escludere (nomi, non path completi)
EXCLUDE_DIRS = {
    ".git",
    ".github",
    "node_modules",
    "assets",
    "cdn-cgi",
}

# Estensioni da includere nella sitemap standard
INCLUDE_EXTENSIONS = {".html", ".htm"}

# Dove salvare le sitemap generate
OUTPUT_SITEMAP      = os.path.join(SITE_ROOT, "sitemap.xml")
OUTPUT_SITEMAP_NEWS = os.path.join(SITE_ROOT, "sitemap-news.xml")

# Priorità per percorso (default 0.5 se non specificato)
PRIORITY_MAP = {
    "/index.html": "1.0",
    "/":           "1.0",
    "/articoli/index.html": "0.8",
    "/articoli/":           "0.8",
}

# Frequenza di cambiamento di default
CHANGEFREQ_MAP = {
    "/index.html": "monthly",
    "/":           "monthly",
}
DEFAULT_CHANGEFREQ = "yearly"

# ─────────────────────────────────────────────────────────────────────────────
# NEWS ARTICLES — aggiorna questa lista ogni volta che pubblichi un articolo
# ─────────────────────────────────────────────────────────────────────────────
# Ordine: dal più recente al più vecchio.
# "path" deve corrispondere esattamente al file HTML nella root del sito.
# "date" usa il formato ISO 8601 con timezone:
#   estate (CET+2): "YYYY-MM-DDT00:00:00+02:00"
#   inverno (CET+1): "YYYY-MM-DDT00:00:00+01:00"

NEWS_ARTICLES = [
    {
        "path":  "art-divulgativi/ai-lavoro-trasformazione.html",
        "title": "L'AI non ruba lavoro, lo trasforma: una storia vecchia",
        "date":  "2025-12-15T00:00:00+01:00",
    },
    {
        "path":  "art-divulgativi/ai-impatto-ambientale-consumo-energetico.html",
        "title": "Quanto inquina l'AI? Non tutti i modelli sono uguali",
        "date":  "2025-12-15T00:00:00+01:00",
    },
    {
        "path":  "art-divulgativi/browser-ai-agentici.html",
        "title": "Browser AI agentici: cosa possono fare (e cosa possono fare di male)",
        "date":  "2025-11-17T00:00:00+01:00",
    },
    {
        "path":  "art-divulgativi/spid-siti-adulti-privacy.html",
        "title": "SPID per i siti adulti: la privacy è davvero protetta?",
        "date":  "2025-11-17T00:00:00+01:00",
    },
    {
        "path":  "art-divulgativi/siae-contro-meta.html",
        "title": "SIAE contro Meta: chi ha perso davvero?",
        "date":  "2023-04-01T00:00:00+02:00",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# SCRIPT — non modificare oltre questo punto
# ─────────────────────────────────────────────────────────────────────────────

def url_for_path(abs_path):
    """Converte un percorso assoluto in URL relativa alla root del sito."""
    rel = os.path.relpath(abs_path, SITE_ROOT)
    rel = rel.replace("\\", "/")
    if not rel.startswith("/"):
        rel = "/" + rel
    return rel


def get_lastmod(abs_path):
    """Restituisce la data di ultima modifica del file in formato W3C (YYYY-MM-DD)."""
    mtime = os.path.getmtime(abs_path)
    return datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")


def collect_html_files(root):
    """
    Scansiona ricorsivamente la cartella root e restituisce
    la lista dei file HTML da includere nella sitemap standard.
    """
    found = []
    print(f"[SCAN] Scansione cartella: {root}")

    for dirpath, dirnames, filenames in os.walk(root):
        # Rimuovi in-place le cartelle escluse
        dirnames[:] = [
            d for d in dirnames
            if d not in EXCLUDE_DIRS and not d.startswith(".")
        ]

        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in INCLUDE_EXTENSIONS:
                continue
            if filename in EXCLUDE_FILES:
                print(f"  [SKIP] {filename} (escluso per nome)")
                continue

            abs_path = os.path.join(dirpath, filename)
            found.append(abs_path)
            print(f"  [OK]   {os.path.relpath(abs_path, root)}")

    print(f"[SCAN] Totale file trovati: {len(found)}\n")
    return found


def build_sitemap(files):
    """Genera il contenuto XML della sitemap standard."""
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for abs_path in sorted(files):
        url_path = url_for_path(abs_path)
        full_url = BASE_URL + url_path

        # Sostituisci /index.html con / per canonical più pulito
        if url_path == "/index.html":
            full_url = BASE_URL + "/"

        lastmod    = get_lastmod(abs_path)
        priority   = PRIORITY_MAP.get(url_path, "0.5")
        changefreq = CHANGEFREQ_MAP.get(url_path, DEFAULT_CHANGEFREQ)

        lines.append("  <url>")
        lines.append(f"    <loc>{full_url}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")

        print(f"[ENTRY] {full_url}  |  lastmod={lastmod}  |  priority={priority}")

    lines.append("</urlset>")
    return "\n".join(lines)


def build_sitemap_news():
    """
    Genera il contenuto XML della Google News sitemap.

    Nota: Google News usa questa sitemap principalmente per la scoperta
    rapida di articoli recenti (ultimi 2 giorni), ma includiamo tutti gli
    articoli perché il Publisher Center li usa per la configurazione.
    """
    print("\n[NEWS] Generazione sitemap-news.xml...")

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<!--')
    lines.append('  sitemap-news.xml — ludovicopapalia.com')
    lines.append('  Google News sitemap (namespace news:).')
    lines.append('  Aggiornata automaticamente da generate_sitemap.py')
    lines.append('  Ref: https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap')
    lines.append('-->')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
    lines.append('        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">')

    for article in NEWS_ARTICLES:
        full_url = BASE_URL + "/" + article["path"].lstrip("/")

        # Escape caratteri XML nel titolo
        title_safe = (
            article["title"]
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

        lines.append("  <url>")
        lines.append(f"    <loc>{full_url}</loc>")
        lines.append("    <news:news>")
        lines.append("      <news:publication>")
        lines.append(f"        <news:name>{NEWS_PUBLICATION_NAME}</news:name>")
        lines.append(f"        <news:language>{NEWS_LANGUAGE}</news:language>")
        lines.append("      </news:publication>")
        lines.append(f"      <news:publication_date>{article['date']}</news:publication_date>")
        lines.append(f"      <news:title>{title_safe}</news:title>")
        lines.append("    </news:news>")
        lines.append("  </url>")

        print(f"  [NEWS] {full_url}  |  date={article['date']}")

    lines.append("</urlset>")
    print(f"[NEWS] Totale articoli: {len(NEWS_ARTICLES)}")
    return "\n".join(lines)


def main():
    print("=" * 60)
    print("  generate_sitemap.py — Ludovico Papalia")
    print("=" * 60)
    print(f"  SITE_ROOT        : {SITE_ROOT}")
    print(f"  BASE_URL         : {BASE_URL}")
    print(f"  OUTPUT (standard): {OUTPUT_SITEMAP}")
    print(f"  OUTPUT (news)    : {OUTPUT_SITEMAP_NEWS}")
    print("=" * 60 + "\n")

    # Verifica che SITE_ROOT esista
    if not os.path.isdir(SITE_ROOT):
        print(f"[ERRORE] La cartella '{SITE_ROOT}' non esiste.")
        print("         Aggiorna la variabile SITE_ROOT in CONFIG.")
        return

    # ── SITEMAP STANDARD ──────────────────────────────────────────────────────
    files = collect_html_files(SITE_ROOT)

    if not files:
        print("[AVVISO] Nessun file HTML trovato. Controlla SITE_ROOT e EXCLUDE_DIRS.")
        return

    print("[BUILD] Generazione sitemap.xml...")
    xml_standard = build_sitemap(files)
    with open(OUTPUT_SITEMAP, "w", encoding="utf-8") as f:
        f.write(xml_standard)
    print(f"\n[DONE]  sitemap.xml salvata: {len(files)} URL incluse.")

    # ── SITEMAP NEWS ──────────────────────────────────────────────────────────
    xml_news = build_sitemap_news()
    with open(OUTPUT_SITEMAP_NEWS, "w", encoding="utf-8") as f:
        f.write(xml_news)
    print(f"[DONE]  sitemap-news.xml salvata: {len(NEWS_ARTICLES)} articoli inclusi.")

    print("\n──────────────────────────────────────────────────────")
    print("  Prossimi passi dopo aver caricato i file:")
    print("  1. Search Console → Sitemap → invia entrambe")
    print("     https://search.google.com/search-console/sitemaps")
    print("  2. Publisher Center → verifica inclusione")
    print("     https://publishercenter.google.com")
    print("──────────────────────────────────────────────────────")


if __name__ == "__main__":
    main()
