import requests
import json
import time
from pathlib import Path
from datetime import datetime, timezone

ARTIST_MBID = "b973e6f2-c282-473a-b2fb-ffb4466b312f"
USER_AGENT  = "izlet_sustav/1.0 (bracakumerle@gmail.com)"
BASE_URL    = "https://musicbrainz.org/ws/2/"
DATA_DIR    = Path(__file__).parent.parent.parent / "data"


class MusicBrainzAgent:
    def __init__(self):
        self.headers  = {"User-Agent": USER_AGENT}
        self.base_url = BASE_URL
        self.mbid     = ARTIST_MBID

    def _get(self, endpoint: str, params: dict = None) -> dict:
        if params is None:
            params = {}
        params["fmt"] = "json"
        time.sleep(1.1)  # MusicBrainz rate limit: max 1 req/sec
        r = requests.get(
            self.base_url + endpoint,
            params=params,
            headers=self.headers,
            timeout=15,
        )
        r.raise_for_status()
        return r.json()

    def fetch_artist(self) -> dict:
        return self._get(
            f"artist/{self.mbid}",
            {"inc": "release-groups+aliases+tags+ratings+url-rels"},
        )

    def fetch_release_groups(self) -> list:
        data = self._get("release-group", {
            "artist": self.mbid,
            "limit": 100,
        })
        return data.get("release-groups", [])

    def fetch_recordings(self) -> list:
        data = self._get("recording", {
            "artist": self.mbid,
            "limit": 100,
        })
        return data.get("recordings", [])

    def snapshot(self) -> tuple:
        artist        = self.fetch_artist()
        release_groups = self.fetch_release_groups()
        recordings    = self.fetch_recordings()

        snapshot = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "mbid": self.mbid,
            "artist": {
                "name":           artist.get("name"),
                "sort_name":      artist.get("sort-name"),
                "type":           artist.get("type"),
                "country":        artist.get("country"),
                "disambiguation": artist.get("disambiguation"),
                "begin":          artist.get("life-span", {}).get("begin"),
                "ended":          artist.get("life-span", {}).get("ended"),
                "aliases":        [a.get("name") for a in artist.get("aliases", [])],
                "tags":           [t.get("name") for t in artist.get("tags", [])],
                "rating":         artist.get("rating", {}).get("value"),
                "urls": [
                    {"type": rel.get("type"), "url": rel.get("url", {}).get("resource")}
                    for rel in artist.get("relations", [])
                    if rel.get("url")
                ],
            },
            "release_groups": [
                {
                    "id":                 rg.get("id"),
                    "title":              rg.get("title"),
                    "type":               rg.get("primary-type"),
                    "secondary_types":    rg.get("secondary-types", []),
                    "first_release_date": rg.get("first-release-date"),
                }
                for rg in release_groups
            ],
            "recordings": [
                {
                    "id":                 rec.get("id"),
                    "title":              rec.get("title"),
                    "length_ms":          rec.get("length"),
                    "first_release_date": rec.get("first-release-date"),
                    "video":              rec.get("video", False),
                }
                for rec in recordings
            ],
            "stats": {
                "release_group_count": len(release_groups),
                "recording_count":     len(recordings),
            },
        }

        DATA_DIR.mkdir(exist_ok=True)
        out = DATA_DIR / "mb_snapshot.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)

        return snapshot, out

    def check_authority(self, title: str) -> bool:
        """Legacy: check if a recording exists in MusicBrainz."""
        try:
            data = self._get("recording", {
                "query": f'recording:"{title}" AND artist:"iZLET"',
            })
            return data.get("count", 0) > 0
        except Exception:
            return False


if __name__ == "__main__":
    agent = MusicBrainzAgent()
    snapshot, path = agent.snapshot()
    print(f"✅ MusicBrainz snapshot saved → {path}")
    print(f"   Artist : {snapshot['artist']['name']}")
    print(f"   Releases: {snapshot['stats']['release_group_count']}")
    print(f"   Tracks  : {snapshot['stats']['recording_count']}")
