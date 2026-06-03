# Design System Audit — bracakumerle.com
**Date:** 2026-06-03  
**Status:** READ-ONLY audit — no changes made  
**Auditor:** Design System V1 pass

---

## 1. Template Inventory

| URL path | Header type | Nav type | Footer type | CSS bundle | Hero type | Schema.org type |
|---|---|---|---|---|---|---|
| `/` | none | footer-only | inline-custom | inline-only | dark-hero (fullscreen) | MusicGroup |
| `/bio` | pipe-nav | pipe-nav | minimal | `style.css` | h1-only | AboutPage |
| `/diskografija` | pipe-nav | pipe-nav | minimal | `style.css` | h1-only | CollectionPage |
| `/arhiva` | pipe-nav | pipe-nav | minimal | `/style.css` | h1-only | BreadcrumbList only |
| `/vizualni-identitet` | custom `.site-header` | single-link | custom `.page-footer` | inline-only + Google Fonts | dark-hero (editorial) | AboutPage |
| `/lyrics/` | none | pipe-nav (abs) | minimal | **none** | none | CollectionPage |
| `/lyrics/krijesovi-lazi` | none | pipe-nav (abs) | minimal | **none** | h1-only (in `<main>`) | CreativeWork + BreadcrumbList |
| `/lyrics/moj-dinamo` | none | pipe-nav (abs) | minimal | **none** | h1-only (in `<main>`) | CreativeWork + BreadcrumbList |
| `/pjesme/krijesovi-lazi` | `bk-site-header` | `bk-site-nav` | `bk-site-footer` | `global.css` + inline | dark-hero (bk-hero) | MusicRecording |
| `/pjesme/zalo` | custom `.site-header` | breadcrumb | custom `.page-footer` | inline-only + Google Fonts | dark-hero (bk-hero) | MusicRecording |
| `/pjesme/cast` | `bk-site-header` | `bk-site-nav` | `bk-site-footer` | `global.css` + inline | dark-hero (bk-hero) | MusicRecording |
| `/pjesme/moj-dinamo` | `bk-site-header` | `bk-site-nav` | `bk-site-footer` | `global.css` + inline | dark-hero (bk-hero) | MusicRecording |
| `/en/` | none | pipe-nav (abs, EN) | minimal (EN) | **none** | h1-only (in `<header>`) | WebPage + MusicGroup |

**Notes:**
- `/vizualni-identitet` exists at root as `vizualni-identitet.html`, not at `vizualni-identitet/index.html`
- All `/pjesme/*` files are flat `.html` files, not subdirectory `index.html` files
- The lyrics subpages (`/lyrics/*/index.html`) carry zero CSS — no stylesheet linked, no inline styles

---

## 2. Shared Components

### Truly shared (single source, copied via inclusion)
- **None.** The site has no server-side includes, no JS component system, and no build-time templating. Every "shared" element is copy-pasted HTML.

### Copy-pasted components (exist in multiple files, maintained manually)

| Component | Files using it | Notes |
|---|---|---|
| `bk-site-header` + `bk-site-nav` | `pjesme/krijesovi-lazi`, `cast`, `moj-dinamo`, `frane-tente`, `sjever-uz-odsutne`, `u-svijetu-bajki`, `znakovlje-hrvata` | Defined in `global.css`; each page copies the HTML block |
| `bk-site-footer` | Same 7 files above | Defined in `global.css`; copy-pasted in each |
| pipe-nav `<header><nav>` | `bio`, `diskografija`, `arhiva/index`, `arhiva/leteci-majmuni-2012`, `arhiva/dallas-records-era`, `arhiva/cmc-demo-2009`, `pjesme/strice-ivane` | Identical HTML, relative paths |
| Minimal `<footer><p>…</p></footer>` | `bio`, `diskografija`, `arhiva/*`, `lyrics/index`, `lyrics/krijesovi-lazi`, `lyrics/moj-dinamo` | Each has slightly different link sets |
| Inline `bk-hero` CSS | All `pjesme/*` (except `zalo`) | ~600 chars of identical CSS duplicated per file |
| `docs/shared-nav.html` | Reference file only — **never actually included anywhere** | Exists as a copy-paste source document |

---

## 3. Divergences

### DIV-001 — Recording page: two different header/nav/footer implementations

**Problem:** Same page type (MusicRecording), two different chrome implementations.

| File | Header | Nav | Footer | CSS |
|---|---|---|---|---|
| `pjesme/krijesovi-lazi`, `cast`, `moj-dinamo`, `frane-tente`, `sjever-uz-odsutne`, `u-svijetu-bajki`, `znakovlje-hrvata` | `bk-site-header` | `bk-site-nav` (dots) | `bk-site-footer` | `global.css` + inline |
| `pjesme/zalo` | custom `.site-header` | `.breadcrumb` (›) | custom `.page-footer` | inline-only + Google Fonts |

`zalo.html` is an isolated legacy outlier built on a different CSS system entirely.

---

### DIV-002 — CSS custom property namespace: two systems

| System | Files | Custom properties |
|---|---|---|
| `global.css` system | Modern `pjesme/*` | `--bk-bijela`, `--bk-plava`, `--bk-zlatna`, `--bk-tekst`, `--font-body`, etc. |
| Local `:root` system | `zalo.html`, `vizualni-identitet.html` | `--plava`, `--bijela`, `--zlatna`, `--tekst`, etc. (no `bk-` prefix) |

These are semantically equivalent but incompatible — cannot share CSS rules across systems.

---

### DIV-003 — Three different footer implementations

1. **`bk-site-footer`** — 3-column structured footer with `bk-footer-col` grid. Used on modern `pjesme/*`.
2. **Custom `.page-footer`** — Similar 3-column blue footer but own CSS, own class names. Used on `zalo.html` and `vizualni-identitet.html`.
3. **Minimal `<footer><p>…</p></footer>`** — Flat text with inline links. Used on `bio`, `diskografija`, `arhiva/*`, `lyrics/*`.
4. **Footer-nav only** — `index.html` has no semantic `<header>`, footer `<nav>` only.

---

### DIV-004 — Lyrics subpages missing nav Tekstovi update

`/lyrics/krijesovi-lazi/index.html` and `/lyrics/moj-dinamo/index.html` still carry the old nav without the Tekstovi link added in WEB-WIRE-001. These pages share the same pipe-nav pattern as `lyrics/index.html` but were not in the WEB-WIRE-001 file list.

---

### DIV-005 — Lyrics subpages: zero CSS

`/lyrics/*/index.html` pages have no stylesheet at all — no `<link>` tag, no `<style>` block. They render with browser defaults only. All other pages on the site have at least one CSS source.

---

### DIV-006 — Schema.org: `arhiva/index.html` has no page-level type

Only has a `BreadcrumbList`. No `CollectionPage`, `AboutPage`, or equivalent. Every other audited page has at least one non-breadcrumb type.

---

### DIV-007 — Absolute vs. relative nav URLs

| Pages | URL style in nav |
|---|---|
| `bio`, `diskografija`, `arhiva/*`, `strice-ivane` | Relative: `/bio`, `/diskografija` |
| `lyrics/index`, `lyrics/*/index`, `en/index` | Absolute: `https://bracakumerle.com/bio` |
| `pjesme/*` (bk-site-nav) | Absolute: `https://bracakumerle.com/diskografija` |

No consistent convention. Relative URLs are safer for local development; absolute URLs break nothing in production but are redundant.

---

## 4. Page Archetypes

### Archetype A — `landing`
**Canonical URL:** `/`  
**Purpose:** Entry point, streaming links, entity graph  
**Characteristics:** Full-viewport dark hero, no site header, footer-nav only, self-contained inline CSS, MusicGroup schema  
**Files:** `index.html`

---

### Archetype B — `knowledge-object`
**Canonical URL:** `/pjesme/{slug}`  
**Purpose:** Authoritative recording page — ISRC, identifiers, context, media refs  
**Characteristics:** `bk-site-header` + `bk-site-nav`, dark bk-hero with title + ID badge, 2-col main grid (content + aside), `bk-site-footer`, `global.css` + inline, MusicRecording schema  
**Files:** `pjesme/krijesovi-lazi`, `cast`, `moj-dinamo`, `frane-tente`, `sjever-uz-odsutne`, `u-svijetu-bajki`, `znakovlje-hrvata`  
**Outlier:** `pjesme/zalo` (same purpose, legacy implementation)

---

### Archetype C — `corpus-index`
**Canonical URL:** `/lyrics/`, `/diskografija`  
**Purpose:** Listing / index of a content collection  
**Characteristics:** Simple header, table or list of entries, CollectionPage schema  
**Files:** `lyrics/index.html`, `diskografija.html`  
**Note:** These two differ in CSS (`style.css` vs. none) and header type — not yet converged

---

### Archetype D — `corpus-entry`
**Canonical URL:** `/lyrics/{slug}`  
**Purpose:** Canonical text/lyrics object with full content, thematic metadata, and reciprocal links  
**Characteristics:** No CSS (bare HTML), pipe-nav, minimal footer, CreativeWork + BreadcrumbList schema, lyrics body as `<article>`  
**Files:** `lyrics/krijesovi-lazi/index.html`, `lyrics/moj-dinamo/index.html` (and all others)  
**Status:** Functional but unstyled — browser-default rendering

---

### Archetype E — `editorial`
**Canonical URL:** `/bio`, `/arhiva`, `/arhiva/*`  
**Purpose:** Prose/narrative pages — band biography, archive context documents  
**Characteristics:** pipe-nav, `style.css`, h1-only, minimal footer, various schemas  
**Files:** `bio.html`, `arhiva/index.html`, `arhiva/leteci-majmuni-2012.html`, `arhiva/dallas-records-era.html`, `arhiva/cmc-demo-2009.html`

---

### Archetype F — `editorial-rich`
**Canonical URL:** `/vizualni-identitet`  
**Purpose:** Long-form editorial document with ToC, epoch tables, pull quotes  
**Characteristics:** Custom site-header, sticky ToC nav, elaborate dark hero, 3-col footer, inline CSS only  
**Files:** `vizualni-identitet.html`  
**Note:** Highest visual quality on the site; entirely self-contained; no relation to `global.css`

---

### Archetype G — `en-mirror`
**Canonical URL:** `/en/`, `/en/biography/`, `/en/discography/`  
**Purpose:** English-language landing and content mirror  
**Characteristics:** Bare HTML, pipe-nav (English), no CSS, minimal footer  
**Files:** `en/index.html`, `en/biography/index.html`, `en/discography/index.html`  
**Status:** Placeholder quality — minimal content, no styling

---

## 5. Migration Matrix

| Current template | Target archetype | Key changes needed | Effort |
|---|---|---|---|
| `index.html` (landing) | `landing` — already canonical | None | — |
| `pjesme/krijesovi-lazi` et al. (bk-site-nav) | `knowledge-object` — already canonical | None | — |
| `pjesme/zalo` (legacy recording) | `knowledge-object` | Replace `.site-header`/breadcrumb with `bk-site-header`/`bk-site-nav`; replace inline CSS with `global.css`; replace `.page-footer` with `bk-site-footer` | **medium** |
| `diskografija.html` (editorial) | `corpus-index` | Add `bk-site-header`; migrate `style.css` → `global.css`; upgrade footer | **medium** |
| `lyrics/index.html` (corpus-index) | `corpus-index` | Add full CSS; add `bk-site-header` (or at minimum styled nav) | **medium** |
| `lyrics/*/index.html` (corpus-entry) | `corpus-entry` | Add CSS (new `lyrics.css` or `global.css`); add `bk-site-header`; add Tekstovi to nav | **high** |
| `bio.html` (editorial) | `editorial` | Migrate `style.css` → `global.css`; add `bk-site-header`; upgrade footer | **medium** |
| `arhiva/index.html` (editorial) | `editorial` | Same as bio; add CollectionPage schema | **medium** |
| `arhiva/leteci-majmuni-2012`, `dallas-records-era`, `cmc-demo-2009` | `editorial` | Same as arhiva/index | **medium** (×3) |
| `vizualni-identitet.html` (editorial-rich) | `editorial-rich` — already canonical of its own kind | Optionally migrate `:root` vars to `global.css` namespace | **low** |
| `en/index.html` et al. (en-mirror) | `en-mirror` | Full restyle; English bk-site-header equivalent | **high** |

---

## 6. Canonical Component Spec

Derived from the best existing implementation: the `bk-site-nav` family (`global.css` + `pjesme/*`).

---

### Canonical Header HTML

```html
<header class="bk-site-header">
  <div class="bk-site-header-inner">
    <a href="https://bracakumerle.com" class="bk-logo">i<span>ZLET</span></a>
    <nav class="bk-site-nav" aria-label="Glavna navigacija">
      <a href="https://bracakumerle.com">Početna</a>
      <span class="nav-separator">·</span>
      <a href="https://bracakumerle.com/diskografija">Diskografija</a>
      <span class="nav-separator">·</span>
      <a href="https://bracakumerle.com/lyrics/">Tekstovi</a>
      <span class="nav-separator">·</span>
      <a href="https://bracakumerle.com/video">Video</a>
      <span class="nav-separator">·</span>
      <a href="https://bracakumerle.com/vizualni-identitet">Vizualni identitet</a>
      <span class="nav-separator">·</span>
      <a href="https://bracakumerle.com/kontakt">Kontakt</a>
    </nav>
  </div>
</header>
```

**Active page:** Add `class="active"` to the matching `<a>` tag for current-page highlighting.

---

### Canonical Nav HTML

The nav lives inside the header above. The dot-separator pattern is the canonical form:

```html
<nav class="bk-site-nav" aria-label="Glavna navigacija">
  <a href="…">Label</a>
  <span class="nav-separator">·</span>
  <a href="…">Label</a>
  <!-- repeat -->
</nav>
```

**Do not use:** pipe `|` separators (legacy pattern), single-link nav (vizualni-identitet outlier), or bare `<nav>` without `aria-label`.

---

### Canonical Footer HTML

```html
<footer class="bk-site-footer">
  <div class="bk-site-footer-inner">

    <div class="bk-footer-col">
      <p class="bk-footer-col-title">iZLET</p>
      <a href="https://bracakumerle.com/diskografija">Diskografija</a>
      <a href="https://bracakumerle.com/lyrics/">Tekstovi</a>
      <a href="https://bracakumerle.com/video">Video</a>
      <a href="https://bracakumerle.com/bio">O bendu</a>
      <a href="https://bracakumerle.com/vizualni-identitet">Vizualni identitet</a>
    </div>

    <div class="bk-footer-col">
      <p class="bk-footer-col-title">Vanjski registri</p>
      <a href="https://www.wikidata.org/wiki/Q139595518" target="_blank" rel="noopener">Wikidata</a>
      <a href="https://musicbrainz.org/artist/b973e6f2-c282-473a-b2fb-ffb4466b312f" target="_blank" rel="noopener">MusicBrainz</a>
      <a href="https://www.discogs.com/artist/6610944" target="_blank" rel="noopener">Discogs</a>
      <a href="https://open.spotify.com/artist/11wCFDSyZy0LfWkgllak6d" target="_blank" rel="noopener">Spotify</a>
      <a href="https://www.youtube.com/@bracakumerle" target="_blank" rel="noopener">YouTube</a>
    </div>

    <div class="bk-footer-col">
      <p class="bk-footer-col-title">Kontakt</p>
      <a href="mailto:izletband@gmail.com">izletband@gmail.com</a>
      <a href="https://www.youtube.com/@bracakumerle" target="_blank" rel="noopener">@bracakumerle</a>
    </div>

  </div>
  <div class="bk-footer-bottom">
    <span class="bk-footer-bottom-text">© Braća Kumerle · Zagreb · 2026.</span>
  </div>
</footer>
```

**Note:** The current footer copies in `pjesme/*` do not include a "Tekstovi" link in the iZLET column. This should be added when the footer is next updated.

---

### Required CSS

All canonical components require `global.css` to be linked in `<head>`:

```html
<link rel="stylesheet" href="/global.css">
```

`global.css` provides:
- CSS custom properties: `--bk-bijela`, `--bk-plava`, `--bk-zlatna`, `--bk-tekst`, `--bk-tekst-svjetli`, `--bk-separator`, `--bk-bijela-hladna`, `--bk-zlatna-svijetla`, `--font-body`, `--font-serif`, `--max-width-wide`
- Layout classes: `.bk-site-header`, `.bk-site-header-inner`, `.bk-logo`, `.bk-site-nav`, `.nav-separator`
- Footer classes: `.bk-site-footer`, `.bk-site-footer-inner`, `.bk-footer-col`, `.bk-footer-col-title`, `.bk-footer-bottom`, `.bk-footer-bottom-text`

Pages may add inline `<style>` blocks for page-specific layout (hero grid, data-table, sidebar) on top of `global.css`.

---

*End of audit — 2026-06-03*
