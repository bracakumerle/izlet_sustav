"""
spotify_works_enricher.py
─────────────────────────
Matches works_registry.json titles against the full iZLET Spotify discography.

Outputs a human-readable preview table + writes data/spotify_enrichment_preview.json.
Does NOT modify works_registry.json — all matches require manual confirmation.

Usage:
    python izlet_os/enrichers/spotify_works_enricher.py

Requires in .env (project root):
    SPOTIFY_CLIENT_ID=...
    SPOTIFY_CLIENT_SECRET=...
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

import requests

# ── Paths ──────────────────────────────────────────────────────────────────

SCRIPT_DIR   = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
WORKS_PATH   = PROJECT_ROOT / "works_registry.json"
PREVIEW_PATH = PROJECT_ROOT / "data" / "spotify_enrichment_preview.json"
ENV_PATH     = PROJECT_ROOT / ".env"

# ── Constants ──────────────────────────────────────────────────────────────

ARTIST_ID        = "11wCFDSyZy0LfWkgllak6d"
TOKEN_URL        = "https://accounts.spotify.com/api/token"
API_BASE         = "https://api.spotify.com/v1"
FUZZY_THRESHOLD  = 0.82   # SequenceMatcher ratio for a soft match
AMBIGUOUS_MARGIN = 0.06   # top-2 scores within this → AMBIGUOUS

# Croatian diacritics → ASCII (đ has no unicode decomposition to 'd')
_DIACRITIC = str.maketrans("žšćčđŽŠĆČĐ", "zsccdzsccd")


# ── Normalisation ──────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    """Lowercase, map Croatian diacritics, strip punctuation, collapse spaces."""
    text = text.lower().translate(_DIACRITIC)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


# ── .env loader ────────────────────────────────────────────────────────────

def _load_env() -> None:
    if not ENV_PATH.exists():
        return
    with open(ENV_PATH, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


# ── Spotify client ──────────────────────────────────────────────────────────

class SpotifyClient:
    def __init__(self, client_id: str, client_secret: str):
        self._id     = client_id
        self._secret = client_secret
        self._token  = self._fetch_token()
        self.headers = {"Authorization": f"Bearer {self._token}"}

    def _fetch_token(self) -> str:
        r = requests.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(self._id, self._secret),
            timeout=10,
        )
        r.raise_for_status()
        return r.json()["access_token"]

    def _get(self, endpoint: str, params: dict | None = None) -> dict:
        url = f"{API_BASE}/{endpoint}"
        for attempt in range(3):
            r = requests.get(url, headers=self.headers, params=params or {}, timeout=15)
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 5)) + 1
                print(f"    ⏳ rate-limited — waiting {wait}s")
                time.sleep(wait)
                continue
            if r.status_code == 401:
                # token expired mid-run — refresh once
                self._token = self._fetch_token()
                self.headers["Authorization"] = f"Bearer {self._token}"
                continue
            r.raise_for_status()
            return r.json()
        raise RuntimeError(f"Failed after retries: {endpoint}")

    # ── Discography fetch ──────────────────────────────────────────────────

    def fetch_artist_albums(self, artist_id: str) -> list[dict]:
        """Return all release stubs (album, single, compilation)."""
        albums, offset = [], 0
        while True:
            data = self._get(
                f"artists/{artist_id}/albums",
                {"include_groups": "album,single,compilation", "limit": 50, "offset": offset},
            )
            items = data.get("items", [])
            albums.extend(items)
            if not data.get("next"):
                break
            offset += 50
            time.sleep(0.2)
        return albums

    def fetch_album_tracks(self, album_id: str) -> list[dict]:
        """Return simplified track objects for one album."""
        tracks, offset = [], 0
        while True:
            data = self._get(f"albums/{album_id}/tracks", {"limit": 50, "offset": offset})
            tracks.extend(data.get("items", []))
            if not data.get("next"):
                break
            offset += 50
            time.sleep(0.15)
        return tracks

    def fetch_tracks_batch(self, track_ids: list[str]) -> list[dict]:
        """Full track objects (includes ISRC) in batches of 50."""
        result = []
        for i in range(0, len(track_ids), 50):
            batch = track_ids[i : i + 50]
            data  = self._get("tracks", {"ids": ",".join(batch)})
            result.extend(t for t in (data.get("tracks") or []) if t)
            time.sleep(0.2)
        return result

    def build_catalog(self, artist_id: str) -> list[dict]:
        """
        Full discography catalog with ISRCs.
        Returns list of:
          {track_id, title, normalized, album, year, isrc, duration_ms}
        """
        print(f"\n  → Fetching releases for artist {artist_id}…")
        albums = self.fetch_artist_albums(artist_id)
        # deduplicate by album id (markets can cause duplicates)
        seen_albums: set[str] = set()
        unique_albums = []
        for a in albums:
            if a["id"] not in seen_albums:
                seen_albums.add(a["id"])
                unique_albums.append(a)
        print(f"    {len(unique_albums)} unique releases found")

        raw_tracks: list[dict] = []
        seen_tracks: set[str] = set()
        for alb in unique_albums:
            for t in self.fetch_album_tracks(alb["id"]):
                if t["id"] not in seen_tracks:
                    seen_tracks.add(t["id"])
                    raw_tracks.append({
                        "track_id":    t["id"],
                        "title":       t["name"],
                        "normalized":  normalize(t["name"]),
                        "album":       alb["name"],
                        "year":        (alb.get("release_date") or "")[:4],
                        "duration_ms": t.get("duration_ms"),
                        "isrc":        None,
                    })

        print(f"    {len(raw_tracks)} unique tracks found — fetching ISRCs…")
        full = self.fetch_tracks_batch([t["track_id"] for t in raw_tracks])
        isrc_map = {ft["id"]: ft.get("external_ids", {}).get("isrc") for ft in full}
        for t in raw_tracks:
            t["isrc"] = isrc_map.get(t["track_id"])

        return raw_tracks


# ── Matcher ─────────────────────────────────────────────────────────────────

class WorksMatcher:
    def __init__(self, catalog: list[dict]):
        # group by normalized title → list of tracks (same title, different releases)
        self.catalog = catalog
        self._index: dict[str, list[dict]] = {}
        for t in catalog:
            self._index.setdefault(t["normalized"], []).append(t)

    def match(self, work_key: str, title_normalized: str, title_original: str) -> dict:
        """
        Returns a match result dict:
          status: EXACT | FUZZY | AMBIGUOUS | NOT_FOUND
          candidates: list of candidate dicts (may be multiple)
          confidence: float (1.0 for EXACT, ratio for others)
        """
        # 1. Exact match
        if title_normalized in self._index:
            candidates = self._index[title_normalized]
            return {
                "status":     "EXACT",
                "confidence": 1.0,
                "candidates": candidates,
            }

        # 2. Fuzzy — score every catalog entry
        scored: list[tuple[float, dict]] = []
        for t in self.catalog:
            score = similarity(title_normalized, t["normalized"])
            scored.append((score, t))
        scored.sort(key=lambda x: x[0], reverse=True)

        best_score, best_track = scored[0]

        if best_score < FUZZY_THRESHOLD:
            return {
                "status":     "NOT_FOUND",
                "confidence": best_score,
                "candidates": [best_track],  # nearest miss for diagnostics
            }

        # Collect all tracks tied at best_score (or within AMBIGUOUS_MARGIN)
        top_candidates = [t for s, t in scored if s >= best_score - AMBIGUOUS_MARGIN]

        if len(top_candidates) > 1:
            second_score = scored[1][0]
            if abs(best_score - second_score) <= AMBIGUOUS_MARGIN:
                return {
                    "status":     "AMBIGUOUS",
                    "confidence": best_score,
                    "candidates": top_candidates[:5],
                }

        return {
            "status":     "FUZZY",
            "confidence": best_score,
            "candidates": [best_track],
        }


# ── Reporting ───────────────────────────────────────────────────────────────

STATUS_EMOJI = {
    "EXACT":     "✅",
    "FUZZY":     "🟡",
    "AMBIGUOUS": "⚠️ ",
    "NOT_FOUND": "❌",
}

COL = {
    "EXACT":     "\033[92m",   # green
    "FUZZY":     "\033[93m",   # yellow
    "AMBIGUOUS": "\033[95m",   # magenta
    "NOT_FOUND": "\033[91m",   # red
    "RESET":     "\033[0m",
}


def _col(status: str, text: str) -> str:
    return f"{COL.get(status, '')}{text}{COL['RESET']}"


def print_preview(results: list[dict]) -> None:
    counts = {"EXACT": 0, "FUZZY": 0, "AMBIGUOUS": 0, "NOT_FOUND": 0}

    print("\n" + "═" * 100)
    print(f"  {'#':<4}  {'STATUS':<12}  {'WORK TITLE':<30}  {'SPOTIFY MATCH':<32}  {'ISRC':<15}  CONF")
    print("═" * 100)

    for r in results:
        status = r["status"]
        counts[status] += 1
        emoji  = STATUS_EMOJI[status]
        conf   = f"{r['confidence']:.2f}"
        title  = r["title_normalized"][:29]

        if status in ("EXACT", "FUZZY") and r["candidates"]:
            c = r["candidates"][0]
            match_title = f"{c['title'][:28]}  [{c['year']}]"
            isrc        = c.get("isrc") or "—"
            tid         = c["track_id"]
        elif status == "AMBIGUOUS":
            match_title = f"{len(r['candidates'])} candidates"
            isrc, tid   = "—", "—"
        else:
            c = r["candidates"][0] if r["candidates"] else {}
            match_title = f"nearest: {c.get('title', '')[:22]}"
            isrc, tid   = "—", "—"

        row = (
            f"  {r['rank']:<4}  "
            f"{emoji} {status:<10}  "
            f"{title:<30}  "
            f"{match_title:<32}  "
            f"{isrc:<15}  "
            f"{conf}"
        )
        print(_col(status, row))

        # For AMBIGUOUS, list all candidates indented
        if status == "AMBIGUOUS":
            for c in r["candidates"]:
                cline = (
                    f"         {'':12}  {'':30}  "
                    f"  → {c['title'][:30]} [{c['year']}]  "
                    f"{c.get('isrc') or '—'}"
                )
                print(_col("AMBIGUOUS", cline))

    print("═" * 100)
    total = sum(counts.values())
    print(
        f"\n  SUMMARY  total={total}  "
        f"✅ EXACT={counts['EXACT']}  "
        f"🟡 FUZZY={counts['FUZZY']}  "
        f"⚠️  AMBIGUOUS={counts['AMBIGUOUS']}  "
        f"❌ NOT_FOUND={counts['NOT_FOUND']}"
    )
    print()


def build_preview_json(results: list[dict], catalog: list[dict]) -> dict:
    """Structured preview suitable for manual review and future --apply step."""
    confirmed_matches = []
    review_required   = []
    not_found         = []

    for r in results:
        status = r["status"]
        base   = {
            "work_key":         r["work_key"],
            "rank":             r["rank"],
            "title_original":   r["title_original"],
            "title_normalized":  r["title_normalized"],
            "iswc":             r["iswc"],
            "status":           status,
            "confidence":       round(r["confidence"], 4),
        }

        if status in ("EXACT", "FUZZY") and r["candidates"]:
            c = r["candidates"][0]
            base["spotify_track_id"] = c["track_id"]
            base["isrc"]             = c.get("isrc")
            base["matched_title"]    = c["title"]
            base["matched_album"]    = c["album"]
            base["matched_year"]     = c["year"]
            confirmed_matches.append(base)

        elif status == "AMBIGUOUS":
            base["candidates"] = [
                {
                    "spotify_track_id": c["track_id"],
                    "isrc":             c.get("isrc"),
                    "title":            c["title"],
                    "album":            c["album"],
                    "year":             c["year"],
                    "confidence":       round(similarity(r["title_normalized"], c["normalized"]), 4),
                }
                for c in r["candidates"]
            ]
            review_required.append(base)

        else:
            base["nearest_title"] = r["candidates"][0].get("title") if r["candidates"] else None
            not_found.append(base)

    return {
        "_generated":          datetime.now(timezone.utc).isoformat(),
        "_artist_id":          ARTIST_ID,
        "_catalog_size":       len(catalog),
        "_fuzzy_threshold":    FUZZY_THRESHOLD,
        "_ambiguous_margin":   AMBIGUOUS_MARGIN,
        "summary": {
            "total":       len(results),
            "exact":       sum(1 for r in results if r["status"] == "EXACT"),
            "fuzzy":       sum(1 for r in results if r["status"] == "FUZZY"),
            "ambiguous":   sum(1 for r in results if r["status"] == "AMBIGUOUS"),
            "not_found":   sum(1 for r in results if r["status"] == "NOT_FOUND"),
        },
        "confirmed_matches":   confirmed_matches,
        "review_required":     review_required,
        "not_found":           not_found,
        "_apply_instruction": (
            "To apply: copy spotify_track_id + isrc from confirmed_matches into "
            "works_registry.json manually, or run enricher with --apply flag (not yet implemented)."
        ),
    }


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Spotify Works Enricher — iZLET discography matcher     ║")
    print("║  READ-ONLY preview mode — works_registry.json untouched ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # ── credentials ──────────────────────────────────────────────────────
    _load_env()
    client_id     = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("\n❌  Missing Spotify credentials.")
        print("    Add to .env (project root):")
        print("      SPOTIFY_CLIENT_ID=<your_client_id>")
        print("      SPOTIFY_CLIENT_SECRET=<your_client_secret>")
        print("\n    Get them at: https://developer.spotify.com/dashboard")
        sys.exit(1)

    # ── load works ───────────────────────────────────────────────────────
    if not WORKS_PATH.exists():
        print(f"\n❌  works_registry.json not found at {WORKS_PATH}")
        sys.exit(1)

    with open(WORKS_PATH, encoding="utf-8") as f:
        registry = json.load(f)

    works = registry.get("works", {})
    print(f"\n  → Loaded {len(works)} works from works_registry.json")

    # ── build Spotify catalog ─────────────────────────────────────────────
    client  = SpotifyClient(client_id, client_secret)
    catalog = client.build_catalog(ARTIST_ID)
    print(f"    Catalog built: {len(catalog)} tracks with ISRCs")

    # ── match ─────────────────────────────────────────────────────────────
    matcher = WorksMatcher(catalog)
    results: list[dict] = []

    print("\n  → Matching works against catalog…")
    for work_key, work in works.items():
        title_norm = normalize(work.get("title_normalized", work.get("title_original", "")))
        result     = matcher.match(work_key, title_norm, work.get("title_original", ""))
        results.append({
            "work_key":         work_key,
            "rank":             work.get("rank"),
            "title_original":   work.get("title_original"),
            "title_normalized": work.get("title_normalized"),
            "iswc":             work.get("iswc"),
            **result,
        })

    # sort by rank
    results.sort(key=lambda r: r.get("rank") or 999)

    # ── print preview ─────────────────────────────────────────────────────
    print_preview(results)

    # ── write preview JSON ────────────────────────────────────────────────
    preview = build_preview_json(results, catalog)
    PREVIEW_PATH.parent.mkdir(exist_ok=True)
    with open(PREVIEW_PATH, "w", encoding="utf-8") as f:
        json.dump(preview, f, ensure_ascii=False, indent=2)

    print(f"  Preview JSON → {PREVIEW_PATH}")
    print(f"\n  ⚠️  works_registry.json was NOT modified.")
    print(f"  Review the preview, then manually copy spotify_track_id + isrc into works_registry.json.")
    print()


if __name__ == "__main__":
    main()
