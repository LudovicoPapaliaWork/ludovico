# Regole tecniche del sito — Head, Schema.org e Markup invisibile

> Documento di riferimento per la struttura tecnica di `ludovicopapalia.com`.  
> Va aggiornato ogni volta che si modifica la struttura dell'head o dello schema.  
> Ultima revisione: 2026-04-05

---

## Indice

1. [Architettura generale](#1-architettura-generale)
2. [site-config.js — LP_SCHEMA globale](#2-site-configjs--lp_schema-globale)
3. [Homepage EN — index.html](#3-homepage-en--indexhtml)
4. [Homepage IT — index-it.html](#4-homepage-it--index-ithtml)
5. [Articolo divulgativo](#5-articolo-divulgativo)
6. [Paper accademico](#6-paper-accademico)
7. [Regole trasversali schema.org](#7-regole-trasversali-schemaorg)
8. [Regole meta tag OpenGraph e Twitter Card](#8-regole-meta-tag-opengraph-e-twitter-card)
9. [Regole Google Scholar (solo paper)](#9-regole-google-scholar-solo-paper)
10. [Cosa NON fare mai](#10-cosa-non-fare-mai)
11. [Checklist pre-pubblicazione](#11-checklist-pre-pubblicazione)

---

## 1. Architettura generale

### Come funziona l'iniezione dello schema

Il sito usa un sistema a due livelli per evitare che lo stesso nodo venga definito due volte sulla stessa pagina (causa di duplicati e conflitti nel parser di Google):

```
site-config.js
  └── Inietta LP_SCHEMA (Person + WebSite) su TUTTE le pagine
      └── ECCEZIONE: salta l'iniezione se trova <script data-lp-static="1">
          (solo index.html e index-it.html usano questo attributo)

index.html / index-it.html
  └── Blocco statico data-lp-static="1": Person + WebSite + ProfilePage
      (il blocco statico garantisce che i crawler leggano lo schema
       anche senza eseguire JavaScript)

Ogni altra pagina (articoli, paper)
  └── Definisce SOLO i nodi specifici di quella pagina (NewsArticle, ScholarlyArticle...)
  └── Referenzia Person e WebSite tramite @id, senza ridefinirli
```

### Regola fondamentale sugli @id

Ogni entità è definita UNA SOLA VOLTA nel sito, tramite un `@id` stabile:

| Entità | @id |
|--------|-----|
| Person (Ludovico Papalia) | `https://www.ludovicopapalia.com/#person` |
| WebSite | `https://www.ludovicopapalia.com/#website` |
| ProfilePage EN | `https://www.ludovicopapalia.com/#profilepage` |
| ProfilePage IT | `https://www.ludovicopapalia.com/index-it.html#profilepage` |
| Ogni articolo | `https://www.ludovicopapalia.com/art-divulgativi/slug.html#article` |

Tutte le altre pagine **referenziano** queste entità con `{"@id": "..."}` senza ridefinirne le proprietà.

---

## 2. site-config.js — LP_SCHEMA globale

Questo oggetto viene iniettato come `<script type="application/ld+json">` su ogni pagina del sito **tranne** homepage EN e IT (che usano il blocco statico).

### Contenuto attuale (da mantenere sincronizzato)

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Person",
      "@id": "https://www.ludovicopapalia.com/#person",
      "name": "Ludovico Papalia",
      "givenName": "Ludovico",
      "familyName": "Papalia",
      "nationality": { "@type": "Country", "name": "Italy" },
      "jobTitle": "PhD Candidate in Legal Informatics",
      "description": "PhD researcher at the University of Bologna specialising in blockchain technology applied to legislative simplification and parliamentary process tracking. Co-tutela with Vrije Universiteit Brussel. Collaborates with the IOTA Foundation within the PRIN2022/ERC HyperModeLex project.",
      "url": "https://www.ludovicopapalia.com",
      "email": "site-contact@ludovicopapalia.com",
      "sameAs": [
        "https://orcid.org/0009-0003-8751-9445",
        "https://www.unibo.it/sitoweb/ludovico.papalia2/",
        "https://dike.research.vub.be/en/ludovico-alessandro-papalia",
        "https://www.linkedin.com/in/ludovico-papalia/",
        "https://scholar.google.com/citations?user=WFQmMZIAAAAJ&hl=it",
        "https://www.instagram.com/ludovicopapalia/",
        "https://www.wikidata.org/wiki/Q138795841"
      ],
      "affiliation": [
        {
          "@type": "CollegeOrUniversity",
          "name": "Università di Bologna",
          "url": "https://www.unibo.it",
          "department": "Dipartimento di Scienze Giuridiche"
        },
        {
          "@type": "CollegeOrUniversity",
          "name": "Vrije Universiteit Brussel",
          "url": "https://www.vub.be"
        }
      ],
      "alumniOf": [
        { "@type": "CollegeOrUniversity", "name": "Università La Sapienza di Roma", "url": "https://www.uniroma1.it" },
        { "@type": "CollegeOrUniversity", "name": "Università degli Studi di Milano-Bicocca", "url": "https://www.unimib.it" },
        { "@type": "CollegeOrUniversity", "name": "University of Lapland", "url": "https://www.ulapland.fi" }
      ],
      "knowsAbout": [
        "Blockchain", "Distributed Ledger Technology", "Distributed Technology",
        "Legislative Simplification", "Legal Informatics", "Smart Contracts",
        "Akoma Ntoso", "Digital Government", "Parliamentary Informatics",
        "Privacy Law", "GDPR", "Online Hate Speech", "Artificial Intelligence in Law",
        "Right to Be Forgotten", "Digital Evidence", "Python Programming"
      ],
      "knowsLanguage": [
        { "@type": "Language", "name": "Italian" },
        { "@type": "Language", "name": "English" },
        { "@type": "Language", "name": "French" }
      ],
      "hasCredential": [
        {
          "@type": "EducationalOccupationalCredential",
          "credentialCategory": "doctorate",
          "name": "PhD in Legal Informatics (DIN Blockchain)",
          "recognizedBy": { "@type": "CollegeOrUniversity", "name": "Università di Bologna" }
        },
        {
          "@type": "EducationalOccupationalCredential",
          "credentialCategory": "master degree",
          "name": "LLM in Legal Informatics, New Technologies and IT Law",
          "recognizedBy": { "@type": "CollegeOrUniversity", "name": "Università La Sapienza di Roma" },
          "description": "Graduated 110/110 cum laude"
        }
      ]
    },
    {
      "@type": "WebSite",
      "@id": "https://www.ludovicopapalia.com/#website",
      "url": "https://www.ludovicopapalia.com",
      "name": "Ludovico Papalia",
      "description": "Personal academic website of Ludovico Papalia, PhD Candidate in Legal Informatics at the University of Bologna.",
      "author": { "@id": "https://www.ludovicopapalia.com/#person" },
      "inLanguage": "en",
      "about": { "@id": "https://www.ludovicopapalia.com/#person" }
    }
  ]
}
```

### Regole di aggiornamento

- `ProfilePage` NON deve mai stare in LP_SCHEMA — appartiene solo ai blocchi statici delle homepage
- Il nodo `Person` in LP_SCHEMA deve essere identico a quello nei blocchi statici di `index.html` e `index-it.html`
- Aggiornare LP_SCHEMA significa aggiornare anche i tre file: `site-config.js`, `index.html`, `index-it.html`

---

## 3. Homepage EN — index.html

### Meta tag head (ordine da rispettare)

```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Ludovico Papalia — PhD Candidate in Legal Informatics at the University of Bologna. Researcher at the intersection of blockchain, distributed ledger technologies, and legislative simplification.">
<meta name="author" content="Ludovico Papalia">
<meta name="keywords" content="Ludovico Papalia, blockchain, legal informatics, PhD, Bologna, DLT, legislative simplification, smart contracts">

<!-- HREFLANG -->
<link rel="alternate" hreflang="en"        href="https://www.ludovicopapalia.com/">
<link rel="alternate" hreflang="it"        href="https://www.ludovicopapalia.com/index-it.html">
<link rel="alternate" hreflang="x-default" href="https://www.ludovicopapalia.com/">

<!-- CANONICAL -->
<link rel="canonical" href="https://www.ludovicopapalia.com/">

<!-- OPEN GRAPH -->
<meta property="og:title"            content="Ludovico Papalia — Legal Informatics Researcher">
<meta property="og:description"      content="PhD Candidate at University of Bologna. Research at the intersection of blockchain and law.">
<meta property="og:type"             content="website">
<meta property="og:url"              content="https://www.ludovicopapalia.com/">
<meta property="og:image"            content="https://www.ludovicopapalia.com/profile.png">
<meta property="og:locale"           content="en_US">
<meta property="og:locale:alternate" content="it_IT">

<title>Ludovico Papalia</title>
```

### Schema.org — blocco statico (data-lp-static="1")

Deve contenere: `Person` + `WebSite` + `ProfilePage`.  
Il nodo `Person` deve essere identico a quello in `site-config.js`.

```json
{
  "@context": "https://schema.org",
  "@graph": [
    { /* ...Person identico a LP_SCHEMA... */ },
    { /* ...WebSite identico a LP_SCHEMA... */ },
    {
      "@type": "ProfilePage",
      "@id": "https://www.ludovicopapalia.com/#profilepage",
      "url": "https://www.ludovicopapalia.com/",
      "name": "Ludovico Papalia — Legal Informatics Researcher",
      "isPartOf": { "@id": "https://www.ludovicopapalia.com/#website" },
      "about": { "@id": "https://www.ludovicopapalia.com/#person" },
      "mainEntity": { "@id": "https://www.ludovicopapalia.com/#person" },
      "inLanguage": "en"
    }
  ]
}
```

> ⚠️ `mainEntity` è OBBLIGATORIO su ProfilePage secondo Google (campo critico nel Rich Results Test).  
> ⚠️ `author` NON va messo su ProfilePage (Google lo marca come "campo non riconosciuto").

---

## 4. Homepage IT — index-it.html

### Meta tag head

```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Ludovico Papalia — Dottorando in Informatica Giuridica all'Università di Bologna. Ricercatore all'incrocio tra tecnologia blockchain, registri distribuiti e semplificazione normativa.">
<meta name="author" content="Ludovico Papalia">
<meta name="keywords" content="Ludovico Papalia, blockchain, informatica giuridica, dottorato, Bologna, DLT, semplificazione normativa, smart contract, IOTA, diritto digitale, diritto informatico">

<!-- OPEN GRAPH -->
<meta property="og:title"            content="Ludovico Papalia — Ricercatore in Informatica Giuridica">
<meta property="og:description"      content="Dottorando all'Università di Bologna. Ricerca all'incrocio tra blockchain e ordinamento giuridico.">
<meta property="og:type"             content="website">
<meta property="og:url"              content="https://www.ludovicopapalia.com/index-it.html">
<meta property="og:image"            content="https://www.ludovicopapalia.com/profile.png">
<meta property="og:locale"           content="it_IT">
<meta property="og:locale:alternate" content="en_US">

<!-- CANONICAL + HREFLANG -->
<link rel="canonical"   href="https://www.ludovicopapalia.com/index-it.html">
<link rel="alternate"   hreflang="it"        href="https://www.ludovicopapalia.com/index-it.html">
<link rel="alternate"   hreflang="en"        href="https://www.ludovicopapalia.com/">
<link rel="alternate"   hreflang="x-default" href="https://www.ludovicopapalia.com/">

<title>Ludovico Papalia</title>
```

### Schema.org

**Blocco 1** — WebPage in italiano (senza `data-lp-static`):

```json
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "url": "https://www.ludovicopapalia.com/index-it.html",
  "name": "Ludovico Papalia — Ricercatore in Informatica Giuridica",
  "description": "Pagina accademica di Ludovico Papalia, dottorando in Informatica Giuridica all'Università di Bologna.",
  "inLanguage": "it",
  "isPartOf": { "@id": "https://www.ludovicopapalia.com/#website" },
  "about":     { "@id": "https://www.ludovicopapalia.com/#person" },
  "author":    { "@id": "https://www.ludovicopapalia.com/#person" }
}
```

**Blocco 2** — Blocco statico `data-lp-static="1"` con Person + WebSite + ProfilePage IT:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    { /* ...Person identico a LP_SCHEMA... */ },
    { /* ...WebSite identico a LP_SCHEMA... */ },
    {
      "@type": "ProfilePage",
      "@id": "https://www.ludovicopapalia.com/index-it.html#profilepage",
      "url": "https://www.ludovicopapalia.com/index-it.html",
      "name": "Ludovico Papalia — Ricercatore in Informatica Giuridica",
      "isPartOf": { "@id": "https://www.ludovicopapalia.com/#website" },
      "about":    { "@id": "https://www.ludovicopapalia.com/#person" },
      "mainEntity": { "@id": "https://www.ludovicopapalia.com/#person" },
      "inLanguage": "it"
    }
  ]
}
```

---

## 5. Articolo divulgativo

Percorso: `art-divulgativi/slug-articolo.html`

### Meta tag head

```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>{TITOLO} — Ludovico Papalia</title>
<meta name="description" content="{META_DESCRIPTION — max 160 caratteri}">
<meta name="author"      content="Ludovico Papalia">
<meta name="keywords"    content="{parole chiave} Ludovico Papalia">
<meta name="robots"      content="index, follow">
<link rel="canonical"    href="https://www.ludovicopapalia.com/art-divulgativi/{SLUG}.html">

<!-- OPEN GRAPH -->
<meta property="og:type"                  content="article">
<meta property="og:title"                 content="{TITOLO}">
<meta property="og:description"           content="{META_DESCRIPTION}">
<meta property="og:url"                   content="https://www.ludovicopapalia.com/art-divulgativi/{SLUG}.html">
<meta property="og:image"                 content="{URL_IMMAGINE_min_696px — fallback: profile.png}">
<meta property="og:site_name"             content="Ludovico Papalia — Legal Informatics">
<meta property="article:author"           content="Ludovico Papalia">
<meta property="article:published_time"   content="{YYYY-MM-DD}">
<meta property="article:section"          content="{SEZIONE — es. Cybersicurezza}">
<meta property="article:tag"              content="{TAG1}">
<!-- ripeti article:tag per ogni tag -->

<!-- TWITTER CARD -->
<meta name="twitter:card"        content="summary_large_image">
<meta name="twitter:title"       content="{TITOLO}">
<meta name="twitter:description" content="{DESCRIZIONE breve max 200 car}">
```

### Schema.org — JSON-LD (nodi specifici della pagina)

Person e WebSite vengono iniettati da `site-config.js`. Qui restano solo i nodi della pagina:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "NewsArticle",
      "@id": "https://www.ludovicopapalia.com/art-divulgativi/{SLUG}.html#article",
      "headline": "{TITOLO — max 110 caratteri per rich results}",
      "description": "Ludovico Papalia esperto di {TEMA} analizza {SOGGETTO}.",
      "keywords": ["{keyword1}", "{keyword2}", "Ludovico Papalia"],
      "datePublished": "{YYYY-MM-DDT00:00:00Z}",
      "dateModified":  "{YYYY-MM-DDT00:00:00Z}",
      "inLanguage": "it",
      "articleSection": "{SEZIONE}",
      "genre": "Divulgazione giuridica",
      "url": "https://www.ludovicopapalia.com/art-divulgativi/{SLUG}.html",
      "isPartOf":  { "@id": "https://www.ludovicopapalia.com/#website" },
      "author":    { "@id": "https://www.ludovicopapalia.com/#person" },
      "publisher": { "@id": "https://www.ludovicopapalia.com/#person" },
      "image": {
        "@type": "ImageObject",
        "url": "{URL_IMMAGINE — fallback: https://www.ludovicopapalia.com/profile.png}"
      },
      "isAccessibleForFree": true,
      "mainEntityOfPage": "https://www.ludovicopapalia.com/art-divulgativi/{SLUG}.html",
      "alternativeHeadline": "{smart_truncate(meta_description, 200)}",
      "speakable": {
        "@type": "SpeakableSpecification",
        "cssSelector": ["h1.article-title", ".article-lead"]
      },
      "about": [
        { "@type": "Thing", "name": "{CONCETTO1}", "description": "{definizione breve}" }
      ],
      "mentions": [
        { "@type": "Organization", "name": "{ORG}", "url": "{URL}" }
      ]
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Home",     "item": "https://www.ludovicopapalia.com" },
        { "@type": "ListItem", "position": 2, "name": "Articoli", "item": "https://www.ludovicopapalia.com/divulgativi-index.html" },
        { "@type": "ListItem", "position": 3, "name": "{TITOLO}", "item": "https://www.ludovicopapalia.com/art-divulgativi/{SLUG}.html" }
      ]
    }
  ]
}
```

### Se l'articolo ha un video YouTube

Aggiungere il nodo `video` dentro `NewsArticle`:

```json
"video": {
  "@type": "VideoObject",
  "name": "{TITOLO VIDEO}",
  "embedUrl": "https://www.youtube-nocookie.com/embed/{VIDEO_ID}",
  "url": "https://youtu.be/{VIDEO_ID}",
  "description": "{DESCRIZIONE VIDEO}",
  "uploadDate": "{YYYY-MM-DDT00:00:00Z}",
  "thumbnailUrl": "https://img.youtube.com/vi/{VIDEO_ID}/maxresdefault.jpg"
}
```

E `og:image` deve usare il thumbnail YouTube:

```
https://img.youtube.com/vi/{VIDEO_ID}/maxresdefault.jpg
```

### Regole descrizione schema (campo `description`)

Il campo `description` nel JSON-LD dell'articolo segue il pattern fisso:

```
"Ludovico Papalia esperto di {COMPETENZA} + {analizza/esamina/discute} + {SOGGETTO_ARTICOLO}."
```

Questo serve al SEO per associare il nome dell'autore ai temi trattati.

### alternativeHeadline — regola smart_truncate

`alternativeHeadline` viene derivato dalla meta description con troncatura a 200 caratteri al confine più vicino tra: `. `, `! `, `? `, `, `, ` `. Non troncare a metà parola.

---

## 6. Paper accademico

Percorso: `papers/{Nome_Paper_Senza_Spazi}.html`  
PDF: `papers/pap-docs/{Nome_Paper_Senza_Spazi}.pdf`

### Meta tag head (ordine: Google Scholar → SEO → OG)

```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- ══ GOOGLE SCHOLAR — OBBLIGATORI (senza questi il paper non viene indicizzato) ══ -->
<meta name="citation_title"              content="{TITOLO COMPLETO}">
<meta name="citation_author"             content="Cognome, Nome">
<!-- ripeti per ogni autore nell'ordine corretto -->
<meta name="citation_publication_date"   content="{YYYY/MM/DD}">

<!-- Per conference paper: -->
<meta name="citation_conference_title"   content="{NOME CONFERENZA}">
<!-- Per journal paper (alternativo): -->
<!-- <meta name="citation_journal_title" content="{NOME RIVISTA}">
     <meta name="citation_volume"        content="{VOLUME}">
     <meta name="citation_issue"         content="{NUMERO}">
     <meta name="citation_firstpage"     content="{PAGINA INIZIO}">
     <meta name="citation_lastpage"      content="{PAGINA FINE}"> -->

<meta name="citation_language"           content="en">
<meta name="citation_keywords"           content="{keyword1}; {keyword2}; Ludovico Papalia">
<meta name="citation_abstract_html_url"  content="https://www.ludovicopapalia.com/papers/{SLUG}.html">
<meta name="citation_pdf_url"            content="https://www.ludovicopapalia.com/papers/pap-docs/{SLUG}.pdf">
<!-- Se disponibile: -->
<!-- <meta name="citation_doi"            content="10.xxxx/xxxxx"> -->

<!-- ══ SEO STANDARD ══ -->
<title>{TITOLO} — Ludovico Papalia</title>
<meta name="description" content="Ludovico Papalia esperto di {TEMA}. {VENUE}, {ANNO}.">
<meta name="author"      content="{Autore1}; {Autore2}; ...">
<meta name="keywords"    content="Ludovico Papalia, {keyword1}, {keyword2}">
<meta name="robots"      content="index, follow">
<link rel="canonical"    href="https://www.ludovicopapalia.com/papers/{SLUG}.html">

<!-- ══ OPEN GRAPH ══ -->
<meta property="og:type"               content="article">
<meta property="og:title"              content="{TITOLO}">
<meta property="og:description"        content="{ABSTRACT breve}">
<meta property="og:url"                content="https://www.ludovicopapalia.com/papers/{SLUG}.html">
<meta property="og:image"              content="https://www.ludovicopapalia.com/profile.png">
<meta property="article:author"        content="Ludovico Papalia">
<meta property="article:published_time" content="{YYYY-MM-DD}">
```

### Schema.org — JSON-LD

Il tipo varia in base alla pubblicazione:

| Tipo pubblicazione | @type schema.org |
|---|---|
| Articolo in conference proceedings | `ScholarlyArticle` |
| Articolo in rivista | `ScholarlyArticle` |
| Capitolo di libro | `Chapter` |
| Libro/Monografia | `Book` |

```json
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "headline": "{TITOLO}",
  "name": "{TITOLO}",
  "author": [
    { "@type": "Person", "name": "Arianna Arruzzoli" },
    {
      "@type": "Person",
      "@id": "https://www.ludovicopapalia.com/#person",
      "name": "Ludovico Papalia",
      "url": "https://www.ludovicopapalia.com",
      "affiliation": { "@type": "CollegeOrUniversity", "name": "Università di Bologna" }
    }
  ],
  "datePublished": "{YYYY-MM-DDT00:00:00Z}",
  "inLanguage": "en",
  "description": "Ludovico Papalia esperto di {TEMA}. {VENUE}, {ANNO}.",
  "keywords": ["{keyword1}", "{keyword2}", "Ludovico Papalia"],
  "abstract": "{ABSTRACT COMPLETO — identico alla rivista/atti}",
  "image": "https://www.ludovicopapalia.com/profile.png",
  "isPartOf": {
    "@type": "Book",
    "name": "{NOME PROCEEDINGS O RIVISTA}",
    "url": "{URL UFFICIALE}"
  },
  "url": "https://www.ludovicopapalia.com/papers/{SLUG}.html",
  "sameAs": "{URL DOI O URL PUBLISHER}",
  "license": "https://creativecommons.org/licenses/by-nc-nd/4.0/"
}
```

### Regola autori nei paper

- Per **Ludovico Papalia**: usare sempre `@id`, `name`, `url`, `affiliation` (nodo con informazioni complete ma non ridondante con LP_SCHEMA)
- Per **co-autori senza URL verificata**: usare solo `@type` e `name` (non inventare URL)
- Per **co-autori con affiliation nota**: aggiungere `affiliation`
- L'ordine degli autori deve rispecchiare esattamente quello della pubblicazione originale

---

## 7. Regole trasversali schema.org

### datePublished e dateModified

Formato obbligatorio: **ISO 8601 completo con timezone**

```
✓ Corretto:   "2026-04-03T00:00:00Z"
✗ Sbagliato:  "2026-04-03"
✗ Sbagliato:  "2026-04"
✗ Sbagliato:  "2026"
```

Per date con solo anno o anno-mese noti, usare il primo giorno come approssimazione (`2022-01-01T00:00:00Z`).

### image

- Obbligatoria su `NewsArticle` e raccomandata su `ScholarlyArticle`
- Formato: `ImageObject` con `url`
- Minimo: 696px di larghezza (requisito Google per rich results)
- Fallback universale: `https://www.ludovicopapalia.com/profile.png`
- Con video YouTube: `https://img.youtube.com/vi/{ID}/maxresdefault.jpg` (1280×720)

### isAccessibleForFree

Obbligatorio `true` su tutti gli articoli divulgativi. La sua assenza può far sì che Google interpreti la pagina come paywall-gated.

### Nodi author e publisher negli articoli divulgativi

```json
"author":    { "@id": "https://www.ludovicopapalia.com/#person" },
"publisher": { "@id": "https://www.ludovicopapalia.com/#person" }
```

Non ridefinire mai le proprietà di `Person` inline dentro `author` o `publisher` sulle pagine articolo: genera conflitti con la definizione iniettata da `site-config.js`.

### ProfilePage

- Presente SOLO su `index.html` e `index-it.html`
- Campi obbligatori: `mainEntity` (critico per Google), `isPartOf`, `about`, `url`
- Campi da NON usare: `author` (Google lo marca come non riconosciuto)
- NON inserire ProfilePage in `site-config.js` (verrebbe iniettato su ogni pagina del sito)

### BreadcrumbList

Obbligatorio su ogni articolo divulgativo. Non necessario su paper accademici.

### Speakable

Usare `cssSelector` (non `xpath`):

```json
"speakable": {
  "@type": "SpeakableSpecification",
  "cssSelector": ["h1.article-title", ".article-lead"]
}
```

---

## 8. Regole meta tag OpenGraph e Twitter Card

### og:image

- **Obbligatorio** su tutti i tipi di pagina
- Minimo 696px di larghezza (soglia Google News e Facebook)
- Preferito: 1200×630px per Facebook/LinkedIn
- Fallback: `https://www.ludovicopapalia.com/profile.png`
- Con video YouTube: usare `maxresdefault.jpg` del video (1280×720)

### og:type

| Pagina | og:type |
|--------|---------|
| Homepage | `website` |
| Articolo divulgativo | `article` |
| Paper accademico | `article` |

### article:published_time

Formato: `YYYY-MM-DD` (senza timezone — è accettato da OpenGraph).

### Twitter Card

```html
<meta name="twitter:card" content="summary_large_image">
```

Usare sempre `summary_large_image` (non `summary`) per massimizzare la visibilità su X/Twitter.

---

## 9. Regole Google Scholar (solo paper)

Google Scholar indicizza i paper tramite i meta tag `citation_*`. Senza questi tag il paper NON appare su Scholar.

### Tag obbligatori (senza questi: non indicizzato)

| Tag | Valore |
|-----|--------|
| `citation_title` | Titolo esatto |
| `citation_author` | Un tag per autore, formato: `Cognome, Nome` |
| `citation_publication_date` | `YYYY/MM/DD` |
| `citation_abstract_html_url` | URL della pagina sul sito |
| `citation_pdf_url` | URL diretto al PDF |

### Tag fortemente raccomandati

| Tag | Note |
|-----|------|
| `citation_conference_title` o `citation_journal_title` | Solo uno dei due |
| `citation_doi` | Se disponibile |
| `citation_keywords` | Includi sempre "Ludovico Papalia" |
| `citation_language` | `en` o `it` |
| `citation_firstpage` | Pagina di inizio nei proceedings |

### Tag opzionali (journal paper)

```
citation_volume, citation_issue, citation_firstpage, citation_lastpage, citation_issn
```

---

## 10. Cosa NON fare mai

| Pratica vietata | Motivazione |
|-----------------|-------------|
| `birthDate` nel nodo `Person` | Dato sensibile, beneficio marginale, non necessario |
| `ProfilePage` in `site-config.js` | Verrebbe iniettato su ogni pagina del sito |
| `author` inline con proprietà complete su pagine articolo | Genera conflitto/duplicato con Person di site-config.js |
| `author` su nodo `ProfilePage` | Google lo marca come campo non riconosciuto |
| Due definizioni dello stesso `@id` sulla stessa pagina | Causa duplicati nel parser di Google |
| `datePublished` senza timezone | Warning nel Rich Results Test |
| `image` mancante su NewsArticle | Riduce eligibilità ai rich results |
| `isAccessibleForFree` assente su articoli gratuiti | Google può interpretare la pagina come paywall |
| `mainEntity` assente su `ProfilePage` | Errore critico nel Rich Results Test |
| URL `youtube.com/embed/` | Usare sempre `youtube-nocookie.com/embed/` (GDPR) |
| Modificare `sitemap.xml` manualmente | Usare sempre `generate_sitemap.py` |
| Aggiornare LP_SCHEMA solo in site-config.js | Va sempre sincronizzato con index.html e index-it.html |

---

## 11. Checklist pre-pubblicazione

### Articolo divulgativo

- [ ] `<title>` nel formato: `{TITOLO} — Ludovico Papalia`
- [ ] `meta description` max 160 caratteri
- [ ] `canonical` URL corretto e completo
- [ ] `og:image` presente (minimo 696px)
- [ ] `article:published_time` in formato `YYYY-MM-DD`
- [ ] JSON-LD valido (verificare con Rich Results Test)
- [ ] `datePublished` e `dateModified` con timezone (`T00:00:00Z`)
- [ ] `author` e `publisher` come semplici `@id` reference (non inline)
- [ ] `isAccessibleForFree: true`
- [ ] `image` presente (ImageObject con url)
- [ ] `mainEntityOfPage` = URL canonica pagina
- [ ] `alternativeHeadline` derivata da meta description (max 200 car)
- [ ] `speakable` con `cssSelector` (non xpath)
- [ ] `BreadcrumbList` con 3 livelli
- [ ] `keywords` include "Ludovico Papalia"
- [ ] Aggiungere a `divulgativi-index.html`
- [ ] Aggiungere a `llms.txt`
- [ ] Rieseguire `generate_sitemap.py`

### Paper accademico

- [ ] Tutti i tag `citation_*` presenti e corretti
- [ ] `citation_author` nel formato `Cognome, Nome`
- [ ] `citation_pdf_url` punta al PDF effettivamente disponibile
- [ ] `datePublished` con timezone (`T00:00:00Z`)
- [ ] `image` presente (fallback: `profile.png`)
- [ ] `abstract` identico all'originale della rivista/atti
- [ ] `og:image` presente
- [ ] Autori in ordine corretto
- [ ] Aggiornare `index.html` e `index-it.html` (chip/link al paper)
- [ ] Aggiungere a `llms.txt`
- [ ] Rieseguire `generate_sitemap.py`

### Aggiornamento globale Person/Schema

Quando si modifica il nodo `Person` aggiornare in questo ordine:

1. `site-config.js` → LP_SCHEMA
2. `index.html` → blocco `data-lp-static="1"`
3. `index-it.html` → blocco `data-lp-static="1"`

I tre devono essere sempre identici sulla parte `Person` e `WebSite`.

---

*Tool di validazione: [Rich Results Test](https://search.google.com/test/rich-results) — [Schema Markup Validator](https://validator.schema.org/) — [Google Search Console](https://search.google.com/search-console)*
