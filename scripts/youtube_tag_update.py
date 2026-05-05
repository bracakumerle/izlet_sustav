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

import datetime
import io
import json
import os
import sys
import traceback
from pathlib import Path
from datetime import timezone

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", write_through=True)

from googleapiclient.errors import HttpError
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

def is_invalid_tag_error(e):
    try:
        msg = str(e).lower()
    except Exception:
        return False
    return any(s in msg for s in ("invalid", "tag", "parameter", "snippet"))


def log_event(video_id, mode, before, after, error=None):
    event = {
        "timestamp":   str(datetime.datetime.utcnow()),
        "video_id":    video_id,
        "mode":        mode,
        "tags_before": before,
        "tags_after":  after,
        "error":       str(error) if error else None,
    }
    sys.stdout.write("TAG_UPDATE_EVENT:" + json.dumps(event) + "\n")
    sys.stdout.flush()


def sanitize(tags):
    return [t.strip() for t in tags if isinstance(t, str) and t.strip()]


def _do_update(youtube, video_id, snippet, tags):
    # YouTube requires title + categoryId in snippet on every update
    body_snippet = {k: snippet[k] for k in ("title", "categoryId", "defaultLanguage", "defaultAudioLanguage") if k in snippet}
    body_snippet["tags"] = tags
    youtube.videos().update(
        part="snippet",
        body={"id": video_id, "snippet": body_snippet},
    ).execute()


def fetch_snippet(youtube, video_id: str) -> dict:
    response = youtube.videos().list(part="snippet", id=video_id).execute()
    items = response.get("items", [])
    if not items:
        raise RuntimeError(f"Video not found: {video_id}")
    return items[0]["snippet"]


def update_video_tags(youtube, video_id, snippet, existing_tags, new_tags):
    existing = sanitize(existing_tags)
    new      = sanitize(new_tags)
    merged   = list(dict.fromkeys(existing + new))

    last_error = None
    for tags, mode in [
        (merged, "merged"),
        (new,    "new_only"),
        (
            [t.encode("ascii", "ignore").decode("ascii").strip()
             for t in new
             if t.encode("ascii", "ignore").decode("ascii").strip()],
            "ascii_fallback",
        ),
    ]:
        try:
            _do_update(youtube, video_id, snippet, tags)
            log_event(video_id, mode, len(existing), len(tags))
            return mode, len(existing), len(tags)
        except HttpError as e:
            last_error = e
            print(f"  [fallback] {mode} failed: {e}", flush=True)
            if not is_invalid_tag_error(e):
                raise
        except Exception as final_error:
            log_event(video_id, "failed", len(existing), 0, final_error)
            print(traceback.format_exc(), flush=True)
            raise

    # All 3 stages exhausted
    log_event(video_id, "all_stages_failed", len(existing), 0, last_error)
    raise RuntimeError(f"All update stages failed for {video_id}: {last_error}")


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

        print(f"  Processing video: {video_id}", flush=True)

        try:
            snippet  = fetch_snippet(youtube, video_id)
            title    = snippet.get("title", video_id)
            existing = snippet.get("tags") or []
            print(f"  Fetched snippet OK — title: {title[:60]!r}  existing tags: {len(existing)}", flush=True)

            mode, before, after = update_video_tags(youtube, video_id, snippet, existing, add_tags)
            print(f"  OK  {video_id}  [{title[:50]}]", flush=True)
            print(f"      mode={mode}  tags: {before} -> {after}\n", flush=True)

        except Exception as e:
            print(f"  FAIL  {video_id} — {e}", flush=True)
            print(traceback.format_exc(), flush=True)
            print(flush=True)


if __name__ == "__main__":
    main()
