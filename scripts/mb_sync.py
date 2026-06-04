import json
import sys
import time
import requests
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

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
    time.sleep(1.1)   # MusicBrainz rate limit: 1 req/sec
    if r.status_code != 200:
        return None
    return r.json()


def extract_best_match(data, title):
    if not data or "recordings" not in data:
        return None

    for rec in data["recordings"]:
        score = rec.get("score", 0)
        if score < 70:
            continue

        rec_title = rec.get("title", "")
        sim = similarity(rec_title, title)
        match_type = "exact" if sim > 99 else "fuzzy"

        return {
            "recording_id": rec.get("id"),
            "work_id": None,   # populated separately if needed
            "release_id": rec["releases"][0]["id"] if rec.get("releases") else None,
            "artist_id": rec["artist-credit"][0]["artist"]["id"]
                         if rec.get("artist-credit") else None,
            "confidence": round(score / 100, 2),
            "match_type": match_type,
        }

    return None


def main():
    with open(WORKS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # canonical = all works where type != "cover" (defensive; registry contains no covers)
    works = data["works"]
    canonical = [(key, w) for key, w in works.items()
                 if w.get("type") != "cover"]

    skipped, matched, unmatched = [], [], []

    for key, work in canonical:
        title = work.get("title_normalized")
        if not title:
            print(f"  [SKIP] {key} — no title_normalized (type={work.get('type')})")
            continue

        # skip already synced
        existing_mb = work.get("musicbrainz", {})
        if existing_mb.get("recording_id"):
            skipped.append((work.get("rank"), title, existing_mb["recording_id"]))
            continue

        # query: iZLET first, Braća Kumerle fallback
        result = extract_best_match(query_musicbrainz(title, "iZLET"), title)
        if not result:
            result = extract_best_match(query_musicbrainz(title, "Braća Kumerle"), title)

        if result:
            work["musicbrainz"] = result
            work["musicbrainz_recording_id"] = result["recording_id"]
            matched.append((work.get("rank"), title, result))
        else:
            work["musicbrainz"] = {
                "recording_id": None,
                "work_id": None,
                "release_id": None,
                "artist_id": None,
                "confidence": 0.0,
                "match_type": "manual_required",
            }
            unmatched.append((work.get("rank"), title))

    with open(WORKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n=== MusicBrainz Sync — results ===\n")

    if skipped:
        print(f"Already synced ({len(skipped)}):")
        for rank, title, mbid in skipped:
            print(f"  [{rank:>2}] {title:<40} {mbid}")

    if matched:
        print(f"\nMatched ({len(matched)}):")
        for rank, title, m in matched:
            print(f"  [{rank:>2}] {title:<40} {m['recording_id']}"
                  f"  conf={m['confidence']}  ({m['match_type']})")

    if unmatched:
        print(f"\nNo match — manual required ({len(unmatched)}):")
        for rank, title in unmatched:
            print(f"  [{rank:>2}] {title}")

    total = len(canonical)
    print(f"\nTotal canonical: {total} | synced: {len(skipped)} | "
          f"new matches: {len(matched)} | unmatched: {len(unmatched)}")


if __name__ == "__main__":
    main()
