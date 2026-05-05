#!/usr/bin/env python3
"""
youtube_tag_update.py — YouTube Data API v3 tag enrichment
iZLET_sustav | Layer: metadata

Fetches existing tags for each video, merges with add_tags (no duplicates),
and updates via videos.update. Saves OAuth token to registries/.youtube_token.json.

Usage:
    python scripts/youtube_tag_update.py

Requires in .env (project root):
    YOUTUBE_CLIENT_ID=...
    YOUTUBE_CLIENT_SECRET=...
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ── Paths ────────────────────────────────────────────────────────────────────

ROOT        = Path(__file__).parent.parent
TOKEN_PATH  = ROOT / "registries" / ".youtube_token.json"

# ── Config ────────────────────────────────────────────────────────────────────

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

VIDEOS = [
    {
        "id": "zOVPy32dfIg",
        "add_tags": [
            "domovinski rat",
            "domovinski rat hrvatska",
            "live performance hrvatska",
            "street performance croatia",
            "croatian patriotic music",
        ],
    },
    {
        "id": "-S2B0VGQg7A",
        "add_tags": [
            "domovinski rat",
            "domovinski rat hrvatska",
            "hrvatska glazba",
            "live performance hrvatska",
            "street performance croatia",
            "croatian patriotic music",
        ],
    },
    {
        "id": "_jUXsiMeyiM",
        "add_tags": [
            "domovinski rat",
            "domovinski rat hrvatska",
            "croatian patriotic music",
        ],
    },
    {
        "id": "_8gaqROsmvU",
        "add_tags": [
            "domovinski rat",
            "domovinski rat hrvatska",
            "live performance hrvatska",
            "street performance croatia",
            "croatian patriotic music",
        ],
    },
    {
        "id": "3wsqpwuWEMM",
        "add_tags": [
            "domovinski rat",
            "domovinski rat hrvatska",
            "live performance hrvatska",
            "street performance croatia",
            "croatian patriotic music",
        ],
    },
]

# ── Credentials ───────────────────────────────────────────────────────────────

load_dotenv(ROOT / ".env")
CLIENT_ID     = os.environ.get("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise SystemExit(
        "❌  Missing YouTube OAuth credentials in .env\n"
        "    Required:\n"
        "      YOUTUBE_CLIENT_ID=...\n"
        "      YOUTUBE_CLIENT_SECRET=...\n"
        "    Get them at: https://console.cloud.google.com/apis/credentials"
    )

_CLIENT_CONFIG = {
    "installed": {
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uris": ["http://localhost"],
        "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
        "token_uri":     "https://oauth2.googleapis.com/token",
    }
}

# ── Auth ──────────────────────────────────────────────────────────────────────

def _load_credentials() -> Credentials | None:
    if not TOKEN_PATH.exists():
        return None
    with open(TOKEN_PATH, encoding="utf-8") as f:
        data = json.load(f)
    creds = Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=data.get("client_id", CLIENT_ID),
        client_secret=data.get("client_secret", CLIENT_SECRET),
        scopes=data.get("scopes", SCOPES),
    )
    return creds


def _save_credentials(creds: Credentials) -> None:
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "token":         creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri":     creds.token_uri,
        "client_id":     creds.client_id,
        "client_secret": creds.client_secret,
        "scopes":        list(creds.scopes or SCOPES),
        "generated_at":  datetime.now(timezone.utc).isoformat(),
    }
    with open(TOKEN_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def get_credentials() -> Credentials:
    creds = _load_credentials()

    if creds and creds.valid:
        print("  Token loaded from cache.")
        return creds

    if creds and creds.expired and creds.refresh_token:
        print("  Token expired — refreshing…")
        creds.refresh(Request())
        _save_credentials(creds)
        print("  Token refreshed and saved.")
        return creds

    print("  No valid token — starting OAuth2 flow…")
    flow = InstalledAppFlow.from_client_config(_CLIENT_CONFIG, SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")
    _save_credentials(creds)
    print(f"  Token saved → {TOKEN_PATH}")
    return creds


# ── YouTube tag operations ────────────────────────────────────────────────────

def fetch_snippet(youtube, video_id: str) -> dict:
    response = youtube.videos().list(
        part="snippet",
        id=video_id,
    ).execute()

    items = response.get("items", [])
    if not items:
        raise RuntimeError(f"Video not found: {video_id}")
    return items[0]["snippet"]


def merge_tags(existing: list[str], add_tags: list[str]) -> list[str]:
    existing_lower = {t.lower() for t in existing}
    merged = list(existing)
    for tag in add_tags:
        if tag.lower() not in existing_lower:
            merged.append(tag)
            existing_lower.add(tag.lower())
    return merged


def update_tags(youtube, video_id: str, snippet: dict, merged_tags: list[str]) -> None:
    snippet["tags"] = merged_tags
    youtube.videos().update(
        part="snippet",
        body={
            "id":      video_id,
            "snippet": snippet,
        },
    ).execute()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("\n  YouTube Tag Update — iZLET")
    print("  ──────────────────────────")

    creds   = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    print(f"\n  Processing {len(VIDEOS)} videos…\n")

    for entry in VIDEOS:
        video_id = entry["id"]
        add_tags = entry["add_tags"]

        try:
            snippet  = fetch_snippet(youtube, video_id)
            title    = snippet.get("title", video_id)
            existing = snippet.get("tags") or []
            merged   = merge_tags(existing, add_tags)
            added    = len(merged) - len(existing)

            if added == 0:
                print(f"  ✓  {video_id}  [{title[:50]}]")
                print(f"     Tags unchanged ({len(existing)} tags — all already present)\n")
                continue

            update_tags(youtube, video_id, snippet, merged)
            print(f"  ✅  {video_id}  [{title[:50]}]")
            print(f"     Tags: {len(existing)} → {len(merged)}  (+{added} new)\n")

        except Exception as e:
            print(f"  ❌  {video_id} — {e}\n")

    print("  Done.\n")


if __name__ == "__main__":
    main()
