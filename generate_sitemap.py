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
NEWS SITEMAP — fonte automatica
──────────────────────────────────────────────────────────────────────
Gli articoli per sitemap-news.xml vengono estratti automaticamente da
divulgativi-index.html, leggendo l'array JS  var ARTICLES = [...].

Per aggiungere un articolo alla news sitemap è sufficiente aggiungerlo
a ARTICLES in divulgativi-index.html come al solito: nessun altro
intervento è necessario su questo script.

La data viene convertita da formato italiano (es. "Marzo 2026") a ISO 8601.
Poiché nell'indice il giorno esatto non è memorizzato, viene usato il
giorno 1 del mese. Il timezone segue la regola CET/CEST italiana:
mesi aprile-ottobre → +02:00, mesi novembre-marzo → +01:00.
──────────────────────────────────────────────────────────────────────
"""

import os
import re
import datetime
import json
import urllib.request
from xml.sax.saxutils import escape as xml_escape
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

# Path del file indice degli articoli divulgativi, relativo a SITE_ROOT
DIVULGATIVI_INDEX = "divulgativi-index.html"

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
INDEXNOW_KEY      = "acaa81d24b20e17ebf85f615e130e6f4"
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
# MAPPA MESI ITALIANI → numero mese
# ─────────────────────────────────────────────────────────────────────────────
MESI_IT = {
    "gennaio":   1,  "febbraio":  2,  "marzo":    3,
    "aprile":    4,  "maggio":    5,  "giugno":   6,
    "luglio":    7,  "agosto":    8,  "settembre":9,
    "ottobre":  10,  "novembre": 11,  "dicembre": 12,
}

# Mesi in cui vige l'ora legale italiana (CEST = UTC+2)
# Nota: la transizione è fine marzo/fine ottobre, ma per semplicità
# usiamo aprile-ottobre come CEST e novembre-marzo come CET.
MESI_CEST = {4, 5, 6, 7, 8, 9, 10}


def italian_date_to_iso(date_str: str) -> str:
    """
    Converte una stringa di data italiana tipo "Marzo 2026" in formato ISO 8601
    con timezone CET/CEST corretta. Usata solo come fallback se datePublished
    non è presente nell'HTML dell'articolo.

    Esempi:
        "Marzo 2026"    → "2026-03-01T00:00:00+01:00"
        "Aprile 2023"   → "2023-04-01T00:00:00+02:00"
        "Novembre 2024" → "2024-11-01T00:00:00+01:00"

    Se il parsing fallisce, restituisce la data odierna come fallback.
    """
    print(f"  [DATE] Fallback parsing data italiana: '{date_str}'")

    parts = date_str.strip().split()
    if len(parts) == 2:
        mese_str = parts[0].lower()
        anno_str = parts[1]
        mese_num = MESI_IT.get(mese_str)
        if mese_num and anno_str.isdigit():
            anno = int(anno_str)
            tz   = "+02:00" if mese_num in MESI_CEST else "+01:00"
            iso  = f"{anno:04d}-{mese_num:02d}-01T00:00:00{tz}"
            print(f"  [DATE] → {iso} (giorno 1, data approssimata)")
            return iso

    # Fallback finale: data odierna
    today = datetime.date.today()
    fallback = f"{today.isoformat()}T00:00:00+01:00"
    print(f"  [DATE] ATTENZIONE: parsing fallito per '{date_str}', uso data odierna: {fallback}")
    return fallback


def extract_date_published(abs_html: str) -> str | None:
    """
    Legge il file HTML dell'articolo ed estrae la data esatta da
    'datePublished' nel JSON-LD o nel meta itemprop.

    Fonti cercate in ordine di priorità:
      1. JSON-LD:     "datePublished": "YYYY-MM-DD"
      2. meta itemprop: <meta itemprop="datePublished" content="YYYY-MM-DD">

    Restituisce la data in formato ISO 8601 con timezone CET/CEST corretta
    (es. "2026-03-19T00:00:00+01:00"), oppure None se non trovata.
    """
    try:
        with open(abs_html, "r", encoding="utf-8") as f:
            html = f.read()
    except OSError as e:
        print(f"  [DATE] Impossibile leggere {abs_html}: {e}")
        return None

    # Prova 1: JSON-LD  "datePublished": "2026-03-19"
    # Cattura sia date con che senza ora (YYYY-MM-DD oppure YYYY-MM-DDTHH:MM:SS...)
    match = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', html)
    if match:
        date_part = match.group(1)   # es. "2026-03-19"
        print(f"  [DATE] datePublished trovato nel JSON-LD: {date_part}")
    else:
        # Prova 2: <meta itemprop="datePublished" content="2026-03-19">
        match = re.search(
            r'<meta\s[^>]*itemprop=["\']datePublished["\'][^>]*content=["\'](\d{4}-\d{2}-\d{2})',
            html,
            re.IGNORECASE,
        )
        if not match:
            # Prova 2b: ordine attributi invertito (content prima di itemprop)
            match = re.search(
                r'<meta\s[^>]*content=["\'](\d{4}-\d{2}-\d{2})["\'][^>]*itemprop=["\']datePublished["\']',
                html,
                re.IGNORECASE,
            )
        if match:
            date_part = match.group(1)
            print(f"  [DATE] datePublished trovato nel meta itemprop: {date_part}")
        else:
            print(f"  [DATE] datePublished non trovato in {os.path.basename(abs_html)}")
            return None

    # Aggiunge timezone CET/CEST in base al mese
    # Formato atteso: "YYYY-MM-DD"
    try:
        mese_num = int(date_part[5:7])
        tz = "+02:00" if mese_num in MESI_CEST else "+01:00"
        iso = f"{date_part}T00:00:00{tz}"
        print(f"  [DATE] → {iso}")
        return iso
    except (ValueError, IndexError) as e:
        print(f"  [DATE] Errore parsing '{date_part}': {e}")
        return None


def parse_articles_from_index() -> list[dict]:
    """
    Legge divulgativi-index.html ed estrae automaticamente gli articoli
    dall'array JS  var ARTICLES = [...].

    Restituisce una lista di dizionari con chiavi:
        path   — percorso relativo al file HTML (es. "art-divulgativi/foo.html")
        title  — titolo dell'articolo
        date   — data ISO 8601 con timezone

    La funzione usa regex per estrarre i campi dal codice JS, che non è
    JSON valido (virgole finali, apostrofi nei valori, ecc.), quindi non
    si può usare json.loads() direttamente.
    """
    index_path = os.path.join(SITE_ROOT, DIVULGATIVI_INDEX)
    print(f"\n[NEWS] Lettura articoli da: {index_path}")

    if not os.path.isfile(index_path):
        print(f"[NEWS] ERRORE: file non trovato → {index_path}")
        return []

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Estrai il blocco dell'array ARTICLES dal JS inline.
    # Il pattern cattura tutto tra "var ARTICLES = [" e il ";" che chiude
    # l'array, attraverso multiple righe.
    array_match = re.search(
        r'var\s+ARTICLES\s*=\s*\[(.*?)\]\s*;',
        html,
        re.DOTALL
    )
    if not array_match:
        print("[NEWS] ERRORE: array ARTICLES non trovato in divulgativi-index.html")
        print("       Verifica che la sintassi  var ARTICLES = [...]  sia presente.")
        return []

    array_body = array_match.group(1)
    print(f"[NEWS] Blocco ARTICLES trovato ({len(array_body)} caratteri).")

    # Estrai i singoli oggetti { ... } dall'array.
    # Usiamo una regex che cattura il contenuto tra { e } per ogni entry.
    entries_raw = re.findall(r'\{([^}]+)\}', array_body, re.DOTALL)
    print(f"[NEWS] Entry grezze trovate: {len(entries_raw)}")

    articles = []
    for i, entry_raw in enumerate(entries_raw):
        print(f"\n[NEWS] Entry #{i+1}:")
        print(f"  [RAW] {entry_raw.strip()[:120]}...")

        # Estrai i singoli campi con regex flessibili che gestiscono
        # sia apici singoli che doppi, e virgole finali.
        # Campo "date" — es.  date:  "Marzo 2026",  oppure  date: 'Aprile 2023'
        date_match = re.search(r'date\s*:\s*["\']([^"\']+)["\']', entry_raw)

        # Campo "title"
        # Fix apostrofi JS-escaped (es. l\'Europa): regex con backreference per riconoscere \. come token singolo
        title_match = re.search(r'title\s*:\s*(["\'])((?:[^\\]|\\.)*?)\1', entry_raw, re.DOTALL)

        # Campo "href" — es.  href:  "/art-divulgativi/foo.html"
        href_match  = re.search(r'href\s*:\s*["\']([^"\']+)["\']', entry_raw)

        # Se manca uno dei campi obbligatori, salta l'entry con avviso
        if not all([date_match, title_match, href_match]):
            missing = []
            if not date_match:  missing.append("date")
            if not title_match: missing.append("title")
            if not href_match:  missing.append("href")
            print(f"  [SKIP] Campi mancanti: {missing} — entry ignorata.")
            continue

        date_raw = date_match.group(1).strip()
        # group(2) perché il nuovo regex ha il delimitatore come gruppo 1
        # re.sub risolve le sequenze escape JS: \' → '  \" → "  \\ → \
        title    = re.sub(r'\\(.)', r'\1', title_match.group(2).strip())
        href     = href_match.group(1).strip()

        # Converti href ("/art-divulgativi/foo.html") in path relativo
        # rimuovendo lo slash iniziale per coerenza con SITE_ROOT
        path = href.lstrip("/")

        # Verifica che il file HTML esista realmente su disco.
        # Questo filtra automaticamente le entry segnaposto del template
        # (es. href="/art-divulgativi/nome-articolo.html") senza richiedere
        # nessuna gestione manuale.
        abs_html = os.path.join(SITE_ROOT, path)
        if not os.path.isfile(abs_html):
            print(f"  [SKIP] File non trovato su disco → {path} (entry template o link errato)")
            continue

        # Fonte primaria: legge datePublished dal JSON-LD/meta dell'articolo stesso.
        # È il giorno esatto già presente negli header SEO di ogni pagina.
        # Fallback: parsing della data italiana dall'indice (giorno 1 del mese).
        date_iso = extract_date_published(abs_html)
        if date_iso is None:
            print(f"  [DATE] Fallback su data italiana dall'indice: '{date_raw}'")
            date_iso = italian_date_to_iso(date_raw)

        articles.append({
            "path":  path,
            "title": title,
            "date":  date_iso,
        })
        print(f"  [OK]  title={title[:60]!r}")
        print(f"        path={path}")
        print(f"        date={date_iso}")

    print(f"\n[NEWS] Articoli estratti con successo: {len(articles)}")
    return articles


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
    la lista dei file HTML da includere nella sitemap standard.
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


def build_sitemap_news(news_articles: list[dict]) -> str:
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
    lines.append('  Fonte: divulgativi-index.html (array ARTICLES)')
    lines.append('  Ref: https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap')
    lines.append('-->')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
    lines.append('        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">')

    for article in news_articles:
        full_url = BASE_URL + "/" + article["path"].lstrip("/")

        # Escape caratteri XML nel titolo
        # xml_escape gestisce &, <, > (i soli obbligatori nei contenuti elemento XML)
        # Gli apostrofi nei contenuti elemento non richiedono escaping — li lasciamo UTF-8
        # per massima leggibilità e compatibilità con tutti i crawler news
        title_safe = xml_escape(article["title"])

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
    print(f"[NEWS] Totale articoli: {len(news_articles)}")
    return "\n".join(lines)


def ping_indexnow(url_list: list[str]) -> None:
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
        error_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        print(f"[INDEXNOW] ✗ Errore HTTP {e.code}: {e.reason}")
        if error_body:
            print(f"[INDEXNOW]   Dettaglio: {error_body[:500]}")
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


def collect_urls_for_indexnow(files: list[str]) -> list[str]:
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
    # Estrai gli articoli automaticamente da divulgativi-index.html
    news_articles = parse_articles_from_index()

    if not news_articles:
        print("[AVVISO] Nessun articolo estratto. sitemap-news.xml non verrà aggiornata.")
    else:
        xml_news = build_sitemap_news(news_articles)
        with open(OUTPUT_SITEMAP_NEWS, "w", encoding="utf-8") as f:
            f.write(xml_news)
        print(f"[DONE]  sitemap-news.xml salvata: {len(news_articles)} articoli inclusi.")

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

