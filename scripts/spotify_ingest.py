#!/usr/bin/env python3
"""
spotify_ingest.py — Spotify artist metrics ingestion
iZLET_sustav | Layer: metrics_registry

Loads token from registries/.spotify_token.json, refreshes if expired,
fetches artist data and writes to metrics_registry.json spotify block.

Usage:
    python scripts/spotify_ingest.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

# ── Paths ───────────────────────────────────────────────────────────────────

ROOT           = Path(__file__).parent.parent
TOKEN_PATH     = ROOT / "registries" / ".spotify_token.json"
METRICS_PATH   = ROOT / "metrics_registry.json"

# ── Constants ────────────────────────────────────────────────────────────────

CLIENT_ID  = "a638c04d2b6043b1a4c3adda6db5bad9"
ARTIST_ID  = "11wCFDSyZy0LfWkgllak6d"
TOKEN_URL  = "https://accounts.spotify.com/api/token"
ARTIST_URL = f"https://api.spotify.com/v1/artists/{ARTIST_ID}"


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


def _refresh(token: dict) -> dict:
    refresh_token = token.get("refresh_token")
    if not refresh_token:
        raise SystemExit(
            "❌  No refresh_token in .spotify_token.json.\n"
            "    Re-run scripts/spotify_auth.py to get a new token."
        )
    print("  Token expired — refreshing…")
    r = requests.post(
        TOKEN_URL,
        data={
            "grant_type":    "refresh_token",
            "refresh_token": refresh_token,
            "client_id":     CLIENT_ID,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    if not r.ok:
        raise SystemExit(f"❌  Refresh failed: HTTP {r.status_code} — {r.text}")

    new_token = r.json()
    merged = {
        **token,
        **new_token,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "client_id":    CLIENT_ID,
        "flow":         "pkce",
    }
    # Spotify may not return a new refresh_token — keep the old one
    if "refresh_token" not in new_token:
        merged["refresh_token"] = refresh_token

    with open(TOKEN_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    print("  Token refreshed and saved.")
    return merged


def _get_access_token() -> str:
    token = _load_token()
    if _is_expired(token):
        token = _refresh(token)
    return token["access_token"]


# ── Spotify fetch ────────────────────────────────────────────────────────────

def _fetch_artist(access_token: str) -> dict:
    r = requests.get(
        ARTIST_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    if not r.ok:
        raise SystemExit(f"❌  Artist fetch failed: HTTP {r.status_code} — {r.text}")
    return r.json()


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

    followers   = artist["followers"]["total"]
    popularity  = artist["popularity"]
    name        = artist.get("name", "iZLET")

    print(f"  Artist   : {name}")
    print(f"  Followers: {followers:,}")
    print(f"  Popularity: {popularity}/100")

    _update_metrics(followers, popularity)

    print(f"\n  ✅  metrics_registry.json updated")
    print(f"      platform   : spotify")
    print(f"      followers  : {followers:,}")
    print(f"      popularity : {popularity}")
    print(f"      source     : api_pull")
    print(f"      confidence : high\n")


if __name__ == "__main__":
    main()
