import sys
import io
import os
import csv
import time
import requests
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

API_KEY         = os.getenv('YOUTUBE_API_KEY')
CHANNEL_ID      = 'UC8jNEBUrOqCcXqVleV9ccKg'
UPLOADS_PLAYLIST = 'UU8jNEBUrOqCcXqVleV9ccKg'  # UC → UU

BASE_URL    = 'https://www.googleapis.com/youtube/v3'
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'registries', 'youtube_corpus_raw.csv')

FIELDNAMES = [
    'video_id', 'title_current', 'upload_date', 'duration',
    'view_count', 'like_count', 'comment_count',
    'has_captions', 'description_length', 'thumbnail_url',
]


def api_get(endpoint, params, retries=1):
    params['key'] = API_KEY
    for attempt in range(retries + 1):
        r = requests.get(f'{BASE_URL}/{endpoint}', params=params, timeout=20)
        if r.status_code == 429 and attempt < retries:
            print('  Quota hit — waiting 5s...')
            time.sleep(5)
            continue
        r.raise_for_status()
        return r.json()
    return {}


def get_all_video_ids():
    ids = []
    token = None
    while True:
        params = {
            'part':       'contentDetails',
            'playlistId': UPLOADS_PLAYLIST,
            'maxResults': 50,
        }
        if token:
            params['pageToken'] = token
        data = api_get('playlistItems', params)
        for item in data.get('items', []):
            ids.append(item['contentDetails']['videoId'])
        print(f'  Fetched {len(ids)} video IDs so far...')
        token = data.get('nextPageToken')
        if not token:
            break
    return ids


def best_thumbnail(thumbnails):
    for size in ('maxres', 'standard', 'high', 'medium', 'default'):
        if size in thumbnails:
            return thumbnails[size]['url']
    return ''


def get_video_details(video_ids):
    records = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        data = api_get('videos', {
            'part': 'snippet,contentDetails,statistics',
            'id':   ','.join(batch),
        })
        for item in data.get('items', []):
            vid        = item['id']
            snippet    = item.get('snippet', {})
            details    = item.get('contentDetails', {})
            stats      = item.get('statistics', {})
            desc       = snippet.get('description', '')
            published  = snippet.get('publishedAt', '')
            upload_date = published[:10] if published else ''
            records.append({
                'video_id':          vid,
                'title_current':     snippet.get('title', ''),
                'upload_date':       upload_date,
                'duration':          details.get('duration', ''),
                'view_count':        stats.get('viewCount', ''),
                'like_count':        stats.get('likeCount', ''),
                'comment_count':     stats.get('commentCount', ''),
                'has_captions':      str(details.get('caption', 'false') == 'true'),
                'description_length': len(desc),
                'thumbnail_url':     best_thumbnail(snippet.get('thumbnails', {})),
            })
        print(f'  Fetched details for {min(i + 50, len(video_ids))}/{len(video_ids)} videos...')
    return records


def main():
    if not API_KEY:
        raise ValueError('YOUTUBE_API_KEY missing in .env')

    print(f'Channel: {CHANNEL_ID}')
    print(f'Playlist: {UPLOADS_PLAYLIST}')
    print()

    print('Step 1 — collecting video IDs...')
    video_ids = get_all_video_ids()
    print(f'  Total video IDs: {len(video_ids)}')
    print()

    print('Step 2 — fetching video details...')
    records = get_video_details(video_ids)
    print()

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)

    print(f'Done. {len(records)} rows written to:')
    print(f'  {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
