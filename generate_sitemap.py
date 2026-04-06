#!/usr/bin/env python3
"""
generate_sitemap.py
-------------------
Scansiona una cartella locale del sito e genera due file:
  - sitemap.xml        (sitemap standard per Googlebot e tutti i crawler)
  - sitemap-news.xml   (Google News sitemap, solo articoli divulgativi)

Alla fine, notifica automaticamente IndexNow con i soli URL HTML
effettivamente modificati dall'ultima esecuzione, in modo che Bing,
Yandex, Naver e altri motori ricrawlino solo le pagine che contano.

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

──────────────────────────────────────────────────────────────────────
CHANGE TRACKING — come funziona
──────────────────────────────────────────────────────────────────────
Ad ogni esecuzione lo script salva in sitemap-state.json un dizionario:
  { "percorso/relativo.html": "sha256hex", ... }

Al run successivo confronta l'hash attuale con quello salvato.
Solo i file con hash diverso (o nuovi) vengono inviati a IndexNow.
Questo è il comportamento corretto del protocollo: si notificano
esclusivamente le pagine che sono state realmente modificate.

Il file sitemap-state.json non va in sitemap.xml (è in EXCLUDE_FILES)
e può essere committato nel repo senza problemi: non contiene segreti.
──────────────────────────────────────────────────────────────────────
"""

import os
import re
import hashlib
import datetime
import json
import urllib.request
from xml.sax.saxutils import escape as xml_escape
import urllib.error

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG — modifica questi valori prima di eseguire
# ─────────────────────────────────────────────────────────────────────────────

# Cartella radice del sito: si posiziona automaticamente dove si trova questo script.
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))

# Dominio base (senza slash finale)
BASE_URL = "https://www.ludovicopapalia.com"

# Nome della testata per la News sitemap
NEWS_PUBLICATION_NAME = "Ludovico Papalia — Diritto Informatico"
NEWS_LANGUAGE = "it"

# Path del file indice degli articoli divulgativi, relativo a SITE_ROOT
DIVULGATIVI_INDEX = "divulgativi-index.html"

# ─────────────────────────────────────────────────────────────────────────────
# INDEXNOW CONFIG
# ─────────────────────────────────────────────────────────────────────────────
INDEXNOW_KEY          = "acaa81d24b20e17ebf85f615e130e6f4"
INDEXNOW_ENDPOINT     = "https://api.indexnow.org/indexnow"
INDEXNOW_KEY_LOCATION = f"{BASE_URL}/{INDEXNOW_KEY}.txt"

# Se True, invia il ping IndexNow al termine dello script.
INDEXNOW_ENABLED = True

# File dove viene salvato lo stato degli hash per il change tracking.
# Non va incluso in sitemap.xml (è in EXCLUDE_FILES qui sotto).
STATE_FILE = os.path.join(SITE_ROOT, "sitemap-state.json")

# File da escludere sempre (nomi esatti, case-sensitive)
EXCLUDE_FILES = {
    "404.html",
    "sitemap.xml",
    "sitemap-news.xml",
    "sitemap-state.json",       # file di stato interno, non è una pagina
    "robots.txt",
    "llms.txt",
    "divulgativo-template.html",
    "paper-template.html",
    "UNUSED-papers-index.html",
    # Pagine escluse per coerenza con robots.txt Disallow
    "chi-sono.html",
}

# Cartelle da escludere (nomi, non path completi)
EXCLUDE_DIRS = {
    ".git",
    ".github",
    "node_modules",
    "assets",
    "cdn-cgi",
    # Cartelle escluse per coerenza con robots.txt Disallow
    "curriculum",
}

# Estensioni da includere nella sitemap standard
INCLUDE_EXTENSIONS = {".html", ".htm"}

# Dove salvare le sitemap generate
OUTPUT_SITEMAP      = os.path.join(SITE_ROOT, "sitemap.xml")
OUTPUT_SITEMAP_NEWS = os.path.join(SITE_ROOT, "sitemap-news.xml")

# ─────────────────────────────────────────────────────────────────────────────
# RSS FEED CONFIG
# ─────────────────────────────────────────────────────────────────────────────

# Percorso di output del feed RSS 2.0
OUTPUT_RSS = os.path.join(SITE_ROOT, "feed.xml")

# URL pubblico del feed (usato nel tag <atom:link> e nei log)
RSS_FEED_URL = f"{BASE_URL}/feed.xml"

# Metadati del canale RSS
RSS_CHANNEL_TITLE       = "Ludovico Papalia — Articoli divulgativi"
RSS_CHANNEL_DESCRIPTION = (
    "Diritto informatico, blockchain, privacy e AI spiegati senza fronzoli. "
    "Articoli divulgativi di Ludovico Papalia."
)
RSS_CHANNEL_LANGUAGE    = "it"
# Immagine del canale RSS (mostrata da alcuni reader)
RSS_CHANNEL_IMAGE_URL   = f"{BASE_URL}/assets/og-default.jpg"


# ─────────────────────────────────────────────────────────────────────────────
# RSS FEED CONFIG
# ─────────────────────────────────────────────────────────────────────────────

# Percorso di output del feed RSS 2.0
OUTPUT_RSS = os.path.join(SITE_ROOT, "feed.xml")

# URL pubblico del feed (usato nel tag <atom:link> e nei log)
RSS_FEED_URL = f"{BASE_URL}/feed.xml"

# Metadati del canale RSS
RSS_CHANNEL_TITLE       = "Ludovico Papalia — Articoli divulgativi"
RSS_CHANNEL_DESCRIPTION = (
    "Diritto informatico, blockchain, privacy e AI spiegati senza fronzoli. "
    "Articoli divulgativi di Ludovico Papalia."
)
RSS_CHANNEL_LANGUAGE    = "it"
RSS_CHANNEL_IMAGE_URL   = f"{BASE_URL}/assets/rss-logo.png"   # 144x144px, crop quadrato da profile.png

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
MESI_CEST = {4, 5, 6, 7, 8, 9, 10}


# ─────────────────────────────────────────────────────────────────────────────
# CHANGE TRACKING
# ─────────────────────────────────────────────────────────────────────────────

def sha256_of_file(abs_path: str) -> str:
    """
    Calcola lo SHA-256 del contenuto di un file.
    Restituisce l'hex digest (64 caratteri).
    Usato per rilevare modifiche reali al contenuto, indipendentemente
    dalla data di modifica del filesystem (che può cambiare con un clone git).
    """
    h = hashlib.sha256()
    # Legge il file a blocchi per non saturare la RAM su file grandi
    with open(abs_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_state() -> dict:
    """
    Carica il dizionario di stato da sitemap-state.json.
    Formato: { "percorso/relativo.html": "sha256hex", ... }
    Restituisce un dict vuoto se il file non esiste (primo run).
    """
    if not os.path.isfile(STATE_FILE):
        print("[STATE] sitemap-state.json non trovato — primo run, tutti i file saranno inviati.")
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        print(f"[STATE] Stato caricato: {len(state)} file tracciati.")
        return state
    except (json.JSONDecodeError, OSError) as e:
        print(f"[STATE] ERRORE lettura stato: {e} — si riparte da zero.")
        return {}


def save_state(state: dict) -> None:
    """
    Salva il dizionario di stato aggiornato in sitemap-state.json.
    Sovrascrive il file precedente.
    """
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"[STATE] Stato salvato: {len(state)} file tracciati → {STATE_FILE}")
    except OSError as e:
        print(f"[STATE] ERRORE salvataggio stato: {e}")


def detect_changed_files(files: list[str], old_state: dict) -> tuple[list[str], dict]:
    """
    Confronta i file attuali con lo stato salvato e restituisce:
      - changed_files : lista di percorsi assoluti dei file modificati o nuovi
      - new_state     : dizionario aggiornato con tutti gli hash attuali

    Un file è considerato "modificato" se:
      - non è presente nel vecchio stato (file nuovo)
      - il suo SHA-256 è diverso da quello salvato (contenuto cambiato)

    I file rimossi vengono silenziosamente esclusi dal nuovo stato
    (non vengono notificati a IndexNow perché non esistono più).
    """
    print("\n[TRACK] Calcolo hash e rilevamento modifiche...")
    new_state   = {}
    changed     = []

    for abs_path in files:
        # Calcola il percorso relativo per usarlo come chiave nello stato
        rel_path = os.path.relpath(abs_path, SITE_ROOT).replace("\\", "/")

        current_hash = sha256_of_file(abs_path)
        new_state[rel_path] = current_hash

        old_hash = old_state.get(rel_path)

        if old_hash is None:
            print(f"  [NEW]      {rel_path}  (hash: {current_hash[:12]}...)")
            changed.append(abs_path)
        elif old_hash != current_hash:
            print(f"  [CHANGED]  {rel_path}  ({old_hash[:12]}... → {current_hash[:12]}...)")
            changed.append(abs_path)
        else:
            print(f"  [unchanged] {rel_path}")

    print(f"\n[TRACK] File modificati / nuovi: {len(changed)} su {len(files)} totali.")
    return changed, new_state


# ─────────────────────────────────────────────────────────────────────────────
# DATE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def italian_date_to_iso(date_str: str) -> str:
    """
    Converte una stringa di data italiana tipo "Marzo 2026" in formato ISO 8601
    con timezone CET/CEST corretta. Usata solo come fallback se datePublished
    non è presente nell'HTML dell'articolo.
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

    today    = datetime.date.today()
    fallback = f"{today.isoformat()}T00:00:00+01:00"
    print(f"  [DATE] ATTENZIONE: parsing fallito per '{date_str}', uso data odierna: {fallback}")
    return fallback


def extract_date_published(abs_html: str) -> str | None:
    """
    Legge il file HTML dell'articolo ed estrae la data esatta da
    'datePublished' nel JSON-LD o nel meta itemprop.
    Restituisce la data in formato ISO 8601 con timezone, oppure None.
    """
    try:
        with open(abs_html, "r", encoding="utf-8") as f:
            html = f.read()
    except OSError as e:
        print(f"  [DATE] Impossibile leggere {abs_html}: {e}")
        return None

    match = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', html)
    if match:
        date_part = match.group(1)
        print(f"  [DATE] datePublished trovato nel JSON-LD: {date_part}")
    else:
        match = re.search(
            r'<meta\s[^>]*itemprop=["\']datePublished["\'][^>]*content=["\'](\d{4}-\d{2}-\d{2})',
            html, re.IGNORECASE,
        )
        if not match:
            match = re.search(
                r'<meta\s[^>]*content=["\'](\d{4}-\d{2}-\d{2})["\'][^>]*itemprop=["\']datePublished["\']',
                html, re.IGNORECASE,
            )
        if match:
            date_part = match.group(1)
            print(f"  [DATE] datePublished trovato nel meta itemprop: {date_part}")
        else:
            print(f"  [DATE] datePublished non trovato in {os.path.basename(abs_html)}")
            return None

    try:
        mese_num = int(date_part[5:7])
        tz  = "+02:00" if mese_num in MESI_CEST else "+01:00"
        iso = f"{date_part}T00:00:00{tz}"
        print(f"  [DATE] → {iso}")
        return iso
    except (ValueError, IndexError) as e:
        print(f"  [DATE] Errore parsing '{date_part}': {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# NEWS SITEMAP — parsing articoli da divulgativi-index.html
# ─────────────────────────────────────────────────────────────────────────────

def parse_articles_from_index() -> list[dict]:
    """
    Legge divulgativi-index.html ed estrae automaticamente gli articoli
    dall'array JS  var ARTICLES = [...].
    Restituisce una lista di dizionari con chiavi: path, title, date.
    """
    index_path = os.path.join(SITE_ROOT, DIVULGATIVI_INDEX)
    print(f"\n[NEWS] Lettura articoli da: {index_path}")

    if not os.path.isfile(index_path):
        print(f"[NEWS] ERRORE: file non trovato → {index_path}")
        return []

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    array_match = re.search(r'var\s+ARTICLES\s*=\s*\[(.*?)\]\s*;', html, re.DOTALL)
    if not array_match:
        print("[NEWS] ERRORE: array ARTICLES non trovato in divulgativi-index.html")
        return []

    array_body = array_match.group(1)
    print(f"[NEWS] Blocco ARTICLES trovato ({len(array_body)} caratteri).")

    entries_raw = re.findall(r'\{([^}]+)\}', array_body, re.DOTALL)
    print(f"[NEWS] Entry grezze trovate: {len(entries_raw)}")

    articles = []
    for i, entry_raw in enumerate(entries_raw):
        print(f"\n[NEWS] Entry #{i+1}:")
        print(f"  [RAW] {entry_raw.strip()[:120]}...")

        date_match  = re.search(r'date\s*:\s*["\']([^"\']+)["\']', entry_raw)
        title_match = re.search(r'title\s*:\s*(["\'])((?:[^\\]|\\.)*?)\1', entry_raw, re.DOTALL)
        href_match  = re.search(r'href\s*:\s*["\']([^"\']+)["\']', entry_raw)

        if not all([date_match, title_match, href_match]):
            missing = []
            if not date_match:  missing.append("date")
            if not title_match: missing.append("title")
            if not href_match:  missing.append("href")
            print(f"  [SKIP] Campi mancanti: {missing} — entry ignorata.")
            continue

        date_raw = date_match.group(1).strip()
        title    = re.sub(r'\\(.)', r'\1', title_match.group(2).strip())
        href     = href_match.group(1).strip()
        path     = href.lstrip("/")

        abs_html = os.path.join(SITE_ROOT, path)
        if not os.path.isfile(abs_html):
            print(f"  [SKIP] File non trovato su disco → {path} (entry template o link errato)")
            continue

        date_iso = extract_date_published(abs_html)
        if date_iso is None:
            print(f"  [DATE] Fallback su data italiana dall'indice: '{date_raw}'")
            date_iso = italian_date_to_iso(date_raw)

        articles.append({"path": path, "title": title, "date": date_iso})
        print(f"  [OK]  title={title[:60]!r}")
        print(f"        path={path}")
        print(f"        date={date_iso}")

    print(f"\n[NEWS] Articoli estratti con successo: {len(articles)}")
    return articles


# ─────────────────────────────────────────────────────────────────────────────
# RSS FEED — generazione feed.xml RSS 2.0
# ─────────────────────────────────────────────────────────────────────────────

def extract_meta_description(abs_html: str) -> str:
    """
    Estrae il contenuto del tag <meta name="description"> da un file HTML.
    Restituisce la stringa trovata, oppure una stringa vuota se non presente.

    La priorità è:
      1. <meta name="description" content="...">
      2. <meta property="og:description" content="...">  (fallback)
    """
    try:
        with open(abs_html, "r", encoding="utf-8") as f:
            html = f.read()
    except OSError as e:
        print(f"  [RSS] Impossibile leggere {abs_html}: {e}")
        return ""

    # Priorità 1: meta name="description"
    # FIX (apostrophe bug): usa backreference sul delimitatore di apertura del valore
    # dell'attributo, in modo che apostrofi nel testo (es. "sull'architettura")
    # non troncino il match. Gestisce entrambi gli ordini degli attributi.
    match = re.search(
        r'<meta\s[^>]*\bname=(?P<q1>["\'])description(?P=q1)[^>]*\bcontent=(?P<q2>["\'])(.*?)(?P=q2)',
        html, re.IGNORECASE | re.DOTALL,
    )
    if match:
        desc = match.group(3).strip()
        print(f"  [RSS] meta description trovata ({len(desc)} chars).")
        return desc

    match = re.search(
        r'<meta\s[^>]*\bcontent=(?P<q2>["\'])(.*?)(?P=q2)[^>]*\bname=(?P<q1>["\'])description(?P=q1)',
        html, re.IGNORECASE | re.DOTALL,
    )
    if match:
        desc = match.group(2).strip()
        print(f"  [RSS] meta description (content-first) trovata ({len(desc)} chars).")
        return desc

    # Fallback: og:description
    match = re.search(
        r'<meta\s[^>]*\bproperty=(?P<q1>["\'])og:description(?P=q1)[^>]*\bcontent=(?P<q2>["\'])(.*?)(?P=q2)',
        html, re.IGNORECASE | re.DOTALL,
    )
    if match:
        desc = match.group(3).strip()
        print(f"  [RSS] Fallback og:description ({len(desc)} chars).")
        return desc

        print(f"  [RSS] AVVISO: nessuna description trovata in {os.path.basename(abs_html)}.")
    return ""


def extract_og_image(abs_html: str) -> str:
    """
    Estrae l'URL dell'immagine og:image dall'HTML dell'articolo.
    Restituisce l'URL assoluto se trovato, stringa vuota altrimenti.
    FIX: usa backreference per non troncare URL con apostrofo nel percorso.
    """
    try:
        with open(abs_html, "r", encoding="utf-8") as f:
            html = f.read()
    except OSError:
        return ""

    match = re.search(
        r'<meta\s[^>]*\bproperty=(?P<q1>["\'])og:image(?P=q1)[^>]*\bcontent=(?P<q2>["\'])(.*?)(?P=q2)',
        html, re.IGNORECASE | re.DOTALL,
    )
    if not match:
        match = re.search(
            r'<meta\s[^>]*\bcontent=(?P<q2>["\'])(.*?)(?P=q2)[^>]*\bproperty=(?P<q1>["\'])og:image(?P=q1)',
            html, re.IGNORECASE | re.DOTALL,
        )
        if match:
            img = match.group(2).strip()
            if img.startswith("/"):
                img = BASE_URL + img
            return img

    if match:
        img = match.group(3).strip()
        if img.startswith("/"):
            img = BASE_URL + img
        return img

    return ""

def format_rfc2822(iso_date: str) -> str:
    """
    Converte una data ISO 8601 (es. '2025-12-15T00:00:00+01:00') in formato
    RFC 2822 richiesto da RSS 2.0 (es. 'Sun, 15 Dec 2025 00:00:00 +0100').
    Accetta anche solo la parte YYYY-MM-DD.
    """
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            date_str_clean = iso_date
            if len(iso_date) > 19 and iso_date[19] in ("+", "-"):
                # Rimuove il ':' in +01:00 -> +0100 per compatibilità Python
                date_str_clean = iso_date[:22] + iso_date[23:]
            dt = datetime.datetime.strptime(date_str_clean, fmt)
            return dt.strftime("%a, %d %b %Y %H:%M:%S %z") if dt.tzinfo else \
                   dt.strftime("%a, %d %b %Y %H:%M:%S ") + tz_offset
        except ValueError:
            continue

    print(f"  [RSS] AVVISO: impossibile convertire data '{iso_date}' in RFC 2822, uso fallback.")
    return datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0100")


def build_rss_feed(articles: list[dict]) -> str:
    """
    Genera il contenuto XML del feed RSS 2.0 completo.

    Ogni <item> contiene:
      - <title>        : titolo dell'articolo
      - <link>         : URL canonico
      - <guid>         : stesso dell'URL (isPermaLink="true")
      - <pubDate>      : data RFC 2822
      - <description>  : meta description estratta dall'HTML
      - <enclosure>    : immagine og:image se disponibile

    Il canale include:
      - <atom:link rel="self">  per autodescription del feed
      - <lastBuildDate>         : timestamp di generazione
      - <image>                 : immagine del canale

    Gli articoli sono ordinati come in ARTICLES (più recente prima).
    """
    print("\n[RSS] Generazione feed.xml RSS 2.0...")

    # FIX: ordina per data ISO 8601 descrescente (più recente prima)
    # indipendentemente dall'ordine in ARTICLES in divulgativi-index.html
    articles_sorted = sorted(articles, key=lambda a: a["date"], reverse=True)
    print(f"[RSS] Articoli ordinati per data: {len(articles_sorted)} item")

    # FIX: lastBuildDate con timezone corretta (CET/CEST italiana)
    tz_offset = "+0200" if datetime.datetime.now().month in {4,5,6,7,8,9,10} else "+0100"
    now_rfc_tz = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S ") + tz_offset

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!-- ================================================================',
        '     feed.xml — RSS 2.0 — ludovicopapalia.com',
        '     Generato automaticamente da generate_sitemap.py',
        '     Fonte: divulgativi-index.html (array ARTICLES)',
        '     Aggiornato ad ogni esecuzione dello script.',
        '================================================================ -->',
        '<rss version="2.0"',
        '     xmlns:atom="http://www.w3.org/2005/Atom"',
        '     xmlns:content="http://purl.org/rss/1.0/modules/content/"',
        '     xmlns:dc="http://purl.org/dc/elements/1.1/">',
        '',
        '  <channel>',
        f'    <title>{xml_escape(RSS_CHANNEL_TITLE)}</title>',
        f'    <link>{BASE_URL}/divulgativi-index.html</link>',
        f'    <description>{xml_escape(RSS_CHANNEL_DESCRIPTION)}</description>',
        f'    <language>{RSS_CHANNEL_LANGUAGE}</language>',
        f'    <lastBuildDate>{now_rfc_tz}</lastBuildDate>',
        f'    <generator>generate_sitemap.py (ludovicopapalia.com)</generator>',
        f'    <docs>https://www.rssboard.org/rss-specification</docs>',
        f'    <atom:link href="{RSS_FEED_URL}" rel="self" type="application/rss+xml"/>',
        '    <image>',
        f'      <url>{RSS_CHANNEL_IMAGE_URL}</url>',
        f'      <title>{xml_escape(RSS_CHANNEL_TITLE)}</title>',
        f'      <link>{BASE_URL}/divulgativi-index.html</link>',
        '    </image>',
        # TTL: suggerisce ai reader di ricontrollare ogni 60 minuti
        '    <ttl>60</ttl>',
        '',
    ]

    items_written = 0
    for article in articles_sorted:
        full_url = BASE_URL + "/" + article["path"].lstrip("/")
        abs_html = os.path.join(SITE_ROOT, article["path"])
        pub_date = format_rfc2822(article["date"])
        desc     = extract_meta_description(abs_html)

        print(f"  [RSS] item: {article['title'][:60]!r} | {pub_date}")

        lines += [
            '    <item>',
            f'      <title>{xml_escape(article["title"])}</title>',
            f'      <link>{full_url}</link>',
            f'      <guid isPermaLink="true">{full_url}</guid>',
            f'      <pubDate>{pub_date}</pubDate>',
            f'      <dc:creator>Ludovico Papalia</dc:creator>',
        ]

        if desc:
            lines.append(f'      <description>{xml_escape(desc)}</description>')
        else:
            lines.append(f'      <description>{xml_escape(article["title"])}</description>')


        lines += [
            '    </item>',
            '',
        ]
        items_written += 1

    lines += [
        '  </channel>',
        '</rss>',
    ]

    print(f"[RSS] Item scritti nel feed: {items_written}")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# SITEMAP HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def url_for_path(abs_path: str) -> str:
    """Converte un percorso assoluto in URL relativa alla root del sito."""
    rel = os.path.relpath(abs_path, SITE_ROOT).replace("\\", "/")
    if not rel.startswith("/"):
        rel = "/" + rel
    return rel


def get_lastmod(abs_path: str) -> str:
    """
    Restituisce la data di ultima modifica del file in formato W3C (YYYY-MM-DD).

    Per gli articoli HTML cerca prima il campo 'datePublished' nel JSON-LD
    (che riflette la data di pubblicazione reale, non il mtime del filesystem).
    Il mtime è inaffidabile su git clone perché tutti i file risultano
    modificati nello stesso momento (quello del clone).
    Fallback: mtime del filesystem.
    """
    # Prova a estrarre datePublished dal JSON-LD (articoli divulgativi e paper)
    if abs_path.endswith(".html"):
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            # Cerca datePublished nel JSON-LD o nei meta itemprop
            match = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', html_content)
            if not match:
                match = re.search(
                    r'<meta\s[^>]*itemprop=["\'\']datePublished["\'\'][^>]*content=["\'\']'
                    r'(\d{4}-\d{2}-\d{2})', html_content, re.IGNORECASE
                )
            if match:
                date_str = match.group(1)
                print(f"  [LASTMOD] datePublished trovato: {date_str} ({os.path.basename(abs_path)})")
                return date_str
        except (OSError, Exception):
            pass
    # Fallback: mtime del filesystem
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
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for abs_path in sorted(files):
        url_path   = url_for_path(abs_path)
        full_url   = BASE_URL + ("/" if url_path == "/index.html" else url_path)
        lastmod    = get_lastmod(abs_path)
        priority   = PRIORITY_MAP.get(url_path, "0.5")
        changefreq = CHANGEFREQ_MAP.get(url_path, DEFAULT_CHANGEFREQ)

        lines += [
            "  <url>",
            f"    <loc>{full_url}</loc>",
            f"    <lastmod>{lastmod}</lastmod>",
            f"    <changefreq>{changefreq}</changefreq>",
            f"    <priority>{priority}</priority>",
            "  </url>",
        ]
        print(f"[ENTRY] {full_url}  |  lastmod={lastmod}  |  priority={priority}")

    lines.append("</urlset>")
    return "\n".join(lines)


def build_sitemap_news(news_articles: list[dict]) -> str:
    """Genera il contenuto XML della Google News sitemap."""
    print("\n[NEWS] Generazione sitemap-news.xml...")
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!--',
        '  sitemap-news.xml — ludovicopapalia.com',
        '  Google News sitemap (namespace news:).',
        '  Aggiornata automaticamente da generate_sitemap.py',
        '  Fonte: divulgativi-index.html (array ARTICLES)',
        '  Ref: https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap',
        '-->',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">',
    ]
    for article in news_articles:
        full_url   = BASE_URL + "/" + article["path"].lstrip("/")
        title_safe = xml_escape(article["title"])
        lines += [
            "  <url>",
            f"    <loc>{full_url}</loc>",
            "    <news:news>",
            "      <news:publication>",
            f"        <news:name>{NEWS_PUBLICATION_NAME}</news:name>",
            f"        <news:language>{NEWS_LANGUAGE}</news:language>",
            "      </news:publication>",
            f"      <news:publication_date>{article['date']}</news:publication_date>",
            f"      <news:title>{title_safe}</news:title>",
            "    </news:news>",
            "  </url>",
        ]
        print(f"  [NEWS] {full_url}  |  date={article['date']}")

    lines.append("</urlset>")
    print(f"[NEWS] Totale articoli: {len(news_articles)}")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# INDEXNOW
# ─────────────────────────────────────────────────────────────────────────────

def collect_urls_for_indexnow(changed_files: list[str]) -> list[str]:
    """
    Converte i percorsi assoluti dei file modificati in URL assoluti
    da passare a IndexNow. Applica la stessa normalizzazione di build_sitemap().
    """
    urls = []
    for abs_path in changed_files:
        url_path = url_for_path(abs_path)
        urls.append(BASE_URL + ("/" if url_path == "/index.html" else url_path))
    return urls


def ping_indexnow(url_list: list[str]) -> None:
    """
    Invia una notifica IndexNow con la lista degli URL modificati.

    Il protocollo IndexNow è supportato da: Bing, Yandex, Naver, Seznam, Yep.
    Inviando a api.indexnow.org il ping viene automaticamente redistribuito
    a tutti i motori partecipanti — una sola chiamata è sufficiente.

    IMPORTANTE: vengono inviati SOLO gli URL delle pagine effettivamente
    cambiate dall'ultima esecuzione (change tracking via SHA-256).
    Questo rispetta le specifiche del protocollo e preserva la quota.

    Google NON supporta IndexNow: per Google valgono sitemap + Search Console.
    """
    if not url_list:
        print("\n[INDEXNOW] Nessuna pagina modificata — ping non necessario. ✓")
        return

    print("\n" + "─" * 60)
    print("[INDEXNOW] Preparazione ping...")
    print(f"[INDEXNOW] Endpoint   : {INDEXNOW_ENDPOINT}")
    print(f"[INDEXNOW] Host       : {BASE_URL.replace('https://', '')}")
    print(f"[INDEXNOW] Key        : {INDEXNOW_KEY}")
    print(f"[INDEXNOW] Key file   : {INDEXNOW_KEY_LOCATION}")
    print(f"[INDEXNOW] URL modificati da notificare: {len(url_list)}")
    for u in url_list:
        print(f"  → {u}")

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
            "User-Agent":   "generate_sitemap.py/2.0 (ludovicopapalia.com)",
        },
        method="POST",
    )

    print("\n[INDEXNOW] Invio richiesta POST...")
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            status = response.status
            body   = response.read().decode("utf-8", errors="replace")
            print(f"[INDEXNOW] Risposta HTTP: {status}")
            if status in (200, 202):
                print("[INDEXNOW] ✓ Ping inviato con successo.")
                print("[INDEXNOW]   I motori supportati (Bing, Yandex, Naver, ecc.)")
                print("[INDEXNOW]   ricrawleranno le pagine modificate nelle prossime ore.")
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
            print(f"[INDEXNOW]   → Verifica che il file chiave sia raggiungibile:")
            print(f"[INDEXNOW]     {INDEXNOW_KEY_LOCATION}")
        elif e.code == 422:
            print("[INDEXNOW]   → Uno o più URL non appartengono all'host dichiarato.")
        elif e.code == 429:
            print("[INDEXNOW]   → Quota superata. Riprova più tardi.")

    except urllib.error.URLError as e:
        print(f"[INDEXNOW] ✗ Errore di rete: {e.reason}")

    except Exception as e:
        print(f"[INDEXNOW] ✗ Errore imprevisto: {type(e).__name__}: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  generate_sitemap.py v2.0 — Ludovico Papalia")
    print("=" * 60)
    print(f"  SITE_ROOT        : {SITE_ROOT}")
    print(f"  BASE_URL         : {BASE_URL}")
    print(f"  OUTPUT (standard): {OUTPUT_SITEMAP}")
    print(f"  OUTPUT (news)    : {OUTPUT_SITEMAP_NEWS}")
    print(f"  STATE FILE       : {STATE_FILE}")
    print(f"  IndexNow         : {'ABILITATO (solo pagine modificate)' if INDEXNOW_ENABLED else 'disabilitato'}")
    print("=" * 60 + "\n")

    if not os.path.isdir(SITE_ROOT):
        print(f"[ERRORE] La cartella '{SITE_ROOT}' non esiste.")
        return

    # ── RACCOLTA FILE ─────────────────────────────────────────────────────────
    files = collect_html_files(SITE_ROOT)
    if not files:
        print("[AVVISO] Nessun file HTML trovato. Controlla SITE_ROOT e EXCLUDE_DIRS.")
        return

    # ── SITEMAP STANDARD ──────────────────────────────────────────────────────
    print("[BUILD] Generazione sitemap.xml...")
    xml_standard = build_sitemap(files)
    with open(OUTPUT_SITEMAP, "w", encoding="utf-8") as f:
        f.write(xml_standard)
    print(f"\n[DONE]  sitemap.xml salvata: {len(files)} URL incluse.")

    # ── SITEMAP NEWS ──────────────────────────────────────────────────────────
    news_articles_all = parse_articles_from_index()

    # ── Filtro 30 giorni (regola Google News adattata) ───────────────────────
    # La specifica ufficiale Google suggerisce 48h, ma Gary Illyes (Google)
    # ha confermato in un Q&A che il limite reale prima dell'esclusione è
    # 30 giorni. Per siti con crawl lento (messi in coda da Google), il
    # filtro a 48h fa sparire gli articoli PRIMA che Google li legga, quindi
    # usiamo 30 giorni come compromesso documentato e non penalizzante.
    # Ref ufficiale: https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap
    # Ref Gary Illyes: https://www.searchenginejournal.com/google-seo-tips-for-news-articles-lastmod-tag-separate-sitemaps/478103/
    from datetime import datetime, timezone, timedelta
    _now = datetime.now(timezone.utc)
    _cutoff = _now - timedelta(days=30)
    news_articles = []
    for _a in news_articles_all:
        try:
            # La data è in formato ISO 8601 con offset (es. 2026-04-01T00:00:00+02:00)
            # Python 3.7+ supporta fromisoformat ma non tutti gli offset:
            # usiamo un parser robusto
            _ds = _a["date"].replace("+02:00", "+0200").replace("+01:00", "+0100")
            _d  = datetime.strptime(_ds, "%Y-%m-%dT%H:%M:%S%z")
            if _d >= _cutoff:
                news_articles.append(_a)
                print(f"  [NEWS-30D] INCLUSO  {_a['path']}  ({_a['date']})")
            else:
                print(f"  [NEWS-30D] ESCLUSO  {_a['path']}  ({_a['date']}) — più vecchio di 30 giorni")
        except Exception as _e:
            # Se la data non è parsabile, includiamo l'articolo per sicurezza
            print(f"  [NEWS-30D] INCLUSO (parse error: {_e})  {_a['path']}")
            news_articles.append(_a)

    print(f"\n[NEWS-30D] Articoli negli ultimi 30 giorni: {len(news_articles)} / {len(news_articles_all)} totali")

    if not news_articles_all:
        print("[AVVISO] Nessun articolo estratto. sitemap-news.xml non verrà aggiornata.")
    else:
        # Se la lista filtrata è vuota, la news sitemap sarà vuota.
        # Google stesso prevede questo caso e non lo considera un errore:
        # vedremo solo un avviso "Empty Sitemap" in Search Console, che è normale.
        xml_news = build_sitemap_news(news_articles)
        with open(OUTPUT_SITEMAP_NEWS, "w", encoding="utf-8") as f:
            f.write(xml_news)
        print(f"[DONE]  sitemap-news.xml salvata: {len(news_articles)} articoli inclusi.")

    # ── RSS FEED ──────────────────────────────────────────────────────────────
    # Riusa news_articles (stessa lista, stesso ordine più recente prima).
    # Se news_articles è vuota (nessun articolo estratto) il feed non viene scritto
    # per non sovrascrivere un feed già esistente con contenuto vuoto.
    if news_articles_all:
        rss_content = build_rss_feed(news_articles_all)  # RSS usa TUTTI gli articoli, non solo ultimi 48h
        with open(OUTPUT_RSS, "w", encoding="utf-8") as f:
            f.write(rss_content)
        print(f"[DONE]  feed.xml salvato: {len(news_articles_all)} articoli inclusi.")
        print()
        print("  ╔══════════════════════════════════════════════════════════════╗")
        print("  ║  RSS FEED AGGIORNATO                                         ║")
        print(f"  ║  File locale : {OUTPUT_RSS}")
        print(f"  ║  URL pubblico: {RSS_FEED_URL}")
        print("  ║                                                              ║")
        print("  ║  RICORDATI DI FARE IL PUSH del nuovo feed.xml               ║")
        print(f"  ║  Localizzato in: {OUTPUT_RSS}")
        print("  ╚══════════════════════════════════════════════════════════════╝")
    else:
        print("[AVVISO] RSS feed non aggiornato (nessun articolo disponibile).")

    # ── CHANGE TRACKING + INDEXNOW ────────────────────────────────────────────
    if INDEXNOW_ENABLED:
        old_state = load_state()
        changed_files, new_state = detect_changed_files(files, old_state)

        # Salva sempre il nuovo stato, anche se non ci sono modifiche,
        # così il file rimane allineato alla situazione attuale.
        save_state(new_state)

        if changed_files:
            url_list = collect_urls_for_indexnow(changed_files)
            ping_indexnow(url_list)
        else:
            print("\n[INDEXNOW] Nessuna pagina modificata — ping non necessario. ✓")
    else:
        print("\n[INDEXNOW] Ping disabilitato (INDEXNOW_ENABLED = False).")

    print("\n──────────────────────────────────────────────────────")
    print("  Prossimi passi dopo aver caricato i file:")
    print("  1. Search Console → Sitemap → invia entrambe (per Google)")
    print("     https://search.google.com/search-console/sitemaps")
    print("  2. Publisher Center → verifica inclusione")
    print("     https://publishercenter.google.com")
    print("  3. IndexNow già inviato automaticamente ↑ (solo modifiche)")
    print("──────────────────────────────────────────────────────")


if __name__ == "__main__":
    main()

