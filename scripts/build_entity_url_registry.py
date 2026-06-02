"""
build_entity_url_registry.py
Generates Entity URL Registry v1 from all HTML files in the repo.
Output: registries/entity_url_registry_v1.csv
        registries/entity_url_registry_v1_report.md
"""
import sys, io, os, re, json, csv
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent.parent

# ── Skip list ──────────────────────────────────────────────────────────────────
SKIP = {"docs/shared-nav.html", "izlet_os/index.html", "dashboard.html"}

# ── URL mapping ────────────────────────────────────────────────────────────────
def file_to_url(rel: str) -> str:
    r = rel.replace("\\", "/")
    if r == "index.html":                return "/"
    if r == "bio.html":                  return "/bio"
    if r == "diskografija.html":         return "/diskografija"
    if r == "kontakt.html":              return "/kontakt"
    if r == "video.html":                return "/video"
    if r == "vizualni-identitet.html":   return "/vizualni-identitet"
    if r == "arhiva/index.html":         return "/arhiva"
    if r.startswith("arhiva/"):          return "/" + r.replace(".html", "")
    if r == "en/index.html":             return "/en/"
    if r == "en/biography/index.html":   return "/en/biography/"
    if r == "en/discography/index.html": return "/en/discography/"
    if r.startswith("pjesme/"):          return "/" + r.replace(".html", "")
    return "/" + r.replace(".html", "")

# ── Fond classification ────────────────────────────────────────────────────────
def classify_fond(url: str, html: str) -> str:
    if url.startswith("/pjesme/"):    return "Songs"
    if url.startswith("/en/"):        return "Root"
    if url.startswith("/arhiva/") and url != "/arhiva":
        lh = html.lower()
        if "musicalbum" in lh or "album" in lh[:3000]:
            return "Releases"
        return "Events"
    return "Root"

# ── Schema type inference ──────────────────────────────────────────────────────
def infer_schema(url, html, jsonld_types):
    if jsonld_types:
        # prefer the most specific
        for t in ["MusicRecording","MusicAlbum","MusicRelease","AboutPage",
                  "CollectionPage","WebPage","MusicGroup","CreativeWork"]:
            if t in jsonld_types:
                return t
    fond = classify_fond(url, html)
    mapping = {
        "Songs": "MusicRecording",
        "Releases": "MusicAlbum",
        "Events": "Event",
        "Visual": "CreativeWork",
        "Root": "WebPage",
    }
    return mapping.get(fond, "WebPage")

# ── Canonical entity ID ────────────────────────────────────────────────────────
def canonical_id(url, fond):
    slug = url.strip("/").split("/")[-1].replace("-", "_")
    if not slug:
        slug = "homepage"
    prefix = {
        "Songs": "work",
        "Releases": "release",
        "Events": "event",
        "Visual": "visual",
        "People": "person",
        "Root": "hub",
    }.get(fond, "hub")
    return f"{prefix}:{slug}"

# ── Identifier extraction ──────────────────────────────────────────────────────
ISRC_RE  = re.compile(r'\b([A-Z]{2}[A-Z0-9]{3}\d{2}\d{5})\b')
UPC_RE   = re.compile(r'\b(\d{12,13})\b')
WD_RE    = re.compile(r'Q\d{6,9}')
MB_RE    = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
SP_RE    = re.compile(r'open\.spotify\.com/(?:track|album|artist)/([A-Za-z0-9]+)')

def extract_identifiers(html):
    ids = []
    for m in ISRC_RE.finditer(html):
        v = m.group(1)
        if v not in ("UTF8", "UTF16"):
            ids.append(f"ISRC:{v}")
    for m in WD_RE.finditer(html):
        ids.append(f"WD:{m.group()}")
    for m in MB_RE.finditer(html):
        ids.append(f"MB:{m.group()}")
    for m in SP_RE.finditer(html):
        ids.append(f"SP:{m.group(1)}")
    # deduplicate preserving order
    seen = set(); out = []
    for x in ids:
        if x not in seen:
            seen.add(x); out.append(x)
    return "; ".join(out[:6])  # cap to keep CSV readable

# ── JSON-LD parsing ────────────────────────────────────────────────────────────
def _collect_same_as(obj, results):
    """Recursively collect all sameAs values from any level of a JSON-LD object."""
    if isinstance(obj, dict):
        if "sameAs" in obj:
            sa = obj["sameAs"]
            results += sa if isinstance(sa, list) else [sa]
        for v in obj.values():
            _collect_same_as(v, results)
    elif isinstance(obj, list):
        for item in obj:
            _collect_same_as(item, results)


def parse_jsonld(html):
    types, same_as = [], []
    blocks = re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.S)
    for block in blocks:
        try:
            data = json.loads(block.strip())
            items = data if isinstance(data, list) else [data]
            for item in items:
                if "@type" in item:
                    t = item["@type"]
                    types += (t if isinstance(t, list) else [t])
            _collect_same_as(data, same_as)
        except Exception:
            pass
    return types, same_as

# ── Title extraction ───────────────────────────────────────────────────────────
def extract_title(html):
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.S)
    if m:
        return re.sub(r'\s+', ' ', m.group(1)).strip()
    m2 = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
    if m2:
        return re.sub(r'<[^>]+>', '', m2.group(1)).strip()
    return ""

# ── Year extraction ────────────────────────────────────────────────────────────
def extract_year(html, url):
    m = re.search(r'"datePublished":\s*"(\d{4})', html)
    if m: return m.group(1)
    m2 = re.search(r'\b(200[7-9]|20[12]\d)\b', html)
    if m2: return m2.group(1)
    return ""

# ── Main ───────────────────────────────────────────────────────────────────────
rows = []
all_html_files = sorted([
    f for f in ROOT.rglob("*.html")
    if not any(skip in str(f) for skip in ["node_modules", ".next", ".git"])
])

for fpath in all_html_files:
    rel = str(fpath.relative_to(ROOT)).replace("\\", "/")
    if rel in SKIP:
        continue

    html = fpath.read_text(encoding="utf-8", errors="replace")
    url  = file_to_url(rel)
    fond = classify_fond(url, html)
    jsonld_types, same_as = parse_jsonld(html)
    schema_tip = infer_schema(url, html, jsonld_types)
    ceid = canonical_id(url, fond)
    title = extract_title(html)
    year  = extract_year(html, url)
    ids   = extract_identifiers(html)

    # Extract entity name from title
    name = re.sub(r'\s*[|—–-].*$', '', title).strip()

    rows.append({
        "url":                  url,
        "fond":                 fond,
        "naziv_entiteta":       name,
        "canonical_entity_id":  ceid,
        "schema_tip":           schema_tip,
        "godina":               year,
        "status":               "Live",
        "identifikatori":       ids,
        "sameAs_count":         len(same_as),
        "napomena":             "",
    })

# ── Known stubs (appear in nav/text but no HTML file) ─────────────────────────
STUBS = [
    {"url": "/petar",        "fond": "People",   "naziv_entiteta": "Petar Kumerle",  "canonical_entity_id": "person:petar_kumerle",  "schema_tip": "Person",       "godina": "", "status": "Stub", "identifikatori": "WD:Q139595619; MB:9ab299e2; Discogs:17042197", "sameAs_count": 0, "napomena": "Linked from master_registry; no HTML"},
    {"url": "/toni",         "fond": "People",   "naziv_entiteta": "Toni Kumerle",   "canonical_entity_id": "person:toni_kumerle",   "schema_tip": "Person",       "godina": "", "status": "Stub", "identifikatori": "WD:Q139595627; MB:b134ce50",                  "sameAs_count": 0, "napomena": "Linked from master_registry; no HTML"},
    {"url": "/bkm",          "fond": "Root",     "naziv_entiteta": "Braća Kumerle Music", "canonical_entity_id": "hub:bkm",         "schema_tip": "Organization", "godina": "", "status": "Stub", "identifikatori": "Discogs:4368922",                              "sameAs_count": 0, "napomena": "Label entity; no HTML"},
    {"url": "/pjesme/znakovlje-hrvata", "fond": "Songs", "naziv_entiteta": "Znakovlje Hrvata",  "canonical_entity_id": "work:znakovlje_hrvata",  "schema_tip": "MusicRecording", "godina": "2021", "status": "Stub", "identifikatori": "MB:multiple refs",  "sameAs_count": 0, "napomena": "High corpus score, multiple YT refs"},
    {"url": "/pjesme/isuse-moj",       "fond": "Songs", "naziv_entiteta": "Isuse moj",           "canonical_entity_id": "work:isuse_moj",          "schema_tip": "MusicRecording", "godina": "2026", "status": "Stub", "identifikatori": "",                   "sameAs_count": 0, "napomena": "BKM singl 2026"},
    {"url": "/pjesme/vitez-jure",      "fond": "Songs", "naziv_entiteta": "Vitez Jure",          "canonical_entity_id": "work:vitez_jure",         "schema_tip": "MusicRecording", "godina": "2025", "status": "Stub", "identifikatori": "MB:807abd53",        "sameAs_count": 0, "napomena": "BKM singl; MB recording confirmed"},
    {"url": "/arhiva/katarza-2019",    "fond": "Releases", "naziv_entiteta": "Katarza",         "canonical_entity_id": "release:katarza",         "schema_tip": "MusicAlbum",     "godina": "2019", "status": "Stub", "identifikatori": "Discogs:35923165",   "sameAs_count": 0, "napomena": "Dallas Records album; Discogs ID in works_registry"},
    {"url": "/arhiva/nikad-ne-znas-2016", "fond": "Releases", "naziv_entiteta": "Nikad ne znaš, to je ono…", "canonical_entity_id": "release:nikad_ne_znas", "schema_tip": "MusicAlbum", "godina": "2016", "status": "Stub", "identifikatori": "Discogs:12898284", "sameAs_count": 0, "napomena": "Dallas Records album; in JSON-LD na index.html"},
    {"url": "/arhiva/ti-si-cudesna",   "fond": "Songs",    "naziv_entiteta": "Ti si čudesna",   "canonical_entity_id": "work:ti_si_cudesna",      "schema_tip": "MusicRecording", "godina": "2009", "status": "Stub", "identifikatori": "ISRC:HRA371600088; SP:3aqsGyAU8uZ7gLJLRIsR06", "sameAs_count": 0, "napomena": "CMC Demo 2009; highest authority_score=80"},
    {"url": "/pjesme/sjever-uz-odsutne", "fond": "Songs",  "naziv_entiteta": "Sjever uz odsutne", "canonical_entity_id": "work:sjever_uz_odsutne", "schema_tip": "MusicRecording", "godina": "2023", "status": "Live", "identifikatori": "", "sameAs_count": 0, "napomena": ""},
]

# Merge stubs (avoid duplicates with live pages)
live_urls = {r["url"] for r in rows}
for stub in STUBS:
    if stub["url"] not in live_urls:
        rows.append(stub)

# Sort
ORDER = ["Root", "Songs", "Releases", "Events", "Visual", "People", "Sources"]
rows.sort(key=lambda r: (ORDER.index(r["fond"]) if r["fond"] in ORDER else 99, r["url"]))

# ── Write CSV ──────────────────────────────────────────────────────────────────
CSV_PATH = ROOT / "registries" / "entity_url_registry_v1.csv"
FIELDS = ["url","fond","naziv_entiteta","canonical_entity_id","schema_tip","godina","status","identifikatori","sameAs_count","napomena"]
with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows)
print(f"CSV: {CSV_PATH} ({len(rows)} rows)")

# ── Analysis ───────────────────────────────────────────────────────────────────
live = [r for r in rows if r["status"] == "Live"]
stubs = [r for r in rows if r["status"] == "Stub"]
by_fond = {}
for r in rows:
    by_fond.setdefault(r["fond"], []).append(r)

isolated = [r for r in rows if r["sameAs_count"] == 0]
isrc_no_jsonld = [r for r in rows if "ISRC:" in r["identifikatori"] and r["sameAs_count"] == 0]

# ── Write report ───────────────────────────────────────────────────────────────
MD_PATH = ROOT / "registries" / "entity_url_registry_v1_report.md"
with open(MD_PATH, "w", encoding="utf-8") as f:
    f.write("# Entity URL Registry v1 — Report\n\n")
    f.write(f"**Generated:** 2026-06-03  \n")
    f.write(f"**Total entries:** {len(rows)} ({len(live)} Live, {len(stubs)} Stub)  \n\n")

    f.write("## Fond Summary\n\n")
    f.write("| Fond | Total | Live | Stub |\n|---|---|---|---|\n")
    for fond in ORDER:
        items = by_fond.get(fond, [])
        lv = sum(1 for x in items if x["status"] == "Live")
        st = sum(1 for x in items if x["status"] == "Stub")
        f.write(f"| {fond} | {len(items)} | {lv} | {st} |\n")
    f.write("\n")

    f.write("## === STUB CANDIDATES ===\n\n")
    f.write("| Naziv | Status | Preporučeni URL | Preporučeni schema | Napomena |\n|---|---|---|---|---|\n")
    for r in stubs:
        f.write(f"| {r['naziv_entiteta']} | Stub | {r['url']} | {r['schema_tip']} | {r['napomena']} |\n")
    f.write("\n")

    f.write("## === GAP ANALYSIS ===\n\n")
    empty_fonds = [fond for fond in ORDER if not by_fond.get(fond)]
    under_fonds = [fond for fond in ORDER if 0 < len(by_fond.get(fond, [])) <= 2]
    f.write(f"**Fondovi s 0 URL-ova:** {', '.join(empty_fonds) or 'none'}\n\n")
    f.write(f"**Fondovi s 1-2 URL-a (underdeveloped):** {', '.join(under_fonds) or 'none'}\n\n")
    f.write(f"**Izolirani čvorovi (sameAs=0):** {len(isolated)}\n")
    for r in isolated[:15]:
        f.write(f"  - {r['url']} [{r['fond']}]\n")
    f.write(f"\n**Imaju ISRC ali sameAs=0:** {len(isrc_no_jsonld)}\n")
    for r in isrc_no_jsonld:
        f.write(f"  - {r['url']} — {r['identifikatori'][:60]}\n")
    f.write("\n")

    f.write("## === P0.2 BACKLOG ===\n\n")
    f.write("Top 10 URL-ova za izgraditi:\n\n")
    f.write("| # | URL | Naziv | Fond | Identifikatori | Razlog prioriteta |\n|---|---|---|---|---|---|\n")
    backlog = sorted(stubs, key=lambda r: (
        -len(r["identifikatori"]),
        r["url"]
    ))[:10]
    for i, r in enumerate(backlog, 1):
        reason = "identifikatori poznati" if r["identifikatori"] else "stub u nav/JSON-LD"
        f.write(f"| {i} | {r['url']} | {r['naziv_entiteta']} | {r['fond']} | {r['identifikatori'][:50]} | {reason} |\n")
    f.write("\n")

print(f"Report: {MD_PATH}")

# ── Console summary ────────────────────────────────────────────────────────────
print()
print("=== FOND SUMMARY ===")
for fond in ORDER:
    items = by_fond.get(fond, [])
    lv = sum(1 for x in items if x["status"] == "Live")
    st = sum(1 for x in items if x["status"] == "Stub")
    print(f"  {fond:<12} total={len(items):>2}  live={lv}  stub={st}")

print()
print("=== STUB CANDIDATES ===")
for r in stubs:
    print(f"  {r['url']:<40} {r['schema_tip']:<20} {r['identifikatori'][:40]}")

print()
print("=== GAP ANALYSIS ===")
print(f"  Fondovi s 0 URL-ova:      {', '.join(empty_fonds) or 'none'}")
print(f"  Fondovi underdeveloped:   {', '.join(under_fonds) or 'none'}")
print(f"  Izolirani čvorovi:        {len(isolated)}")
print(f"  ISRC bez sameAs:          {len(isrc_no_jsonld)}")

print()
print("=== P0.2 BACKLOG (top 10) ===")
for i, r in enumerate(backlog, 1):
    print(f"  {i:>2}. {r['url']:<42} {r['naziv_entiteta'][:30]}")
