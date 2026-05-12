import json
import time
import requests
import sys
import io
import os
from datetime import datetime

sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKS_FILE = "works_registry.json"
EVENTS_FILE = "registry/enrichment_events.json"

CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


def get_token():
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    return r.json()["access_token"]


def safe_request(fn, retries=3):
    for i in range(retries):
        try:
            return fn()
        except Exception as e:
            print(f"  retry {i+1}: {e}")
            time.sleep(2 ** i)
    return None


def _search(isrc, token):
    r = requests.get(
        "https://api.spotify.com/v1/search",
        params={"q": f"isrc:{isrc}", "type": "track", "limit": 1},
        headers={"Authorization": f"Bearer {token}"}
    )
    time.sleep(0.6)
    if r.status_code != 200:
        return None
    items = r.json().get("tracks", {}).get("items", [])
    if not items:
        return None
    t = items[0]
    return {
        "track_id":    t["id"],
        "album_id":    t["album"]["id"],
        "popularity":  t["popularity"],
        "duration_ms": t["duration_ms"],
        "explicit":    t["explicit"],
        "confidence":  1.0,
        "match_type":  "exact"
    }


def search_by_isrc(isrc, token):
    return safe_request(lambda: _search(isrc, token))


def main():
    data = json.load(open(WORKS_FILE, encoding="utf-8"))
    token = get_token()
    results = []
    events = []

    for key, work in data["works"].items():
        mb = work.get("musicbrainz", {})
        isrc = work.get("isrc") or mb.get("isrc")
        mbid = mb.get("recording_id")

        if not isrc:
            continue

        # IDEMPOTENCY GUARD
        if work.get("spotify", {}).get("track_id"):
            print(f"  SKIP (already enriched): {work['title_normalized']}")
            continue

        sp = search_by_isrc(isrc, token)

        if sp:
            work["spotify"] = sp
            if "reconciliation" not in work:
                work["reconciliation"] = {}
            work["reconciliation"]["spotify_confidence"] = 1.0
            work["reconciliation"]["status"] = "partial"
            work["reconciliation"]["entity_state"] = {
                "musicbrainz": "confirmed",
                "spotify":     "confirmed",
                "discogs":     "pending",
                "youtube":     "pending"
            }
            events.append({
                "event_type":       "entity_enrichment",
                "source":           "spotify",
                "entity_mbid":      mbid,
                "isrc":             isrc,
                "spotify_track_id": sp["track_id"],
                "confidence":       1.0,
                "timestamp":        datetime.utcnow().isoformat() + "Z"
            })
        else:
            work["spotify"] = {
                "track_id":    None,
                "album_id":    None,
                "popularity":  None,
                "duration_ms": None,
                "explicit":    None,
                "confidence":  0.0,
                "match_type":  "manual_required"
            }
            if "reconciliation" not in work:
                work["reconciliation"] = {}
            work["reconciliation"]["spotify_confidence"] = 0.0
            work["reconciliation"]["status"] = "partial"
            work["reconciliation"]["entity_state"] = {
                "musicbrainz": "confirmed",
                "spotify":     "pending",
                "discogs":     "pending",
                "youtube":     "pending"
            }

        results.append({
            "title":      work["title_normalized"],
            "mbid":       mbid,
            "isrc":       isrc,
            "track_id":   work["spotify"]["track_id"],
            "popularity": work["spotify"]["popularity"]
        })

    json.dump(data, open(WORKS_FILE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    if events:
        json.dump(events,
                  open(EVENTS_FILE, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print(f"\nLogged {len(events)} enrichment events.")

    print("\n=== SPOTIFY ENRICH RESULTS ===\n")
    for r in results:
        print(
            r["title"], "|",
            "ISRC:", r["isrc"], "|",
            "Spotify:", r["track_id"], "|",
            "Pop:", r["popularity"]
        )


if __name__ == "__main__":
    main()
