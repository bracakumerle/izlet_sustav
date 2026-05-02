import requests
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

Q_IDS      = ["Q139595518", "Q139595619", "Q139595627"]
USER_AGENT = "izlet_sustav/1.0 (bracakumerle@gmail.com)"
API_URL    = "https://www.wikidata.org/w/api.php"
DATA_DIR   = Path(__file__).parent.parent.parent / "data"

# Wikidata property IDs we care about
PROPS = {
    "P31":   "instance_of",
    "P136":  "genre",
    "P17":   "country",
    "P495":  "country_of_origin",
    "P571":  "inception",
    "P577":  "publication_date",
    "P175":  "performer",
    "P264":  "record_label",
    "P856":  "official_website",
    "P1902": "spotify_artist_id",
    "P434":  "musicbrainz_artist_id",
    "P1045": "discogs_artist_id",
    "P2397": "youtube_channel_id",
    "P2047": "duration_min",
    "P18":   "image",
}


class WikidataAgent:
    def __init__(self):
        self.headers = {"User-Agent": USER_AGENT}
        self.url     = API_URL
        self.q_ids   = Q_IDS

    def fetch_entities(self) -> dict:
        params = {
            "action":    "wbgetentities",
            "ids":       "|".join(self.q_ids),
            "languages": "hr|en",
            "format":    "json",
        }
        r = requests.get(self.url, params=params, headers=self.headers, timeout=15)
        r.raise_for_status()
        return r.json().get("entities", {})

    def _claim_values(self, claims: dict, pid: str) -> list:
        vals = []
        for c in claims.get(pid, []):
            mv = c.get("mainsnak", {}).get("datavalue", {}).get("value")
            if mv is None:
                continue
            if isinstance(mv, dict):
                vals.append(
                    mv.get("id")
                    or mv.get("time")
                    or mv.get("text")
                    or str(mv)
                )
            else:
                vals.append(str(mv))
        return vals

    def _parse_entity(self, qid: str, entity: dict) -> dict:
        claims = entity.get("claims", {})
        parsed = {
            "qid":          qid,
            "labels":       {lang: v["value"] for lang, v in entity.get("labels", {}).items()},
            "descriptions": {lang: v["value"] for lang, v in entity.get("descriptions", {}).items()},
            "aliases": {
                lang: [a["value"] for a in vals]
                for lang, vals in entity.get("aliases", {}).items()
            },
        }
        for pid, field in PROPS.items():
            parsed[field] = self._claim_values(claims, pid)
        return parsed

    def snapshot(self) -> tuple:
        entities_raw = self.fetch_entities()
        parsed = {
            qid: self._parse_entity(qid, ent)
            for qid, ent in entities_raw.items()
        }

        now = datetime.now(timezone.utc).isoformat()

        snapshot = {
            "fetched_at": now,
            "q_ids":      self.q_ids,
            "entities":   parsed,
        }

        DATA_DIR.mkdir(exist_ok=True)

        snap_path = DATA_DIR / "wikidata_snapshot.json"
        with open(snap_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)

        # Change detection
        content_hash = hashlib.sha256(
            json.dumps(parsed, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()

        state_path = DATA_DIR / "wikidata_state.json"
        prev_state: dict = {}
        if state_path.exists():
            with open(state_path, "r", encoding="utf-8") as f:
                prev_state = json.load(f)

        changed = prev_state.get("hash") != content_hash

        state = {
            "last_checked":             now,
            "hash":                     content_hash,
            "changed_since_last_check": changed,
            "previous_check":           prev_state.get("last_checked"),
            "q_ids":                    self.q_ids,
        }

        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        return snapshot, snap_path, state_path, changed

    def check_entity(self, name: str) -> bool:
        """Legacy: check if a Wikidata entity exists by name search."""
        params = {
            "action":   "wbsearchentities",
            "search":   name,
            "language": "hr",
            "format":   "json",
        }
        try:
            r = requests.get(self.url, params=params, headers=self.headers, timeout=10)
            return len(r.json().get("search", [])) > 0
        except Exception:
            return False


if __name__ == "__main__":
    agent = WikidataAgent()
    snapshot, snap_path, state_path, changed = agent.snapshot()
    print(f"✅ Wikidata snapshot saved → {snap_path}")
    print(f"✅ Wikidata state saved   → {state_path}")
    for qid, ent in snapshot["entities"].items():
        label = ent["labels"].get("hr") or ent["labels"].get("en", qid)
        print(f"   {qid}: {label}")
    print(f"   Changed since last check: {changed}")
