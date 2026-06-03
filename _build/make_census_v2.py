import csv, sys
from collections import OrderedDict

# ── load v1 ──────────────────────────────────────────────────────────────────

v1 = OrderedDict()
with open(r'C:\Users\petar\OneDrive\Desktop\izlet_sustav\registries\works_census_v1.csv',
          encoding='utf-8') as f:
    for r in csv.DictReader(f):
        v1[r['slug']] = r

# ── load YT corpus for year lookup ──────────────────────────────────────────

yt_year = {}   # video_id → upload_year
with open(r'C:\Users\petar\OneDrive\Desktop\izlet_sustav\registries\youtube_corpus_scored.csv',
          encoding='utf-8') as f:
    for r in csv.DictReader(f):
        vid = r.get('video_id','').strip()
        yr  = r.get('upload_year','').strip()
        if vid and yr.isdigit():
            yt_year[vid] = int(yr)

def year_from_yt_ids(notes_str):
    """Extract first YT video ID from notes and return its upload year."""
    for part in notes_str.split('|'):
        part = part.strip()
        if part.startswith('yt='):
            ids = part[3:].split('|')
            for vid in ids[0].split('|'):
                vid = vid.strip()
                if vid in yt_year:
                    return yt_year[vid]
    return ''

# ── v2 schema ────────────────────────────────────────────────────────────────

FIELDS = ['title','slug','year','work_type','triage_class','confidence',
          'primary_source','notes']

v2 = OrderedDict()   # slug → dict

def add(title, slug, year, work_type, triage_class, confidence, primary_source, notes):
    year = str(year) if year else ''
    if slug in v2:
        e = v2[slug]
        # upgrade triage_class if needed
        rank = {'WORK':4,'PERFORMANCE':3,'COVER':3,'MEDIA':1}
        if rank.get(triage_class,0) > rank.get(e['triage_class'],0):
            e['triage_class'] = triage_class
        if confidence == 'confirmed' and e['confidence'] != 'confirmed':
            e['confidence'] = confidence
        # merge notes
        for part in notes.split('|'):
            part = part.strip()
            if part and part not in e['notes']:
                e['notes'] = (e['notes'] + ' | ' + part).strip(' |')
        # keep earlier year if both non-empty
        if year and e['year'] and e['year'].isdigit() and year.isdigit():
            e['year'] = str(min(int(e['year']), int(year)))
        elif year and not e['year']:
            e['year'] = year
    else:
        v2[slug] = dict(title=title, slug=slug, year=year, work_type=work_type,
                        triage_class=triage_class, confidence=confidence,
                        primary_source=primary_source, notes=notes)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Migrate v1
# ─────────────────────────────────────────────────────────────────────────────

# Explicit reclassifications from candidate
COVERS       = {'moj-kupresu-legendo-hrvata', 'zemlja-dide-mog'}
PERFORMANCES = {'rajska-djevo-kraljice-hrvata', 'vracam-se-zagrebe'}
PERF_NOTES   = {
    'rajska-djevo-kraljice-hrvata': 'izvedba narodne vjerske pjesme',
    'vracam-se-zagrebe':           'izvedba Robiceva slagera',
}
WORK_PROBABLE = {'strice-ivane'}

# Step 2 slugs that will be added as WORK — mark them so they don't become MEDIA
STEP2_WORK_SLUGS = {
    'spasi-me','ljeto-u-maximiru','sadanji-trenutak','tuzni-odlazak',
    'oo-da-sa-krilima','samo-tamo','igraj-donna','tvoja-njedra',
    'pod-ovim-nebom','dzomba','ljeto-ide-majko','nezavisna-drzava-hrvatska',
    'zetovac','roadrunner','cast-postenje-i-cisti-obraz',
    'mozda-su-u-sumi','ludi-gadovi','nemam-ni-jednog-prijatelja-policajca',
    'celavi-skembici','susjedova-vila','i-migranti',
    'himna-veslackog-kluba-zagreb','obale-se-tope','gori-oluja',
    'koza-u-velegradu','oltar-spasa','postoji-samo-jedan-bog',
    'autori-nalaze-smisao','konji-od-zada','neka-slatko-boli',
    'hrvatski-trolist','dotepenci','hrabrost','dozivljaj',
    'tvoje-je-pitanje-totalno-suvisno','vlak','mon-ami','soram-snjevovica',
}

for slug, r in v1.items():
    ds = r['discovery_status']
    notes = r['notes']

    if ds == 'confirmed':
        # All confirmed → WORK
        tc = 'WORK'
        conf = 'confirmed'

        # Specific note additions
        if slug == 'cast':
            extra = 'alternate_title=Honour | yt=1gPfgO3daPk|K90ntS9oIEM'
            notes = (notes + ' | ' + extra).strip(' |')
        if slug == 'krijesovi-lazi':
            extra = 'alternate_title=Bonfires of Lies | yt=gk5AHkbyLVU'
            notes = (notes + ' | ' + extra).strip(' |')

        add(r['title'], slug, r['year'], r['work_type'],
            tc, conf, r['primary_source'], notes)

    else:
        # candidate
        if slug in COVERS:
            add(r['title'], slug, r['year'], r['work_type'],
                'COVER', 'confirmed', r['primary_source'], notes)
        elif slug in PERFORMANCES:
            pnotes = (notes + ' | ' + PERF_NOTES[slug]).strip(' |') if PERF_NOTES.get(slug) else notes
            add(r['title'], slug, r['year'], r['work_type'],
                'PERFORMANCE', 'confirmed', r['primary_source'], pnotes)
        elif slug in WORK_PROBABLE:
            add(r['title'], slug, r['year'], r['work_type'],
                'WORK', 'probable', r['primary_source'], notes)
        elif slug in STEP2_WORK_SLUGS:
            # will be handled by step 2 with upgrade — temporarily add as MEDIA
            # step 2 will upgrade triage_class to WORK
            add(r['title'], slug, r['year'], r['work_type'],
                'MEDIA', 'probable', r['primary_source'], notes)
        else:
            add(r['title'], slug, r['year'], r['work_type'],
                'MEDIA', 'probable', r['primary_source'], notes)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Add / upgrade new confirmed WORKs
# ─────────────────────────────────────────────────────────────────────────────

new_works = [
    # (title, slug, year_override, primary_source, notes_extra)
    # year_override=None → infer from YT ID in notes
    ('Spasi me',            'spasi-me',             None, 'youtube_corpus',
     'yt=hhLKTaqshvE | Spot/Official Video'),
    ('Ljeto u Maximiru',    'ljeto-u-maximiru',      None, 'youtube_corpus',
     'yt=Ri0cJPe72uc | Spot/Official Video'),
    ('Sadašnji Trenutak',   'sadanji-trenutak',       None, 'youtube_corpus',
     'yt=570Z7nd9DnM | Spot/Official Video'),
    ('Tužni odlazak',       'tuzni-odlazak',          None, 'youtube_corpus',
     'yt=AzIAgVPLglo | Spot/Official Video'),
    ('Oo da sa krilima',    'oo-da-sa-krilima',       None, 'youtube_corpus',
     'yt=cX1TgmIcM1M | Spot/Official Video'),
    ('Samo tamo',           'samo-tamo',              None, 'youtube_corpus',
     'yt=-yytBsUO7vg | Spot/Official Video'),
    ('Igraj Donna',         'igraj-donna',            None, 'youtube_corpus',
     'yt=IwSwfLdVwEM | Spot/Official Video'),
    ('Tvoja njedra',        'tvoja-njedra',           None, 'youtube_corpus',
     'yt=mnm1PQdDBCA | Spot/Official Video'),
    ('Pod ovim nebom',      'pod-ovim-nebom',         None, 'youtube_corpus',
     'yt=c50YNCfEveM | Spot/Official Video'),
    ('Džomba',              'dzomba',                 None, 'youtube_corpus',
     'yt=CScTvW2KtMI | Spot/Official Video'),
    ('Ljeto ide majko',     'ljeto-ide-majko',        None, 'youtube_corpus',
     'yt=YRZ9NpV6LMs | feat. Damir Dinjar'),
    ('Nezavisna Država Hrvatska', 'nezavisna-drzava-hrvatska', None, 'youtube_corpus',
     'yt=GCW4uYcJTbs | ft. Tomislav Lucic'),
    ('Zetovac',             'zetovac',                None, 'youtube_corpus',
     'yt=WryChY9304U | ft. 3 Gosta | Satiricna oda ZET radniku'),
    ('Roadrunner',          'roadrunner',             None, 'youtube_corpus',
     'yt=1NBy512CpaM | ft. Grgo Savic'),
    ('Čast poštenje i čisti obraz', 'cast-postenje-i-cisti-obraz', None, 'youtube_corpus',
     'yt=V8Jw0Letyyo | Autorska pjesma / Live'),
    ('Možda su u šumi',     'mozda-su-u-sumi',        None, 'youtube_corpus',
     'yt=j_oPnn2_iUI | feat. Grgo Savic'),
    ('Ludi gadovi',         'ludi-gadovi',            None, 'youtube_corpus',
     'yt=LPsDeZYTXxs | feat. Grgo Savic & Niksa Ersek'),
    ('Nemam ni jednog prijatelja policajca', 'nemam-ni-jednog-prijatelja-policajca',
     None, 'youtube_corpus', 'yt=FYYSZX601uw | feat. Ante Cash'),
    ('Ćelavi škembići',     'celavi-skembici',        None, 'youtube_corpus',
     'yt=OXbbZ3siV2o'),
    ('Susjedova vila',      'susjedova-vila',         None, 'youtube_corpus',
     'yt=vXlovhrX1lI'),
    ('i Migranti',          'i-migranti',             None, 'youtube_corpus',
     'yt=saci9JTd0Kk | Zavrsni dio Marjanske trilogije'),
    ('Himna Veslačkog kluba Zagreb', 'himna-veslackog-kluba-zagreb', None, 'youtube_corpus',
     'yt=4VEgzZOOz0I | narudzba/commission'),
    ('Obale se tope',       'obale-se-tope',          None, 'youtube_corpus',
     'yt=NOd5DcwBB-w'),
    ('Gori Oluja',          'gori-oluja',             None, 'youtube_corpus',
     'yt=QeNd7IbWGRY | feat. Marko Juric'),
    ('Koza u velegradu',    'koza-u-velegradu',       None, 'youtube_corpus',
     'yt=WzluO7jci3k'),
    ('Altar of salvation',  'altar-of-salvation',     None, 'youtube_corpus',
     'yt=3gkz1TgqFpU | hr: Oltar spasa'),
    ('There is only one God','there-is-only-one-god', None, 'youtube_corpus',
     'yt=l811vDOLeIw | hr: Postoji samo jedan Bog'),
    ('Autori nalaze smisao','autori-nalaze-smisao',   None, 'youtube_corpus',
     'yt=z8WtJjLURDc'),
    ('Konji od žada',       'konji-od-zada',          None, 'youtube_corpus',
     'yt=RIMjp8vhOcE'),
    ('Neka slatko boli',    'neka-slatko-boli',       None, 'youtube_corpus',
     'yt=hx0FveDZWXw | puni naslov: Neka slatko boli (Ljubav lijeci sve)'),
    ('Hrvatski Trolist',    'hrvatski-trolist',       None, 'youtube_corpus',
     'yt=ggKfXgO-tqI'),
    ('Dotepenci',           'dotepenci',              None, 'youtube_corpus',
     'yt=6btrsbTtJeM'),
    ('Hrabrost',            'hrabrost',               None, 'youtube_corpus',
     'yt=ARk01HV2ic8'),
    ('Doživljaj',           'dozivljaj',              None, 'youtube_corpus',
     'yt=0VvUpR_IMIY'),
    ('Tvoje je pitanje totalno suvišno', 'tvoje-je-pitanje-totalno-suvisno', None,
     'youtube_corpus', 'yt=TdmNgEb4Dy8'),
    ('Vlak',                'vlak',                   2012, 'youtube_corpus',
     'yt=RKxeAaIqHMI | album Leteci majmuni 2012 | yt=tlXIQyi9tPk'),
    ('Mon Ami',             'mon-ami',                None, 'youtube_corpus',
     'yt=i3kU-6rPVFU | live @ Route 66 Zagreb'),
    ('Šoram snjegovića',    'soram-snjevovica',       None, 'youtube_corpus',
     'yt=LW0Om2bBluc | live @ Aquarius Zagreb'),
]

# Entries not in v1 that need explicit add with non-WORK triage
explicit_non_work = [
    ('Zemlja dide mog', 'zemlja-dide-mog', 2024, 'song', 'COVER', 'confirmed',
     'youtube_corpus', 'yt=XjxpRZaWCgQ'),
    ('Rajska Djevo, Kraljice Hrvata', 'rajska-djevo-kraljice-hrvata', 2024, 'song',
     'PERFORMANCE', 'confirmed', 'youtube_corpus',
     'yt=EWziHN3oFk0 | izvedba narodne vjerske pjesme'),
    ('Vraćam se Zagrebe', 'vracam-se-zagrebe', 2024, 'song',
     'PERFORMANCE', 'confirmed', 'youtube_corpus',
     'yt=mgXu_i6Aemo | izvedba Robiceva slagera'),
]
for title, slug, year, wt, tc, conf, src, notes in explicit_non_work:
    add(title, slug, year, wt, tc, conf, src, notes)

for title, slug, yr_override, src, notes_extra in new_works:
    # infer year from YT if not overridden
    if yr_override is not None:
        year = yr_override
    else:
        year = year_from_yt_ids(notes_extra)

    add(title, slug, year, 'song', 'WORK', 'confirmed', src, notes_extra)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — Write v2 CSV
# ─────────────────────────────────────────────────────────────────────────────

out = r'C:\Users\petar\OneDrive\Desktop\izlet_sustav\registries\works_census_v2.csv'
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    for r in v2.values():
        w.writerow(r)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — Summary to stdout (ASCII-safe for redirect)
# ─────────────────────────────────────────────────────────────────────────────

rows = list(v2.values())
total = len(rows)

by_tc   = {}
by_conf = {}
for r in rows:
    tc = r['triage_class']
    by_tc[tc] = by_tc.get(tc, 0) + 1
    c = r['confidence']
    by_conf[c] = by_conf.get(c, 0) + 1

work_conf    = len([r for r in rows if r['triage_class']=='WORK' and r['confidence']=='confirmed'])
work_prob    = len([r for r in rows if r['triage_class']=='WORK' and r['confidence']=='probable'])
perf_count   = by_tc.get('PERFORMANCE', 0)
cover_count  = by_tc.get('COVER', 0)
media_count  = by_tc.get('MEDIA', 0)
coverage_pct = work_conf / 90 * 100

# Year breakdown for WORK confirmed
work_years = {}
for r in rows:
    if r['triage_class'] == 'WORK' and r['confidence'] == 'confirmed' and r['year']:
        try:
            y = int(r['year'])
            work_years[y] = work_years.get(y, 0) + 1
        except:
            pass

conf_works = [r for r in rows if r['triage_class']=='WORK' and r['confidence']=='confirmed' and r['year']]
earliest = min(conf_works, key=lambda x: int(x['year'])) if conf_works else None
latest   = max(conf_works, key=lambda x: int(x['year'])) if conf_works else None

out_txt = r'C:\Users\petar\OneDrive\Desktop\izlet_sustav\reports\census_v2_summary.txt'
import io
buf = io.StringIO()

buf.write("works_census_v2.csv — Summary\n")
buf.write("=" * 40 + "\n\n")
buf.write(f"Total rows:             {total}\n\n")
buf.write("By triage_class:\n")
for tc in ['WORK','COVER','PERFORMANCE','MEDIA']:
    buf.write(f"  {tc:<14} {by_tc.get(tc,0)}\n")
buf.write("\nBy confidence:\n")
for c in ['confirmed','probable','possible']:
    buf.write(f"  {c:<12} {by_conf.get(c,0)}\n")
buf.write("\nWORK detail:\n")
buf.write(f"  confirmed:  {work_conf}\n")
buf.write(f"  probable:   {work_prob}\n")
buf.write(f"\nCoverage (WORK confirmed / 90): {work_conf} / 90 = {coverage_pct:.0f}%\n")
buf.write("\nBy year (WORK confirmed):\n")
for y in sorted(work_years):
    buf.write(f"  {y}: {work_years[y]}\n")
if earliest:
    buf.write(f"\nEarliest WORK confirmed: {earliest['title'].encode('ascii','replace').decode()} ({earliest['year']})\n")
if latest:
    buf.write(f"Latest WORK confirmed:   {latest['title'].encode('ascii','replace').decode()} ({latest['year']})\n")

summary = buf.getvalue()
with open(out_txt, 'w', encoding='utf-8') as f:
    f.write(summary)
print(summary)
print(f"Written: {out}")
print(f"Written: {out_txt}")
