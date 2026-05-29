import sys
import io
import os
import csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

INPUT_PATH   = os.path.join(os.path.dirname(__file__), '..', 'registries', 'youtube_corpus_scored.csv')
TOP40_PATH   = os.path.join(os.path.dirname(__file__), '..', 'registries', 'youtube_review_top40.csv')
COVERS_PATH  = os.path.join(os.path.dirname(__file__), '..', 'registries', 'youtube_covers.csv')

REVIEW_FIELDS = [
    'video_id', 'title_current', 'upload_date', 'upload_year',
    'duration_seconds', 'view_count', 'like_count', 'comment_count',
    'authority_score', 'probable_tier',
    'era', 'type', 'primary_anchor', 'secondary_anchor',
    'canonical_status', 'notes',
]


def main():
    with open(INPUT_PATH, encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))

    print(f'Loaded {len(rows)} rows.')

    sorted_rows = sorted(rows, key=lambda r: float(r['authority_score']), reverse=True)

    top40 = sorted_rows[:40]
    with open(TOP40_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=REVIEW_FIELDS, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(top40)
    print(f'Top 40 written to: {TOP40_PATH}')

    covers = [r for r in rows if 'cover' in r['title_current'].lower()]
    with open(COVERS_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=REVIEW_FIELDS, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(covers)
    print(f'Covers found: {len(covers)}')
    print(f'Covers written to: {COVERS_PATH}')
    print()

    print(f'{"#":<3}  {"Score":>6}  {"Tier":<5}  {"Year":<5}  Title')
    print('-' * 85)
    for i, r in enumerate(top40, 1):
        print(f'{i:<3}  {float(r["authority_score"]):>6.1f}  {r["probable_tier"]:<5}  {r["upload_year"]:<5}  {r["title_current"][:55]}')

    print()
    print('Cover titles:')
    for r in sorted(covers, key=lambda r: float(r['authority_score']), reverse=True):
        print(f'  [{r["upload_year"]}]  {r["title_current"][:70]}  (score: {r["authority_score"]})')


if __name__ == '__main__':
    main()
