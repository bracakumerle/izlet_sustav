import sys
import io
import os
import csv
import math
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

INPUT_PATH  = os.path.join(os.path.dirname(__file__), '..', 'registries', 'youtube_corpus_raw.csv')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'registries', 'youtube_corpus_scored.csv')

NEW_FIELDS = [
    'upload_year', 'duration_seconds', 'authority_score', 'probable_tier',
    'era', 'type', 'primary_anchor', 'secondary_anchor',
    'canonical_status', 'notes',
]


def parse_duration(iso):
    if not iso or iso == 'P0D':
        return 0
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso)
    if not m:
        return 0
    h = int(m.group(1) or 0)
    mn = int(m.group(2) or 0)
    s = int(m.group(3) or 0)
    return h * 3600 + mn * 60 + s


def authority_score(row, duration_seconds):
    views    = int(row['view_count']    or 0)
    comments = int(row['comment_count'] or 0)
    likes    = int(row['like_count']    or 0)
    captions = row['has_captions'] == 'True'
    desc_len = int(row['description_length'] or 0)
    year     = int(row['upload_date'][:4]) if row['upload_date'] else 2020

    score = 0
    score += min(math.log10(views + 1) * 25, 25)
    score += min(math.log10(comments + 1) * 20, 20)
    score += min(math.log10(likes + 1) * 15, 15)
    if captions:
        score += 10
    if year < 2012:
        score += 15
    elif year <= 2018:
        score += 8
    if desc_len > 200:
        score += 5

    return round(score, 2)


def assign_tiers(rows):
    scored = sorted(rows, key=lambda r: r['authority_score'], reverse=True)
    for i, r in enumerate(scored):
        if i < 15:
            r['probable_tier'] = 'A'
        elif i < 65:
            r['probable_tier'] = 'B'
        else:
            r['probable_tier'] = 'C'
    return rows


def main():
    with open(INPUT_PATH, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        base_fields = reader.fieldnames

    print(f'Loaded {len(rows)} rows from {INPUT_PATH}')
    print()

    for row in rows:
        year = int(row['upload_date'][:4]) if row['upload_date'] else ''
        dur  = parse_duration(row['duration'])
        score = authority_score(row, dur)

        row['upload_year']       = year
        row['duration_seconds']  = dur
        row['authority_score']   = score
        row['probable_tier']     = ''
        row['era']               = ''
        row['type']              = ''
        row['primary_anchor']    = ''
        row['secondary_anchor']  = ''
        row['canonical_status']  = 'raw'
        row['notes']             = ''

    assign_tiers(rows)

    all_fields = list(base_fields) + NEW_FIELDS
    with open(OUTPUT_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f'Written {len(rows)} rows to {OUTPUT_PATH}')
    print()

    top20 = sorted(rows, key=lambda r: r['authority_score'], reverse=True)[:20]
    print(f'{"#":<3}  {"Tier":<5}  {"Score":>6}  {"Video ID":<13}  Title')
    print('-' * 90)
    for i, r in enumerate(top20, 1):
        title = r['title_current'][:55]
        print(f'{i:<3}  {r["probable_tier"]:<5}  {r["authority_score"]:>6}  {r["video_id"]:<13}  {title}')


if __name__ == '__main__':
    main()
