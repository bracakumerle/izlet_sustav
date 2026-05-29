#!/usr/bin/env python3
"""
youtube_tag_replace.py — Remove specific tags and set new ones for a single video.
iZLET_sustav | one-off tag remediation
"""

import io, json, os, sys, datetime, traceback
from pathlib import Path
from datetime import timezone

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", write_through=True)

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ROOT         = Path(__file__).parent.parent
TOKEN_PATH   = ROOT / "registries" / ".youtube_token.json"
SCOPES       = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# ── Target video ──────────────────────────────────────────────────────────────

VIDEO_ID = "1gPfgO3daPk"

REMOVE_TAGS = [
    # explicit matches
    "ndh", "ustaše", "poglavnik", "ustaški pokret", "ustaski pokret",
    "ndr", "nsh", "ndh hrvatska",
    # variants caught in first pass — now explicit
    "ustase", "ustasa", "ustaske pjesme", "ustaške pjesme",
    "ustaša", "ustše", "ustashe", "ustaška se vojska diže",
    "independent state of croatia", "ustaski", "ustasha",
    "slavko kvaternik", "eugen dido kvaternik", "stanko šarić",
    "poglavnik pavelić", "poglavnik ante pavelić", "kvaternik poglavnik",
    "ustaški poglavnik",
]

# substring keywords — any tag containing these is also removed
REMOVE_KEYWORDS = ["ustash", "ustasa", "ustase", "ustase", "poglavni", "ndh", "pavelić", "kvaternik"]

ADD_TAGS = [
    "iZLET",
    "Katarza",
    "čast",
    "hrvatska",
    "domoljubna glazba",
    "rock",
    "Braća Kumerle",
    "ISRC HRA371800845",
]

# ── Auth ──────────────────────────────────────────────────────────────────────

load_dotenv(ROOT / ".env")
CLIENT_ID     = os.environ.get("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")

_CLIENT_CONFIG = {
    "installed": {
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uris": ["http://localhost"],
        "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
        "token_uri":     "https://oauth2.googleapis.com/token",
    }
}


def get_credentials():
    if TOKEN_PATH.exists():
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
        if creds.valid:
            print("  Token loaded from cache.")
            return creds
        if creds.expired and creds.refresh_token:
            print("  Token expired — refreshing…")
            creds.refresh(Request())
            _save(creds)
            return creds

    print("  Starting OAuth2 flow…")
    flow = InstalledAppFlow.from_client_config(_CLIENT_CONFIG, SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")
    _save(creds)
    return creds


def _save(creds):
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "token":         creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri":     creds.token_uri,
        "client_id":     creds.client_id,
        "client_secret": creds.client_secret,
        "scopes":        list(creds.scopes or SCOPES),
        "generated_at":  datetime.datetime.now(timezone.utc).isoformat(),
    }
    with open(TOKEN_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"  Token saved → {TOKEN_PATH}")


# ── Tag logic ─────────────────────────────────────────────────────────────────

def should_remove(tag):
    t = tag.lower().strip()
    if any(t == r.lower() for r in REMOVE_TAGS):
        return True
    if any(kw in t for kw in REMOVE_KEYWORDS):
        return True
    return False


def main():
    print(f"\n  YouTube Tag Replace — video: {VIDEO_ID}")
    print("  " + "─" * 50)

    creds   = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    # Fetch snippet
    resp  = youtube.videos().list(part="snippet", id=VIDEO_ID).execute()
    items = resp.get("items", [])
    if not items:
        raise SystemExit(f"Video not found: {VIDEO_ID}")

    snippet  = items[0]["snippet"]
    title    = snippet.get("title", VIDEO_ID)
    existing = snippet.get("tags") or []

    print(f"\n  Title    : {title}")
    print(f"  Existing tags ({len(existing)}): {existing}")

    # Filter out removed tags
    kept    = [t for t in existing if not should_remove(t)]
    removed = [t for t in existing if should_remove(t)]

    print(f"\n  Tags to REMOVE ({len(removed)}): {removed}")
    print(f"  Tags to ADD    ({len(ADD_TAGS)}): {ADD_TAGS}")

    # Merge: kept + new (dedup, preserve order)
    final = list(dict.fromkeys(kept + ADD_TAGS))
    print(f"\n  Final tag set ({len(final)}): {final}")

    # Build snippet body (YouTube requires title + categoryId)
    body_snippet = {k: snippet[k] for k in ("title", "categoryId", "defaultLanguage", "defaultAudioLanguage") if k in snippet}
    body_snippet["tags"] = final

    try:
        youtube.videos().update(
            part="snippet",
            body={"id": VIDEO_ID, "snippet": body_snippet},
        ).execute()
        print(f"\n  OK — tags updated successfully.")
        print(f"  Before: {len(existing)} tags  |  Removed: {len(removed)}  |  Added: {len(ADD_TAGS)}  |  After: {len(final)}")
    except HttpError as e:
        print(f"\n  FAIL: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
