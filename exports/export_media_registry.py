import sys
import io
import os
import json
import csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE   = os.path.join(os.path.dirname(__file__), '..')
INPUT  = os.path.join(BASE, 'registry', 'media_registry.json')
PUBLIC = os.path.join(BASE, 'exports', 'media_registry_public.csv')
GEMINI = os.path.join(BASE, 'exports', 'media_registry_gemini.csv')

FIELDS = ['media_id', 'media_name', 'title', 'published_date', 'url', 'category', 'author']

# Authority ranking — higher = stronger
MEDIA_AUTHORITY = {
    'Večernji list':          10,
    'Jutarnji list':          10,
    '24sata.hr':              9,
    'Net.hr':                 9,
    'Novi list':              9,
    'Direktno.hr':            8,
    'Barikada.com':           8,
    'Ziher.hr':               8,
    'Wikipedia HR':           7,
    'Fenix Magazin':          6,
    'Mixeta.net':             6,
    'Zagreb.info':            6,
    'HOP.com.hr':             5,
    'Maxportal.hr':           5,
    'Dalmatinskiportal.hr':   5,
    'Narod.hr':               4,
    'Likaclub.net.hr':        4,
    'Portal Braniteljski forum': 3,
}

def load_articles(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    rows = []
    for art in data['articles']:
        rows.append({
            'media_id':      art.get('id', ''),
            'media_name':    art.get('source', ''),
            'title':         art.get('title', ''),
            'published_date': art.get('date', ''),
            'url':           art.get('url', ''),
            'category':      art.get('category', ''),
            'author':        art.get('author', ''),
            # internal — for sorting only
            '_status':       art.get('status', ''),
            '_gng':          art.get('gng_eligible', False),
        })
    return rows


def authority_score(row):
    media_score  = MEDIA_AUTHORITY.get(row['media_name'], 3)
    author_score = 2 if row['author'] else 0
    live_score   = 2 if row['_status'] == 'live' else 0
    gng_score    = 3 if row['_gng'] else 0
    return media_score + author_score + live_score + gng_score


def write_csv(path, rows):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows = load_articles(INPUT)
    print(f'Loaded {len(rows)} articles from media_registry.json')
    print()

    # --- public CSV (original order) ---
    write_csv(PUBLIC, rows)
    print(f'Public CSV: {PUBLIC}')

    # --- category counts ---
    cats = {}
    for r in rows:
        cats[r['category']] = cats.get(r['category'], 0) + 1
    print()
    print('Articles by category:')
    for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f'  {n:>3}  {cat}')

    # --- authority scores ---
    for r in rows:
        r['_authority'] = authority_score(r)

    sorted_rows = sorted(rows, key=lambda r: r['_authority'], reverse=True)

    # --- top 10 reverse citation candidates ---
    print()
    print('Top 10 — Reverse Citation Engine candidates:')
    print(f'  {"#":<3}  {"Score":>5}  {"ID":<7}  {"Source":<22}  Title')
    print('  ' + '-' * 80)
    for i, r in enumerate(sorted_rows[:10], 1):
        print(f'  {i:<3}  {r["_authority"]:>5}  {r["media_id"]:<7}  {r["media_name"]:<22}  {r["title"][:45]}')

    # --- gemini CSV (sorted by authority) ---
    write_csv(GEMINI, sorted_rows)
    print()
    print(f'Gemini CSV: {GEMINI}')
    print()
    print('Done.')


if __name__ == '__main__':
    main()
