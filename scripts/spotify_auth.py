#!/usr/bin/env python3
"""
spotify_auth.py — Spotify Client Credentials flow
iZLET_sustav | Layer: auth

No browser, no user login. Fetches an app-level access token
with full public API access. Valid for 1h; re-run to refresh.

Usage:
    python scripts/spotify_auth.py

Requires in .env (project root):
    SPOTIFY_CLIENT_SECRET=...
"""

import base64
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

# ── Config ──────────────────────────────────────────────────────────────────

CLIENT_ID  = "a638c04d2b6043b1a4c3adda6db5bad9"
TOKEN_URL  = "https://accounts.spotify.com/api/token"
TOKEN_PATH = Path(__file__).parent.parent / "registries" / ".spotify_token.json"

# ── Credentials ─────────────────────────────────────────────────────────────

load_dotenv(Path(__file__).parent.parent / ".env")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
if not CLIENT_SECRET:
    raise SystemExit(
        "❌  SPOTIFY_CLIENT_SECRET not found in .env\n"
        "    Add: SPOTIFY_CLIENT_SECRET=<your_secret>"
    )

# ── Token fetch ──────────────────────────────────────────────────────────────

def fetch_token() -> dict:
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
        raise SystemExit(f"❌  Auth failed: HTTP {r.status_code} — {r.text}")
    return r.json()


def save_token(token: dict) -> None:
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        **token,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "client_id":    CLIENT_ID,
        "flow":         "client_credentials",
    }
    with open(TOKEN_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print("\n  Spotify Auth — Client Credentials")
    print("  ───────────────────────────────────")
    print("  Fetching token…")

    token = fetch_token()
    save_token(token)

    expires_in = token.get("expires_in", 3600)
    print(f"\n  ✅  Token saved → {TOKEN_PATH}")
    print(f"      access_token : {token['access_token'][:24]}…")
    print(f"      token_type   : {token.get('token_type')}")
    print(f"      expires_in   : {expires_in}s ({expires_in // 60} min)")
    print(f"      flow         : client_credentials\n")


if __name__ == "__main__":
    main()
