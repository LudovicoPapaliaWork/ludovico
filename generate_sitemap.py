#!/usr/bin/env python3
"""
generate_sitemap.py
-------------------
Scansiona una cartella locale del sito e genera due file:
  - sitemap.xml        (sitemap standard per Googlebot e tutti i crawler)
  - sitemap-news.xml   (Google News sitemap, solo articoli divulgativi)

Alla fine, notifica automaticamente IndexNow con tutti gli URL HTML trovati,
in modo che Bing, Yandex, Naver e altri motori ricrawlino le pagine aggiornate.

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
import json
import urllib.request
import urllib.error

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

# ─────────────────────────────────────────────────────────────────────────────
# INDEXNOW CONFIG
# ─────────────────────────────────────────────────────────────────────────────
# Chiave generata una volta sola. Il file {INDEXNOW_KEY}.txt deve essere
# presente nella root del sito (es. ludovicopapalia.com/acaa81d24b20e17ebf85f615e130e6f4.txt)
# Non è un segreto: è un meccanismo di verifica della proprietà del dominio,
# esattamente come la verifica DNS TXT per Search Console.
#
# Motori supportati (marzo 2026): Bing, Yandex, Naver, Seznam, Yep.
# Google NON supporta IndexNow — per Google continuano a valere sitemap + Search Console.
# Inviando a api.indexnow.org il ping viene automaticamente redistribuito
# a tutti i motori partecipanti.
INDEXNOW_KEY = "acaa81d24b20e17ebf85f615e130e6f4"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
INDEXNOW_KEY_LOCATION = f"{BASE_URL}/{INDEXNOW_KEY}.txt"

# Se True, invia il ping IndexNow al termine dello script.
# Metti False se vuoi solo rigenerare le sitemap senza notificare i motori.
INDEXNOW_ENABLED = True

# File da escludere sempre (nomi esatti, case-sensitive)
EXCLUDE_FILES = {
    "404.html",
    "sitemap.xml",
    "sitemap-news.xml",
    "robots.txt",
    "llms.txt",
    "divulgativo-template.html",    # template, non contenuto reale
    "paper-template.html",          # template, non contenuto reale
    "UNUSED-papers-index.html",     # pagina non in uso
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
    "/index.html":              "1.0",
    "/":                        "1.0",
    "/index-it.html":           "0.9",
    "/divulgativi-index.html":  "0.8",
    "/articoli/index.html":     "0.8",
    "/articoli/":               "0.8",
}

# Frequenza di cambiamento di default
CHANGEFREQ_MAP = {
    "/index.html":             "monthly",
    "/":                       "monthly",
    "/index-it.html":          "monthly",
    "/divulgativi-index.html": "monthly",
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
        "path":  "art-divulgativi/openclaw-agenti-ai-responsabilita-diritto.html",
        "title": "OpenClaw: quando l'AI agisce per te, ma il diritto non sa ancora chi risponde",
        "date":  "2026-03-19T00:00:00+01:00",
    },
    {
        "path":  "art-divulgativi/autenticazione-due-fattori-punto-debole.html",
        "title": "Doppia autenticazione: non tutti i sistemi sono uguali — e spesso sei tu il problema",
        "date":  "2025-05-09T00:00:00+02:00",
    },
    {
        "path":  "art-divulgativi/sim-swap-il-numero-non-e-identita.html",
        "title": "SIM Swap: il tuo numero di telefono non è una prova d'identità",
        "date":  "2025-05-09T00:00:00+02:00",
    },
    {
        "path":  "art-divulgativi/signalgate-federal-records-act.html",
        "title": "Signalgate: Signal funzionava. La legge no.",
        "date":  "2025-04-04T00:00:00+02:00",
    },
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
        "path":  "art-divulgativi/cellulare-scuola-divieto-applicabile.html",
        "title": "Vietare il cellulare a scuola: la norma c'è, ma è applicabile?",
        "date":  "2024-11-05T00:00:00+01:00",
    },
    {
        "path":  "art-divulgativi/chat-genitori-scuola-dati-sensibili-privacy.html",
        "title": "La chat dei genitori viola la privacy dei tuoi figli",
        "date":  "2024-11-05T00:00:00+01:00",
    },
    {
        "path":  "art-divulgativi/instagram-teen-account-profilo-privato-minori.html",
        "title": "Instagram Teen Account: il profilo privato obbligatorio per i minori",
        "date":  "2024-11-05T00:00:00+01:00",
    },
    {
        "path":  "art-divulgativi/responsabilita-genitoriale-sim-cellulare-minori.html",
        "title": "Dai il telefono a tuo figlio? La SIM è tua, la responsabilità anche",
        "date":  "2024-11-05T00:00:00+01:00",
    },
    {
        "path":  "art-divulgativi/social-dipendenza-minori-class-action.html",
        "title": "I social creano dipendenza come le sigarette? Arriva la causa legale",
        "date":  "2024-11-05T00:00:00+01:00",
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


def ping_indexnow(url_list):
    """
    Invia una notifica IndexNow con la lista degli URL aggiornati.

    Il protocollo IndexNow è supportato da: Bing, Yandex, Naver, Seznam, Yep.
    Inviando a api.indexnow.org il ping viene automaticamente redistribuito
    a tutti i motori partecipanti — una sola chiamata è sufficiente.

    Google NON supporta IndexNow (marzo 2026): per Google valgono le sitemap
    e la Search Console come al solito.

    Il file {INDEXNOW_KEY}.txt deve essere presente e raggiungibile sulla root
    del sito, altrimenti il motore rifiuta la richiesta con 403.
    """
    print("\n" + "─" * 60)
    print("[INDEXNOW] Preparazione ping...")
    print(f"[INDEXNOW] Endpoint : {INDEXNOW_ENDPOINT}")
    print(f"[INDEXNOW] Host     : {BASE_URL.replace('https://', '').replace('http://', '')}")
    print(f"[INDEXNOW] Key      : {INDEXNOW_KEY}")
    print(f"[INDEXNOW] Key file : {INDEXNOW_KEY_LOCATION}")
    print(f"[INDEXNOW] URL da notificare: {len(url_list)}")

    # Stampa ogni URL che verrà inviato, per trasparenza
    for u in url_list:
        print(f"  → {u}")

    # Costruisci il payload JSON secondo le specifiche del protocollo
    # Ref: https://www.indexnow.org/documentation
    host = BASE_URL.replace("https://", "").replace("http://", "")
    payload = {
        "host":        host,
        "key":         INDEXNOW_KEY,
        "keyLocation": INDEXNOW_KEY_LOCATION,
        "urlList":     url_list,
    }

    payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    print(f"\n[INDEXNOW] Payload JSON ({len(payload_bytes)} bytes):")
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    # Costruisci la richiesta HTTP POST
    req = urllib.request.Request(
        url=INDEXNOW_ENDPOINT,
        data=payload_bytes,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent":   "generate_sitemap.py/1.0 (ludovicopapalia.com)",
        },
        method="POST",
    )

    print("\n[INDEXNOW] Invio richiesta POST...")

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            status = response.status
            body   = response.read().decode("utf-8", errors="replace")

            print(f"[INDEXNOW] Risposta HTTP: {status}")

            # Codici di risposta attesi secondo le specifiche IndexNow:
            # 200 → OK, URL accettati
            # 202 → Accepted (alcuni motori usano questo)
            # 400 → Invalid format
            # 403 → Forbidden — chiave non valida o file .txt non trovato sul sito
            # 422 → Unprocessable — URL non appartengono all'host dichiarato
            # 429 → Too Many Requests — quota superata, riprova più tardi
            if status in (200, 202):
                print("[INDEXNOW] ✓ Ping inviato con successo.")
                print("[INDEXNOW]   I motori supportati (Bing, Yandex, Naver, ecc.) ")
                print("[INDEXNOW]   ricrawleranno le pagine nelle prossime ore.")
            else:
                print(f"[INDEXNOW] ✗ Risposta inattesa: {status}")
                if body:
                    print(f"[INDEXNOW]   Body: {body[:500]}")

    except urllib.error.HTTPError as e:
        # Leggi il corpo dell'errore per diagnosticare il problema
        error_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        print(f"[INDEXNOW] ✗ Errore HTTP {e.code}: {e.reason}")
        if error_body:
            print(f"[INDEXNOW]   Dettaglio: {error_body[:500]}")
        # Suggerimenti per i codici di errore più comuni
        if e.code == 403:
            print("[INDEXNOW]   → Verifica che il file chiave sia raggiungibile:")
            print(f"[INDEXNOW]     {INDEXNOW_KEY_LOCATION}")
        elif e.code == 422:
            print("[INDEXNOW]   → Uno o più URL non appartengono all'host dichiarato.")
        elif e.code == 429:
            print("[INDEXNOW]   → Quota superata. Riprova più tardi.")

    except urllib.error.URLError as e:
        print(f"[INDEXNOW] ✗ Errore di rete: {e.reason}")
        print("[INDEXNOW]   Verifica la connessione internet e riprova.")

    except Exception as e:
        print(f"[INDEXNOW] ✗ Errore imprevisto: {type(e).__name__}: {e}")


def collect_urls_for_indexnow(files):
    """
    Costruisce la lista di URL assoluti da passare a IndexNow,
    partendo dai file HTML già raccolti per la sitemap.
    Applica la stessa normalizzazione usata in build_sitemap()
    (es. /index.html → BASE_URL/).
    """
    urls = []
    for abs_path in files:
        url_path = url_for_path(abs_path)
        if url_path == "/index.html":
            urls.append(BASE_URL + "/")
        else:
            urls.append(BASE_URL + url_path)
    return urls


def main():
    print("=" * 60)
    print("  generate_sitemap.py — Ludovico Papalia")
    print("=" * 60)
    print(f"  SITE_ROOT        : {SITE_ROOT}")
    print(f"  BASE_URL         : {BASE_URL}")
    print(f"  OUTPUT (standard): {OUTPUT_SITEMAP}")
    print(f"  OUTPUT (news)    : {OUTPUT_SITEMAP_NEWS}")
    print(f"  IndexNow         : {'ABILITATO' if INDEXNOW_ENABLED else 'disabilitato'}")
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

    # ── INDEXNOW ──────────────────────────────────────────────────────────────
    if INDEXNOW_ENABLED:
        url_list = collect_urls_for_indexnow(files)
        ping_indexnow(url_list)
    else:
        print("\n[INDEXNOW] Ping disabilitato (INDEXNOW_ENABLED = False).")

    print("\n──────────────────────────────────────────────────────")
    print("  Prossimi passi dopo aver caricato i file:")
    print("  1. Search Console → Sitemap → invia entrambe (per Google)")
    print("     https://search.google.com/search-console/sitemaps")
    print("  2. Publisher Center → verifica inclusione")
    print("     https://publishercenter.google.com")
    print("  3. IndexNow già inviato automaticamente ↑")
    print("──────────────────────────────────────────────────────")


if __name__ == "__main__":
    main()
