#!/usr/bin/env python3
"""
generate_sitemap.py
-------------------
Scansiona una cartella locale del sito e genera sitemap.xml.

Uso:
    python3 generate_sitemap.py

Configura le variabili nella sezione CONFIG prima di eseguire.
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

# File da escludere sempre (nomi esatti, case-sensitive)
EXCLUDE_FILES = {
    "404.html",
    "sitemap.xml",         # evitiamo di includere la sitemap stessa
    "robots.txt",
    "llms.txt",
}

# Cartelle da escludere (nomi, non path completi)
EXCLUDE_DIRS = {
    ".git",
    ".github",
    "node_modules",
    "assets",              # immagini, font, ecc. non vanno in sitemap
    "cdn-cgi",
}

# Estensioni da includere
INCLUDE_EXTENSIONS = {".html", ".htm"}

# Dove salvare la sitemap generata
OUTPUT_FILE = os.path.join(SITE_ROOT, "sitemap.xml")

# Priorità per percorso (default 0.5 se non specificato)
PRIORITY_MAP = {
    "/index.html":  "1.0",
    "/":            "1.0",
    "/articoli/index.html": "0.8",
    "/articoli/":   "0.8",
}

# Frequenza di cambiamento di default
CHANGEFREQ_MAP = {
    "/index.html": "monthly",
    "/":           "monthly",
}
DEFAULT_CHANGEFREQ = "yearly"

# ─────────────────────────────────────────────────────────────────────────────
# SCRIPT — non modificare oltre questo punto
# ─────────────────────────────────────────────────────────────────────────────

def url_for_path(abs_path: str) -> str:
    """Converte un percorso assoluto in URL relativa alla root del sito."""
    rel = os.path.relpath(abs_path, SITE_ROOT)
    # Normalizza separatori su Windows
    rel = rel.replace("\\", "/")
    # Aggiungi slash iniziale
    if not rel.startswith("/"):
        rel = "/" + rel
    return rel


def get_lastmod(abs_path: str) -> str:
    """Restituisce la data di ultima modifica del file in formato W3C (YYYY-MM-DD)."""
    mtime = os.path.getmtime(abs_path)
    return datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")


def collect_html_files(root: str) -> list[str]:
    """
    Scansiona ricorsivamente la cartella root e restituisce
    la lista dei file HTML da includere nella sitemap.
    """
    found = []
    print(f"[SCAN] Scansione cartella: {root}")

    for dirpath, dirnames, filenames in os.walk(root):
        # Rimuovi in-place le cartelle escluse (evita di scenderci dentro)
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


def build_sitemap(files: list[str]) -> str:
    """Genera il contenuto XML della sitemap."""
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for abs_path in sorted(files):
        url_path = url_for_path(abs_path)
        full_url = BASE_URL + url_path

        # Sostituisci /index.html con / per canonical più pulito
        if url_path == "/index.html":
            full_url = BASE_URL + "/"

        lastmod   = get_lastmod(abs_path)
        priority  = PRIORITY_MAP.get(url_path, "0.5")
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


def main():
    print("=" * 60)
    print("  generate_sitemap.py — Ludovico Papalia")
    print("=" * 60)
    print(f"  SITE_ROOT : {SITE_ROOT}")
    print(f"  BASE_URL  : {BASE_URL}")
    print(f"  OUTPUT    : {OUTPUT_FILE}")
    print("=" * 60 + "\n")

    # Verifica che SITE_ROOT esista
    if not os.path.isdir(SITE_ROOT):
        print(f"[ERRORE] La cartella '{SITE_ROOT}' non esiste.")
        print("         Aggiorna la variabile SITE_ROOT in CONFIG.")
        return

    # Raccolta file
    files = collect_html_files(SITE_ROOT)

    if not files:
        print("[AVVISO] Nessun file HTML trovato. Controlla SITE_ROOT e EXCLUDE_DIRS.")
        return

    # Generazione XML
    print("[BUILD] Generazione sitemap.xml...")
    xml_content = build_sitemap(files)

    # Scrittura
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(xml_content)

    print(f"\n[DONE]  sitemap.xml salvata in: {OUTPUT_FILE}")
    print(f"        {len(files)} URL incluse.")


if __name__ == "__main__":
    main()
