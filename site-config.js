/**
 * ╔══════════════════════════════════════════════════════════════════════════╗
 * ║  LUDOVICO PAPALIA — MASTER SITE CONFIGURATION                          ║
 * ║  /site-config.js                                                        ║
 * ║                                                                          ║
 * ║  Modifica SOLO questo file per propagare le modifiche su tutte le       ║
 * ║  pagine del sito contemporaneamente:                                    ║
 * ║    • Palette colori e design tokens CSS                                  ║
 * ║    • Tipografia (font families + Google Fonts URL)                       ║
 * ║    • Barra di navigazione (logo, link sets)                             ║
 * ║    • Schema.org Person + WebSite (condivisi su tutte le pagine)         ║
 * ║    • Google Analytics 4 + Meta Pixel (tracking IDs)                    ║
 * ║                                                                          ║
 * ║  I meta tag citation_* di Google Scholar NON sono gestiti qui —         ║
 * ║  restano in ciascun file HTML come richiesto dallo Scholar indexer.     ║
 * ║                                                                          ║
 * ║  ── COME IMPOSTARE IL TIPO DI NAV PER PAGINA ───────────────────────── ║
 * ║                                                                          ║
 * ║  Nav principale EN (index.html) — nessun override necessario            ║
 * ║                                                                          ║
 * ║  Nav con back-link (pagine paper/articolo):                             ║
 * ║    <script>                                                             ║
 * ║      window.LP_NAV_TYPE = 'back';                                       ║
 * ║      window.LP_NAV_BACK = {                                             ║
 * ║        href:  '/index.html#publications',                               ║
 * ║        label: 'All publications'                                        ║
 * ║      };                                                                 ║
 * ║    </script>                                                            ║
 * ║                                                                          ║
 * ║  Nav italiana (pagine /articoli):                                       ║
 * ║    <script>                                                             ║
 * ║      window.LP_NAV_TYPE   = 'it';                                       ║
 * ║      window.LP_NAV_ACTIVE = 'Articoli'; // label da evidenziare         ║
 * ║    </script>                                                            ║
 * ╚══════════════════════════════════════════════════════════════════════════╝
 */


/* ═══════════════════════════════════════════════════════════════════════════ */
/* 1. PALETTE COLORI                                                          */
/*    Modifica questi valori per ridipingere l'intero sito istantaneamente.   */
/* ═══════════════════════════════════════════════════════════════════════════ */
var LP_COLORS = {

  /* ── FONDALI ─────────────────────────────────────────────────
     Bianco caldo (non clinico), con una leggera nota panna
     che mantiene la sensazione "carta di qualità".            */
  bg:       '#faf8f5',               /* sfondo pagina principale              */
  bgCard:   '#f3f0ea',               /* card / pannelli: leggermente più scuro */
  bgCard2:  '#eae6dd',               /* card annidate o hover state           */
  bgNav:    'rgba(250,248,245,.88)', /* nav: stesso tono, semi-trasparente     */

  /* ── BORDI ───────────────────────────────────────────────────
     Su fondo chiaro i bordi bianchi spariscono;
     serve un nero a bassa opacità.                           */
  border:   'rgba(30,25,18,.09)',    /* bordi sottili, caldi non freddi       */

  /* ── ORO ─────────────────────────────────────────────────────
     Problema principale: #c8a96e su bianco = contrasto 2.3:1
     insufficiente anche per testo decorativo.
     #8a6220 → contrasto ~5.2:1 su #faf8f5: leggibile e premium.
     goldDim sale invece di scendere, usato per badge/dot dove
     il contrasto non è critico ma la leggibilità conta.      */
  gold:     '#8a6220',               /* oro primario: label, badge, accenti   */
  goldDim:  '#b09050',               /* oro decorativo: bordi, separatori     */

  /* ── TESTO ───────────────────────────────────────────────────
     L'inversione più importante: text → quasi-nero caldo,
     muted → grigio caldo leggibile (~5:1),
     accent → il colore più scuro, per h1/h2 serif.           */
  text:     '#1c1a16',               /* body text primario                    */
  muted:    '#6b6055',               /* helper text, metadata                 */
  accent:   '#2a2318',               /* intestazioni: massimo contrasto warm  */

  radius:   '14px',
};

/* ═══════════════════════════════════════════════════════════════════════════ */
/* 2. TIPOGRAFIA                                                               */
/*    Modifica font stack o Google Fonts URL qui.                             */
/* ═══════════════════════════════════════════════════════════════════════════ */
var LP_FONTS = {
  serif:     "'Cormorant Garamond', Georgia, serif",
  sans:      "'Sora', system-ui, sans-serif",
  googleUrl: 'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400;1,600&family=Sora:wght@300;400;500&display=swap',
};


/* ═══════════════════════════════════════════════════════════════════════════ */
/* 3. TRACKING                                                                 */
/*    Inserisci gli ID per attivare il tracking. Lascia '' per disattivare.  */
/* ═══════════════════════════════════════════════════════════════════════════ */
var LP_TRACKING = {
  ga4:        '',   /* Google Analytics 4 Measurement ID  — es. 'G-XXXXXXXXXX'    */
  metaPixel:  '',   /* Meta (Facebook) Pixel ID           — es. '123456789012345' */
};


/* ═══════════════════════════════════════════════════════════════════════════ */
/* 4. NAVIGAZIONE                                                              */
/*    Testo logo e set di link. Vedi header per gli override per-pagina.     */
/* ═══════════════════════════════════════════════════════════════════════════ */
var LP_NAV_LOGO = 'Ludovico Papalia';

var LP_NAV_LINKS = {

  /* Nav principale inglese — usata su index.html */
  'default': [
    { label: 'Research',     href: '/index.html#research' },
    { label: 'About',        href: '/index.html#about' },
    { label: 'Background',   href: '/index.html#education' },
    { label: 'Publications', href: '/index.html#publications' },
    { label: 'Divulgazione 🇮🇹', href: '/divulgativi-index.html' },
    { label: 'Contact',      href: '/index.html#contact' },
  ],

  /* Nav italiana — usata sulle pagine /art-divulgativi */
  'it': [
    { label: 'Home',         href: '/index-it.html' },
    { label: 'Divulgazione', href: '/divulgativi-index.html' },
    { label: 'Ricerca',      href: '/index-it.html#research' },
    { label: 'Contatti',     href: '/index-it.html#contact' },
  ],

  /* Nav italiana per la homepage index-it.html — link interni hash */
  'it-home': [
    { label: 'Ricerca',          href: '#research' },
    { label: 'Chi sono',         href: '#about' },
    { label: 'Percorso',         href: '#education' },
    { label: 'Pubblicazioni',    href: '#publications' },
    { label: 'Divulgazione 🇮🇹', href: '/divulgativi-index.html' },
    { label: 'Contatti',         href: '#contact' },
  ],

};


/* ═══════════════════════════════════════════════════════════════════════════ */
/* 5. SCHEMA.ORG — PERSON + WEBSITE CONDIVISI                                 */
/*    Iniettati come JSON-LD su ogni pagina.                                  */
/*    Gli schema specifici per pagina (ScholarlyArticle, Article, ecc.)      */
/*    restano nel <head> di ciascun file HTML.                                */
/* ═══════════════════════════════════════════════════════════════════════════ */
var LP_SCHEMA = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Person",
      "@id": "https://www.ludovicopapalia.com/#person",
      "name": "Ludovico Papalia",
      "givenName": "Ludovico",
      "familyName": "Papalia",
      "birthDate": "1996-11-21",
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
        "https://www.instagram.com/ludovicopapalia/"
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
        {
          "@type": "CollegeOrUniversity",
          "name": "Università La Sapienza di Roma",
          "url": "https://www.uniroma1.it"
        },
        {
          "@type": "CollegeOrUniversity",
          "name": "Università degli Studi di Milano-Bicocca",
          "url": "https://www.unimib.it"
        },
        {
          "@type": "CollegeOrUniversity",
          "name": "University of Lapland",
          "url": "https://www.ulapland.fi"
        }
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
      ],
      "author": [
        {
          "@type": "Book",
          "name": "Odio Online: Tra Criminologia e Diritto",
          "datePublished": "2020",
          "isbn": "979-8567192726"
        },
        {
          "@type": "ScholarlyArticle",
          "name": "The Bias of Artificial Intelligence within the Justice Field",
          "datePublished": "2022",
          "publisher": { "@type": "Organization", "name": "CEUR-WS" },
          "isPartOf": { "@type": "PublicationVolume", "name": "CEUR-WS Vol. 3368" }
        }
      ]
    },
    {
      "@type": "WebSite",
      "@id": "https://www.ludovicopapalia.com/#website",
      "url": "https://www.ludovicopapalia.com",
      "name": "Ludovico Papalia — Legal Informatics Researcher",
      "description": "Personal academic website of Ludovico Papalia, PhD Candidate in Legal Informatics at the University of Bologna.",
      "author": { "@id": "https://www.ludovicopapalia.com/#person" },
      "inLanguage": "en",
      "about": { "@id": "https://www.ludovicopapalia.com/#person" }
    }
  ]
};


/* ══════════════════════════════════════════════════════════════════════════ */
/* MOTORE DI INIEZIONE — non modificare se non sai cosa stai facendo         */
/* ══════════════════════════════════════════════════════════════════════════ */

/**
 * A. CSS design tokens — iniettati in modo sincrono per evitare FOUC.
 *    Viene creato un <style id="lp-design-tokens"> come primo elemento in <head>.
 */
(function injectTokens() {
  var s = document.createElement('style');
  s.id = 'lp-design-tokens';
  s.textContent =
    ':root {\n' +
    '  --bg:       ' + LP_COLORS.bg       + ';\n' +
    '  --bg-card:  ' + LP_COLORS.bgCard   + ';\n' +
    '  --bg-card2: ' + LP_COLORS.bgCard2  + ';\n' +
    '  --bg-nav:   ' + LP_COLORS.bgNav    + ';\n' +
    '  --border:   ' + LP_COLORS.border   + ';\n' +
    '  --gold:     ' + LP_COLORS.gold     + ';\n' +
    '  --gold-dim: ' + LP_COLORS.goldDim  + ';\n' +
    '  --text:     ' + LP_COLORS.text     + ';\n' +
    '  --muted:    ' + LP_COLORS.muted    + ';\n' +
    '  --accent:   ' + LP_COLORS.accent   + ';\n' +
    '  --radius:   ' + LP_COLORS.radius   + ';\n' +
    '  --ff-serif: ' + LP_FONTS.serif     + ';\n' +
    '  --ff-sans:  ' + LP_FONTS.sans      + ';\n' +
    '}';
  document.head.appendChild(s);
}());

/**
 * B. CSS della navigazione — iniettato in modo sincrono.
 *    Include tutti gli stili per nav, .nav-logo, .nav-links, .nav-back
 *    e i relativi breakpoint responsive.
 */
(function injectNavCSS() {
  var s = document.createElement('style');
  s.id = 'lp-nav-css';
  s.textContent = [
    '/* ─── NAV — generato da site-config.js ───────────────────── */',
    'nav {',
    '  position: fixed; top: 0; left: 0; right: 0; z-index: 100;',
    '  display: flex; align-items: center; justify-content: space-between;',
    '  padding: 1.2rem 2.5rem;',
    '  backdrop-filter: blur(18px) saturate(1.4);',
    '  -webkit-backdrop-filter: blur(18px) saturate(1.4);',
    '  background: var(--bg-nav);',
    '  border-bottom: 1px solid var(--border);',
    '}',
    '.nav-logo {',
    '  font-family: var(--ff-serif);',
    '  font-size: 1.2rem; font-weight: 400;',
    '  letter-spacing: .02em; color: var(--accent);',
    '}',
    '.nav-links {',
    '  display: flex; gap: 2rem; list-style: none;',
    '  font-size: .78rem; font-weight: 500;',
    '  letter-spacing: .12em; text-transform: uppercase;',
    '  color: var(--muted);',
    '}',
    '.nav-links a:hover { color: var(--gold); transition: color .2s; }',
    '.nav-links a.active { color: var(--gold); }',
    '.nav-back {',
    '  display: flex; align-items: center; gap: .5rem;',
    '  font-size: .78rem; font-weight: 500;',
    '  letter-spacing: .1em; text-transform: uppercase;',
    '  color: var(--muted); transition: color .2s;',
    '}',
    '.nav-back:hover { color: var(--gold); }',
    '.nav-back svg { width: 14px; height: 14px; }',
    '@media (max-width: 900px) {',
    '  nav { padding: 1rem 1.5rem; }',
    '  .nav-links { gap: 1.2rem; font-size: .72rem; }',
    '}',

    /* ── Hamburger button — visibile solo su mobile ── */
    '.nav-hamburger {',
    '  display: none;',
    '  flex-direction: column;',
    '  justify-content: center;',
    '  align-items: center;',
    '  gap: 5px;',
    '  width: 36px; height: 36px;',
    '  background: none;',
    '  border: 1px solid var(--border);',
    '  border-radius: 8px;',
    '  cursor: pointer;',
    '  padding: 0;',
    '  transition: border-color .2s;',
    '}',
    '.nav-hamburger:hover { border-color: var(--gold-dim); }',
    '.nav-hamburger span {',
    '  display: block;',
    '  width: 16px; height: 1.5px;',
    '  background: var(--muted);',
    '  transition: all .22s ease;',
    '  transform-origin: center;',
    '}',
    /* Animazione → X quando aperto */
    '.nav-hamburger.open span:nth-child(1) { transform: translateY(6.5px) rotate(45deg); }',
    '.nav-hamburger.open span:nth-child(2) { opacity: 0; transform: scaleX(0); }',
    '.nav-hamburger.open span:nth-child(3) { transform: translateY(-6.5px) rotate(-45deg); }',

    /* ── Mobile menu drawer — appare sotto la nav ── */
    '.nav-mobile-menu {',
    '  position: fixed;',
    '  top: 57px;',            /* verrà sovrascritto in JS con la vera altezza nav */
    '  left: 0; right: 0;',
    '  z-index: 99;',
    '  background: var(--bg-nav);',
    '  backdrop-filter: blur(18px) saturate(1.4);',
    '  -webkit-backdrop-filter: blur(18px) saturate(1.4);',
    '  border-bottom: 1px solid var(--border);',
    '  max-height: 0;',
    '  overflow: hidden;',
    '  transition: max-height .28s ease, opacity .22s ease;',
    '  opacity: 0;',
    '  pointer-events: none;',
    '}',
    '.nav-mobile-menu.open {',
    '  max-height: 500px;',
    '  opacity: 1;',
    '  pointer-events: auto;',
    '}',
    '.nav-mobile-menu-inner {',
    '  padding: .6rem 1.5rem 1.2rem;',
    '}',
    '.nav-mobile-menu a {',
    '  display: flex;',
    '  align-items: center;',
    '  padding: .9rem 0;',
    '  font-size: .78rem;',
    '  font-weight: 500;',
    '  letter-spacing: .12em;',
    '  text-transform: uppercase;',
    '  color: var(--muted);',
    '  border-bottom: 1px solid var(--border);',
    '  transition: color .18s;',
    '}',
    '.nav-mobile-menu a:last-child { border-bottom: none; }',
    '.nav-mobile-menu a:hover { color: var(--gold); }',
    '.nav-mobile-menu a.active { color: var(--gold); }',

    '@media (max-width: 540px) {',
    '  .nav-links { display: none; }',
    '  .nav-hamburger { display: flex; }',
    '}',

    /* ─── DISCLAIMER ARTICOLO ─────────────────────────────────────────── */
    '.article-disclaimer {',
    '  margin-top: 3rem;',
    '  padding: 1.4rem 1.8rem;',
    '  background: var(--bg-card);',
    '  border: 1px solid var(--border);',
    '  border-radius: var(--radius);',
    '  border-left: 3px solid var(--gold-dim);',
    '}',
    '.disclaimer-label {',
    '  font-size: .68rem;',
    '  letter-spacing: .18em;',
    '  text-transform: uppercase;',
    '  color: var(--gold-dim);',
    '  margin-bottom: .75rem;',
    '}',
    '.disclaimer-text {',
    '  font-size: .78rem;',
    '  color: var(--muted);',
    '  line-height: 1.8;',
    '  margin-bottom: .6rem;',
    '}',
    ".disclaimer-text:last-child { margin-bottom: 0; }",
  ].join('\n');
  document.head.appendChild(s);
}());

/**
 * C. Google Fonts — preconnect + stylesheet, iniettati in modo sincrono
 *    per caricare i font prima del primo paint.
 */
(function injectFonts() {
  var pc1 = document.createElement('link');
  pc1.rel = 'preconnect';
  pc1.href = 'https://fonts.googleapis.com';

  var pc2 = document.createElement('link');
  pc2.rel = 'preconnect';
  pc2.href = 'https://fonts.gstatic.com';
  pc2.setAttribute('crossorigin', '');

  var lf = document.createElement('link');
  lf.rel = 'stylesheet';
  lf.href = LP_FONTS.googleUrl;

  document.head.appendChild(pc1);
  document.head.appendChild(pc2);
  document.head.appendChild(lf);
}());

/**
 * D. Nav HTML, Schema.org e Tracking — iniettati dopo che il DOM è pronto.
 */
document.addEventListener('DOMContentLoaded', function () {
  _injectNav();
  _injectSchemaOrg();
  _injectTracking();
  _injectDisclaimer();
});

/* ── D1. Nav HTML ─────────────────────────────────────────────────────────── */
function _injectNav() {
  var type   = window.LP_NAV_TYPE   || 'default';
  var active = window.LP_NAV_ACTIVE || '';
  var back   = window.LP_NAV_BACK   || { href: '/', label: 'Back' };

  var nav = document.createElement('nav');

  /* Logo */
  var logo = document.createElement('span');
  logo.className = 'nav-logo';
  logo.textContent = LP_NAV_LOGO;
  nav.appendChild(logo);

  if (type === 'back') {
    /* Paper / articolo — nav con back-link */
    var a = document.createElement('a');
    a.href = back.href;
    a.className = 'nav-back';
    a.innerHTML =
      '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">' +
      '<path d="M10 3L5 8l5 5"/></svg>' +
      back.label;
    nav.appendChild(a);

  } else {
    /* Default (EN) o Italiano — lista di link */
    var links = LP_NAV_LINKS[type] || LP_NAV_LINKS['default'];
    var isDefault = (type === 'default');

    if (isDefault) {
      /* ul > li > a  (nav principale inglese) */
      var ul = document.createElement('ul');
      ul.className = 'nav-links';
      links.forEach(function (link) {
        var li = document.createElement('li');
        var anchor = document.createElement('a');
        anchor.href = link.href;
        anchor.textContent = link.label;
        li.appendChild(anchor);
        ul.appendChild(li);
      });
      nav.appendChild(ul);

    } else {
      /* div > a  (nav italiana con supporto classe .active) */
      nav.setAttribute('aria-label', 'Navigazione principale');
      var div = document.createElement('div');
      div.className = 'nav-links';
      links.forEach(function (link) {
        var anchor = document.createElement('a');
        anchor.href = link.href;
        anchor.textContent = link.label;
        if (link.label === active) anchor.className = 'active';
        div.appendChild(anchor);
      });
      nav.appendChild(div);
    }

    /* ── Hamburger button (visibile solo su mobile via CSS) ──────────────── */
    var hamburger = document.createElement('button');
    hamburger.className = 'nav-hamburger';
    hamburger.setAttribute('aria-label', 'Apri menu di navigazione');
    hamburger.setAttribute('aria-expanded', 'false');
    /* Tre barre che animano in X */
    hamburger.innerHTML = '<span></span><span></span><span></span>';
    nav.appendChild(hamburger);

    /* ── Mobile menu drawer — inserito come figlio diretto di <body> ──────── */
    var mobileMenu = document.createElement('div');
    mobileMenu.className = 'nav-mobile-menu';
    mobileMenu.setAttribute('role', 'navigation');
    mobileMenu.setAttribute('aria-label', 'Navigazione mobile');

    var mobileInner = document.createElement('div');
    mobileInner.className = 'nav-mobile-menu-inner';

    /* Stessi link della nav desktop */
    links.forEach(function (link) {
      var a = document.createElement('a');
      a.href = link.href;
      a.textContent = link.label;
      if (link.label === active) a.className = 'active';
      /* Chiudi il menu al click su un link */
      a.addEventListener('click', function () {
        mobileMenu.classList.remove('open');
        hamburger.classList.remove('open');
        hamburger.setAttribute('aria-expanded', 'false');
      });
      mobileInner.appendChild(a);
    });

    mobileMenu.appendChild(mobileInner);

    /* ── Toggle logic ─────────────────────────────────────────────────────── */
    hamburger.addEventListener('click', function (e) {
      e.stopPropagation();
      var isOpen = mobileMenu.classList.toggle('open');
      hamburger.classList.toggle('open', isOpen);
      hamburger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    /* Chiudi cliccando fuori dal menu */
    document.addEventListener('click', function (e) {
      if (!nav.contains(e.target) && !mobileMenu.contains(e.target)) {
        mobileMenu.classList.remove('open');
        hamburger.classList.remove('open');
        hamburger.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* Inserisci come primo figlio di <body> */
  document.body.insertBefore(nav, document.body.firstChild);

  /* Inserisci il mobile menu dopo la nav e allineane il top alla vera altezza */
  if (typeof mobileMenu !== 'undefined') {
    document.body.insertBefore(mobileMenu, nav.nextSibling);
    /* Aggiorna il top dinamicamente in base all'altezza reale della nav */
    requestAnimationFrame(function () {
      mobileMenu.style.top = nav.offsetHeight + 'px';
    });
    /* Ricalcola al resize (orientamento, zoom) */
    window.addEventListener('resize', function () {
      mobileMenu.style.top = nav.offsetHeight + 'px';
    });
  }
}

/* ── D2. Schema.org Person + WebSite ─────────────────────────────────────── */
function _injectSchemaOrg() {
  /* Se la homepage ha già un blocco JSON-LD statico (data-lp-static="1"),
     non iniettare un duplicato. La pagina è già ottimizzata per il crawling
     di prima ondata. Tutte le altre pagine ricevono l'iniezione normale. */
  if (document.querySelector('script[type="application/ld+json"][data-lp-static]')) return;
  var script = document.createElement('script');
  script.type = 'application/ld+json';
  script.textContent = JSON.stringify(LP_SCHEMA, null, 2);
  document.head.appendChild(script);
}

/* ── D3. Tracking pixels ─────────────────────────────────────────────────── */
function _injectTracking() {

  /* Google Analytics 4 */
  if (LP_TRACKING.ga4) {
    var gaSrc = document.createElement('script');
    gaSrc.async = true;
    gaSrc.src = 'https://www.googletagmanager.com/gtag/js?id=' + LP_TRACKING.ga4;
    document.head.appendChild(gaSrc);

    var gaInit = document.createElement('script');
    gaInit.textContent =
      'window.dataLayer = window.dataLayer || [];\n' +
      'function gtag(){dataLayer.push(arguments);}\n' +
      "gtag('js', new Date());\n" +
      "gtag('config', '" + LP_TRACKING.ga4 + "');";
    document.head.appendChild(gaInit);
  }

  /* Meta (Facebook) Pixel */
  if (LP_TRACKING.metaPixel) {
    var fbInit = document.createElement('script');
    fbInit.textContent =
      '!function(f,b,e,v,n,t,s){\n' +
      'if(f.fbq)return;n=f.fbq=function(){n.callMethod?\n' +
      'n.callMethod.apply(n,arguments):n.queue.push(arguments)};\n' +
      "if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';\n" +
      'n.queue=[];t=b.createElement(e);t.async=!0;\n' +
      't.src=v;s=b.getElementsByTagName(e)[0];\n' +
      "s.parentNode.insertBefore(t,s)}(window,document,'script',\n" +
      "'https://connect.facebook.net/en_US/fbevents.js');\n" +
      "fbq('init','" + LP_TRACKING.metaPixel + "');\n" +
      "fbq('track','PageView');";
    document.body.appendChild(fbInit);

    var ns = document.createElement('noscript');
    var img = document.createElement('img');
    img.height = 1;
    img.width = 1;
    img.style.display = 'none';
    img.src = 'https://www.facebook.com/tr?id=' + LP_TRACKING.metaPixel + '&ev=PageView&noscript=1';
    ns.appendChild(img);
    document.body.appendChild(ns);
  }
}

/* ── D4. Disclaimer personale ────────────────────────────────────────────── */
function _injectDisclaimer() {
  /* Cerca il tag <article> nella pagina.
     Se non c'è (es. homepage, papers) la funzione esce silenziosamente. */
  var article = document.querySelector('article');
  if (!article) return;

  /* Evita di iniettare due volte (es. se il file ha ancora il blocco statico) */
  if (article.querySelector('.article-disclaimer')) return;

  var div = document.createElement('div');
  div.className = 'article-disclaimer';
  div.innerHTML =
    '<p class="disclaimer-label">Disclaimer</p>' +
    '<p class="disclaimer-text">' +
      'Le opinioni espresse in questo sito, e in qualsiasi altra sede — online, offline o pubblica — ' +
      'incluse, senza limitazione alcuna, posizioni politiche, valutazioni sociali e giudizi di qualsiasi natura, ' +
      'sono esclusivamente e strettamente personali di Ludovico Papalia. ' +
      'Esse non sono in alcun modo riconducibili, né devono essere associate, a persone, istituzioni, enti, ' +
      'organizzazioni o editori con cui Ludovico Papalia collabora, ha collaborato o ha pubblicato.' +
    '</p>' +
    '<p class="disclaimer-text">' +
      'The views expressed on this website, and in any other context — online, offline, or public — ' +
      'including, without limitation, political positions, social assessments, and judgments of any kind, ' +
      'are solely and strictly personal to Ludovico Papalia. ' +
      'They are in no way attributable to, nor should they be associated with, any persons, institutions, ' +
      'entities, organizations, or publishers with whom Ludovico Papalia collaborates, has collaborated, or has published.' +
    '</p>';

  /* Appende come ultimo figlio di <article>, prima del footer di pagina */
  article.appendChild(div);
}


