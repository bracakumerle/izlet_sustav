import json
import time
import requests
from difflib import SequenceMatcher

WORKS_FILE = "works_registry.json"

HEADERS = {
    "User-Agent": "izlet_sustav/1.0 (izletband@gmail.com)"
}

MB_URL = "https://musicbrainz.org/ws/2/recording/"


def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100


def query_musicbrainz(title, artist):
    params = {
        "query": f'recording:"{title}" AND artist:"{artist}"',
        "fmt": "json"
    }
    r = requests.get(MB_URL, params=params, headers=HEADERS)
    time.sleep(1)
    if r.status_code != 200:
        return None
    return r.json()


def extract_best_match(data, title):
    if not data or "recordings" not in data:
        return None

    best = None

    for rec in data["recordings"]:
        score = rec.get("score", 0)

        if score < 70:
            continue

        rec_title = rec.get("title", "")
        sim = similarity(rec_title, title)

        match_type = "fuzzy"
        if sim > 99:
            match_type = "exact"

        best = {
            "recording_id": rec.get("id"),
            "release_id": rec["releases"][0]["id"] if rec.get("releases") else None,
            "artist_id": rec["artist-credit"][0]["artist"]["id"]
                          if rec.get("artist-credit") else None,
            "confidence": round(score / 100, 2),
            "match_type": match_type
        }
        break

    return best


def main():
    with open(WORKS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    works = data["works"]

    results = []

    for key, work in works.items():
        rank = work.get("rank", 0)

        if rank < 33 or rank > 43:
            continue

        title = work["title_normalized"]

        # Primary artist
        mb_data = query_musicbrainz(title, "iZLET")
        match = extract_best_match(mb_data, title)

        # fallback
        if not match:
            mb_data = query_musicbrainz(title, "Braća Kumerle")
            match = extract_best_match(mb_data, title)

        if not match:
            match = {
                "recording_id": None,
                "release_id": None,
                "artist_id": None,
                "confidence": 0.0,
                "match_type": "manual_required"
            }

        works[key]["musicbrainz"] = match

        results.append({
            "title": title,
            **match
        })

    with open(WORKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n=== MUSICBRAINZ SYNC RESULTS ===\n")
    for r in results:
        print(
            r["title"],
            "| MBID:", r["recording_id"],
            "| confidence:", r["confidence"],
            "| match:", r["match_type"]
        )


if __name__ == "__main__":
    main()
