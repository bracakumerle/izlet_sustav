#!/usr/bin/env python3
"""
spotify_ingest.py — Spotify artist metrics ingestion
iZLET_sustav | Layer: metrics_registry

Loads token from registries/.spotify_token.json, refreshes if expired,
fetches artist data and writes to metrics_registry.json spotify block.

Usage:
    python scripts/spotify_ingest.py
"""

import base64
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

# ── Paths ───────────────────────────────────────────────────────────────────

ROOT         = Path(__file__).parent.parent
TOKEN_PATH   = ROOT / "registries" / ".spotify_token.json"
METRICS_PATH = ROOT / "metrics_registry.json"

# ── Constants ────────────────────────────────────────────────────────────────

CLIENT_ID  = "a638c04d2b6043b1a4c3adda6db5bad9"
ARTIST_ID  = "11wCFDSyZy0LfWkgllak6d"
TOKEN_URL  = "https://accounts.spotify.com/api/token"
ARTIST_URL = f"https://api.spotify.com/v1/artists/{ARTIST_ID}"

load_dotenv(ROOT / ".env")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
if not CLIENT_SECRET:
    raise SystemExit("❌  SPOTIFY_CLIENT_SECRET not found in .env")


# ── Token management ─────────────────────────────────────────────────────────

def _load_token() -> dict:
    if not TOKEN_PATH.exists():
        raise SystemExit(
            f"❌  Token not found: {TOKEN_PATH}\n"
            "    Run scripts/spotify_auth.py first."
        )
    with open(TOKEN_PATH, encoding="utf-8") as f:
        return json.load(f)


def _is_expired(token: dict) -> bool:
    generated_at = token.get("generated_at")
    expires_in   = token.get("expires_in", 3600)
    if not generated_at:
        return True
    issued = datetime.fromisoformat(generated_at)
    age    = (datetime.now(timezone.utc) - issued).total_seconds()
    return age >= expires_in - 60  # 60s safety margin


def _reauth() -> dict:
    print("  Token expired — re-authenticating (client credentials)…")
    credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    r = requests.post(
        TOKEN_URL,
        data={"grant_type": "client_credentials"},
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type":  "application/x-www-form-urlencoded",
        },
        timeout=15,
    )
    if not r.ok:
        raise SystemExit(f"❌  Re-auth failed: HTTP {r.status_code} — {r.text}")

    token = {
        **r.json(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "client_id":    CLIENT_ID,
        "flow":         "client_credentials",
    }
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_PATH, "w", encoding="utf-8") as f:
        json.dump(token, f, indent=2, ensure_ascii=False)
    print("  Token saved.")
    return token


def _get_access_token() -> str:
    token = _load_token()
    if _is_expired(token):
        token = _reauth()
    return token["access_token"]


# ── Helpers ──────────────────────────────────────────────────────────────────

def safe_int(value):
    return int(value) if isinstance(value, (int, float)) else None


# ── Spotify fetch ────────────────────────────────────────────────────────────

def _fetch_artist(access_token: str) -> dict:
    print(f"  Endpoint: GET {ARTIST_URL}")
    r = requests.get(
        ARTIST_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    if not r.ok:
        raise SystemExit(f"❌  Artist fetch failed: HTTP {r.status_code} — {r.text}")
    data = r.json()
    print("\n  --- RAW API RESPONSE ---")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("  --- END RESPONSE ---\n")
    return data


# ── Registry update ──────────────────────────────────────────────────────────

def _update_metrics(followers: int, popularity: int) -> None:
    with open(METRICS_PATH, encoding="utf-8") as f:
        registry = json.load(f)

    today = datetime.now(timezone.utc).date().isoformat()

    for entry in registry.get("metrics", []):
        if entry.get("entity_id") == "izlet" and entry.get("platform") == "spotify":
            entry["timestamp"] = today
            entry["source"]    = "api_pull"
            entry["data"].update({
                "followers":  followers,
                "popularity": popularity,
            })
            entry.pop("note", None)
            break

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print("\n  Spotify Ingest — iZLET artist metrics")
    print("  ──────────────────────────────────────")

    access_token = _get_access_token()
    print(f"  Token OK (access_token: {access_token[:24]}…)")

    print(f"  Fetching artist {ARTIST_ID}…")
    artist = _fetch_artist(access_token)

    print(f"  Fields present in response: {sorted(artist.keys())}")

    followers  = safe_int(artist.get("followers", {}).get("total"))
    popularity = safe_int(artist.get("popularity"))
    name       = artist.get("name", "iZLET")

    if followers is None:
        print("  ⚠️   'followers' field missing from API response")
    if popularity is None:
        print("  ⚠️   'popularity' field missing from API response")

    followers_str  = f"{followers:,}"  if isinstance(followers,  int) else "N/A"
    popularity_str = f"{popularity}"   if isinstance(popularity, int) else "N/A"

    print(f"  Artist    : {name}")
    print(f"  Followers : {followers_str}")
    print(f"  Popularity: {popularity_str}/100" if isinstance(popularity, int) else f"  Popularity: {popularity_str}")

    _update_metrics(followers, popularity)

    print(f"\n  ✅  metrics_registry.json updated")
    print(f"      platform   : spotify")
    print(f"      followers  : {followers_str}")
    print(f"      popularity : {popularity_str}")
    print(f"      source     : api_pull")
    print(f"      confidence : high\n")


if __name__ == "__main__":
    main()
