import csv, re, unicodedata, sys
from collections import OrderedDict

# ── helpers ──────────────────────────────────────────────────────────────────

def nfd(s):
    s = unicodedata.normalize('NFD', s)
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()

def slugify(s):
    s = nfd(s)
    s = re.sub(r'[^a-z0-9\s]', '', s)
    s = re.sub(r'\s+', '-', s.strip())
    return re.sub(r'-+', '-', s)

CONF = {'confirmed': 3, 'probable': 2, 'possible': 1}

census = OrderedDict()   # slug → row dict

def put(title, slug, year, work_type, confidence, primary_source, notes, discovery_status):
    if not slug:
        return
    if slug in census:
        ex = census[slug]
        new_rank = CONF.get(confidence, 0)
        old_rank = CONF.get(ex['confidence'], 0)
        if new_rank > old_rank:
            ex['confidence']      = confidence
            ex['primary_source']  = primary_source
            ex['discovery_status']= discovery_status
        if new_rank == old_rank == 3 and isinstance(year, int) and isinstance(ex['year'], int):
            if year < ex['year'] and year > 0:
                ex['year'] = year           # prefer earlier confirmed year
        if notes and notes not in ex['notes']:
            ex['notes'] = (ex['notes'] + ' | ' + notes).strip(' |') if ex['notes'] else notes
    else:
        census[slug] = dict(title=title, slug=slug, year=year, work_type=work_type,
                            confidence=confidence, primary_source=primary_source,
                            notes=notes, discovery_status=discovery_status)

# ── step 1: Discogs confirmed ────────────────────────────────────────────────

# Nikad ne znas album (Discogs 12898284, 2016)
album_nn = 'Nikad Ne Znas To Je Ono | Discogs 12898284'
for t in ['Pernastica','Dva Gemišta','Oni Spavaju','Svemir','Imam','Ne Žurim',
          'Noćima (Here I Am)','Kako Da Se Smijem','Maša','Topim Se I Gubim Se',
          'Ti Si Čudesna','Majčin Skut','Žalo']:
    put(t, slugify(t), 2016, 'song', 'confirmed', 'discogs', album_nn, 'confirmed')

# Ti si cudesna: first confirmed appearance 2009 CMC Demo (TrackAppearance)
census['ti-si-cudesna']['year'] = 2009
census['ti-si-cudesna']['notes'] += ' | orig.2009 CMC Demo Discogs 12309194'
# Zalo: Dallas Promo Sampler 2013 (TrackAppearance) — earlier than album
census['zalo']['year'] = 2013
census['zalo']['notes'] += ' | first confirmed 2013 Dallas Promo Sampler Discogs 25236337'

# Katarza album (Discogs 35923165, 2019)
album_k = 'Katarza | Discogs 35923165'
for t in ['Čast','U svijetu bajki','Uredi se','Tko si ti','Urota duhova','Oceana',
          'Siluete','Zaklopi moje oči','Zašto šutim','Čaroban otok','Poslije svega',
          'Princeza Tea','Ponekad','Kokosovo mlijeko','Osmijeh je bitan']:
    put(t, slugify(t), 2019, 'song', 'confirmed', 'discogs', album_k, 'confirmed')

# Nema Mjesta single (Hitchtone, 2018)
put('Nema Mjesta','nema-mjesta',2018,'song','confirmed','discogs',
    'Hitchtone Music | Discogs 35924701','confirmed')

# BKM singles — using original year from YouTube corpus evidence, not Discogs re-reg year (2025)
bkm = [
    ('Sjever uz odsutne','sjever-uz-odsutne',2023,'Braća Kumerle Music | Discogs 35920849'),
    ('Moj Dinamo','moj-dinamo',2024,'Braća Kumerle Music | Discogs 35923336'),
    ('Vitez Jure','vitez-jure',2021,'Braća Kumerle Music | Discogs 35923378'),
    ('Frane Tente','frane-tente',2020,'Braća Kumerle Music | Discogs 35923390'),
    ('Krijesovi Laži','krijesovi-lazi',2025,'Braća Kumerle Music | Discogs 35923438'),
    ('Znakovlje Hrvata','znakovlje-hrvata',2021,'Braća Kumerle Music | Discogs 35923459'),
    ('Bogdanovačka Kalvarija','bogdanovacka-kalvarija',2020,'Braća Kumerle Music | Discogs 35923474'),
    ('124. Vukovarska Brigada Himna','124-vukovarska-brigada-himna',2021,'Braća Kumerle Music | Discogs 35923504'),
    ('Božićna Idila','bozicna-idila',2023,'Braća Kumerle Music | Discogs 37224165'),
    ('Čovjek moli Boga','covjek-moli-boga',2022,'Braća Kumerle Music | Discogs 37223433'),
    ('Isuse moj','isuse-moj',2020,'Braća Kumerle Music | Discogs 37224108'),
]
for title,slug,year,notes in bkm:
    put(title,slug,year,'song','confirmed','discogs',notes,'confirmed')

# ── step 2: lyrics_corpus_registry.csv ───────────────────────────────────────

with open(r'C:\Users\petar\OneDrive\Desktop\izlet_sustav\registries\lyrics_corpus_registry.csv',
          encoding='utf-8') as f:
    for row in csv.DictReader(f):
        slug = (row.get('slug') or '').strip()
        if not slug:
            continue
        title = (row.get('title') or '').strip()
        yr_raw = (row.get('first_release_year') or '').strip()
        year = int(yr_raw) if yr_raw.isdigit() else 0
        notes = 'lyrics_registry'
        isrc = (row.get('isrc') or '').strip()
        if isrc:
            notes += f' | ISRC {isrc}'
        put(title, slug, year, 'song', 'confirmed',
            'discogs+lyrics' if slug in census else 'lyrics_registry',
            notes, 'confirmed')

# ── step 3: DistroKid manual seeds ───────────────────────────────────────────

dk_seeds = [
    ('Krijesovi laži','krijesovi-lazi',2025,
     'ISRC QT6F32539173, UPC 199951813477, rel.2025-11-22'),
    ('Sjever uz odsutne','sjever-uz-odsutne',2023,
     'ISRC QT6EX2529331, UPC 199953974831, orig.2023, rel.2025-11-15'),
    ('Frane Tente','frane-tente',2020,
     'ISRC QT6F32536381, UPC 199951817604, orig.2020, rel.2025-11-22'),
    ('Znakovlje Hrvata','znakovlje-hrvata',2021,
     'ISRC QZ6PP2514425, UPC 199943222911, orig.2021, rel.2025-12-14'),
]
for title,slug,year,notes in dk_seeds:
    put(title,slug,year,'song','confirmed','DistroKid',notes,'confirmed')

# ── step 4: YouTube corpus discovery ─────────────────────────────────────────

BAND_PREFIX = re.compile(
    r'^(iZLET|Braća\s+Kumerle|Braca\s+Kumerle|IZLET|Kumerle\s+Brothers?)'
    r'(\s+[&i]\s+\w+)?\s*[-–]\s*', re.IGNORECASE)

LIVE_KW = re.compile(
    r'\b(live|uživo|uzivo|akustičn|akusticn|acoustic|nastup|intervju|'
    r'interview|trailer|najava|božić|bozic|fešta|festa|vlog|hrt|'
    r'podcast\s+velebit|svjetski\s+dan\s+glazbe)\b', re.IGNORECASE)
COVER_KW = re.compile(r'\bcover\b', re.IGNORECASE)

def extract_core(raw):
    t = raw
    # strip emoji / flags
    t = re.sub(r'[\U0001F300-\U0001FFFF]', '', t).strip()
    # remove band prefix
    t = BAND_PREFIX.sub('', t)
    # cut at | or # or ( or [
    t = re.split(r'\s*[\|#\(\[]', t)[0]
    # remove trailing live/official suffixes
    t = re.sub(r'\s*(OFFICIAL\s+VIDEO|Official\s+Video|LIVE\s*@.*|Uživo\s*@.*)', '',
               t, flags=re.IGNORECASE)
    t = t.strip(' -–.,!?')
    return t

def slug_in_title(norm_title, slugs):
    for s in sorted(slugs, key=len, reverse=True):
        if s.replace('-', ' ') in norm_title:
            return s
    return None

SKIP_PATTERNS = re.compile(
    r'\b(hodocasn|hocosasn|pilgrimage|arena\s+zagreb|hipodrom|thompson\s+x|'
    r'hvo\s+nas\s+vodi|bog\s+i\s+hrvati|na\s+na\s+na|ko\s+sam|'
    r'zasto\s+su\s+svi|sto\s+te\s+skola|grobnica\s+od\s+zlata|'
    r'pravi\s+zagreb|dragi\s+hrvati|deseti\s+travanj|'
    r'bogdanovci\s+moji|bijeli\s+kriz|bile\s+hercegovina|nece\s+pasti|'
    r'nova\s+zora\s+nama|svaku\s+stopu|ivo\s+fabijan|toni\s+cavar|'
    r'oliver\s+dragoj|mate\s+bulic|jura\s+stublic|eric\s+clapton|'
    r'iron\s+maiden|avicii|pink\s+floyd|film\s+-\s+idemo|dubo\s+remix|'
    r'la\s+amour\s+toujours|harambas|vilo\s+velebita\s+cover|'
    r'gdje\s+sam\s+bio\s+ne\s+pitaj|hvalospjev\s+ljubavi|'
    r'sam\s+reci\s+rijec|frane\s+sisko|djani\s+marsan|'
    r'drazen\s+zanko|toni\s+cavar)\b', re.IGNORECASE)

with open(r'C:\Users\petar\OneDrive\Desktop\izlet_sustav\registries\youtube_corpus_scored.csv',
          encoding='utf-8') as f:
    for row in csv.DictReader(f):
        raw = (row.get('title_current') or '').strip()
        vid  = (row.get('video_id') or '').strip()
        yr_raw = (row.get('upload_year') or '').strip()
        try:
            yt_year = int(yr_raw)
        except:
            yt_year = 0

        core = extract_core(raw)
        if not core or len(core) < 4:
            continue

        core_norm = nfd(core)
        matched = slug_in_title(core_norm, list(census.keys()))

        if matched:
            vid_note = f'YT:{vid}'
            ex = census[matched]
            if vid_note not in ex['notes']:
                ex['notes'] = (ex['notes'] + ' | ' + vid_note).strip(' |') if ex['notes'] else vid_note
            continue

        # New candidate
        slug = slugify(core)
        if not slug or len(slug) < 3 or slug in census:
            # If slug exists, still add video id
            if slug in census:
                vid_note = f'YT:{vid}'
                ex = census[slug]
                if vid_note not in ex['notes']:
                    ex['notes'] = (ex['notes'] + ' | ' + vid_note).strip(' |') if ex['notes'] else vid_note
            continue

        # Skip obvious non-works (specific known non-original content)
        if SKIP_PATTERNS.search(core_norm):
            # Still add but mark clearly
            pass

        extra = ''
        if COVER_KW.search(raw):
            extra = 'cover performance'
        elif LIVE_KW.search(raw):
            extra = 'live/performance context'

        notes_parts = [f'YT:{vid}']
        if extra:
            notes_parts.append(extra)
        notes = ' | '.join(notes_parts)

        put(core, slug, yt_year, 'song', 'probable', 'youtube_corpus', notes, 'candidate')

# ── step 6: write CSV ─────────────────────────────────────────────────────────

import os
out_path = r'C:\Users\petar\OneDrive\Desktop\izlet_sustav\registries\works_census_v1.csv'
fields = ['title','slug','year','work_type','confidence','primary_source','notes','discovery_status']

with open(out_path, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in census.values():
        w.writerow(r)

# ── step 7: summary ───────────────────────────────────────────────────────────

total = len(census)
by_status = {}
by_year_conf = {}
for r in census.values():
    s = r['discovery_status']
    by_status[s] = by_status.get(s,0) + 1
    if s == 'confirmed' and r['year']:
        by_year_conf.setdefault(r['year'], []).append(r['title'])

conf_rows = [r for r in census.values() if r['discovery_status']=='confirmed' and r['year']]
earliest = min(conf_rows, key=lambda x: x['year']) if conf_rows else None
latest   = max(conf_rows, key=lambda x: x['year']) if conf_rows else None
n_conf   = by_status.get('confirmed', 0)

print(f"\nTotal rows: {total}")
print("By discovery_status:")
for k in ('confirmed','candidate','rejected'):
    print(f"  {k}: {by_status.get(k,0)}")
print("By year (confirmed only):")
for y in sorted(by_year_conf):
    print(f"  {y}: {len(by_year_conf[y])}  ({', '.join(by_year_conf[y])})")
if earliest:
    print(f"Earliest confirmed work: {earliest['title']}, {earliest['year']}")
if latest:
    print(f"Latest confirmed work: {latest['title']}, {latest['year']}")
print(f"Confirmed Work Coverage estimate: {n_conf} / ~80-100 = {n_conf/90*100:.0f}%")
print(f"\nWritten to: {out_path}")
