"""
youtube_tag_audit_bulk.py
Bulk tag audit + cleanup za iZLET YouTube corpus.

Modes:
  python scripts/youtube_tag_audit_bulk.py            → dry-run (samo log, nema YouTube write)
  python scripts/youtube_tag_audit_bulk.py --execute  → live write na YouTube

Output:
  registries/youtube_tag_audit_log.json  → per-video diff (before/after/removed/added)
"""

import os
import sys
import io
import re
import json
import time
import csv
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", write_through=True)
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────────────────────────

DRY_RUN = "--execute" not in sys.argv

CORPUS_CSV = Path("registries/youtube_corpus_scored.csv")
LOG_PATH   = Path("registries/youtube_tag_audit_log.json")
TOKEN_PATH = Path("registries/.youtube_token.json")

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Tags to remove from ALL videos (global blacklist)
GLOBAL_REMOVE = [
    # geo/brand signal
    "zds",
    "ex yu",
    "ex-yu",
    "balkanska glazba",
    "balkanski rock",
    "balkanski punk",
    "ex yu rock",
    "ex yu punk",
    "#balkanskisvijet",
    # muzika — srpski/BiH spelling variants
    "muzika",
    "muzika hrvatska",
    "hrvatska muzika",
    "narodna muzika",
    "live muzika",
    "duhovna muzika",
    "balkanska muzika",
    "muzika 2023",
    "muzika na javi",
    "muzika sa balkana",
    "muzika za party",
    "muzika za uživanje",
    "pop muzika",
    "striming muzika",
    "muzika nova",
    "muzika za opuštanje",
    "alternativna muzika",
    "kontemporarna muzika",
    "patriotska muzika",
    # YouTube auto-generated tags
    "(musical artist)",
    "(musical group)",
    "(musical recording)",
    "(musical genre)",
    "musical journey",
    "musical exploration",
    "musical analysis",
    "musical artistry",
    "musical tribute",
    "fete de la musique",
]

# Tags to remove from videos that are NOT Thompson covers/performances
# Applied to all videos UNLESS title contains "thompson" (case-insensitive)
THOMPSON_REMOVE = [
    "thompson",
    "marko perkovic thompson",
    "marko perković thompson",
    "marko perković",
    "thompson live",
    "thompson koncert",
    "thompson cover",
    "thompson songs",
    "thompson pjesme",
    "bojna čavoglave",
    "bojna cavoglave",
    "cavoglave",
    "ako ne znas sta je bilo",
    "ako ne znaš šta je bilo",
]

# Canonical tags added to ALL videos if not already present
CANONICAL_ADD = [
    "iZLET",
    "Braća Kumerle",
    "hrvatska glazba",
    "hrvatski rock",
    "Croatian music",
    "Croatian rock",
    "Hrvatska",
    "Croatia",
]

# Existing high-risk tags from youtube_tag_replace.py — apply globally
REMOVE_TAGS_EXPLICIT = [
    "ndh", "ustaše", "poglavnik", "ustaški pokret", "ustaski pokret",
    "ndr", "nsh", "ndh hrvatska", "ustase", "ustasa", "ustaske pjesme",
    "ustaške pjesme", "ustaša", "ustše", "ustashe",
    "ustaška se vojska diže", "independent state of croatia",
    "ustaski", "ustasha", "slavko kvaternik", "eugen dido kvaternik",
    "stanko šarić", "poglavnik pavelić", "poglavnik ante pavelić",
    "kvaternik poglavnik", "ustaški poglavnik",
]
REMOVE_KEYWORDS = ["ustash", "ustasa", "ustase", "poglavni", "ndh", "pavelić", "kvaternik", "(musical"]

# ── AUTH ──────────────────────────────────────────────────────────────────────

def get_youtube_client():
    creds = None
    if TOKEN_PATH.exists():
        with open(TOKEN_PATH) as f:
            token_data = json.load(f)
        creds = Credentials(
            token=token_data.get("token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=token_data.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
            client_secret=token_data.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
            scopes=SCOPES,
        )
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            json.dump({
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
            }, f, indent=2)
    return build("youtube", "v3", credentials=creds)

# ── TAG LOGIC ─────────────────────────────────────────────────────────────────

def should_remove_global(tag):
    t = tag.lower().strip()
    if t in [r.lower() for r in GLOBAL_REMOVE]:
        return True, "global_blacklist"
    if t in [r.lower() for r in REMOVE_TAGS_EXPLICIT]:
        return True, "explicit_remove"
    if any(kw in t for kw in REMOVE_KEYWORDS):
        return True, "keyword_match"
    return False, None

def should_remove_thompson(tag, is_thompson_video):
    if is_thompson_video:
        return False, None
    t = tag.lower().strip()
    if t in [r.lower() for r in THOMPSON_REMOVE]:
        return True, "thompson_brand_collision"
    return False, None

THOMPSON_TITLE_KEYWORDS = [
    "thompson", "čavoglave", "cavoglave",
    "ako ne znaš", "ako ne znas",
    "kralj tomislav", "ne varaj me",
    "ne boj se rogova", "bijeli križ", "bijeli kriz",
    "geni kameni",
]

def is_thompson_video(title):
    t = title.lower()
    return any(kw in t for kw in THOMPSON_TITLE_KEYWORDS)

def is_clean_tag(tag):
    """Return True if every character in tag is in unicode category L, N, P, or Z."""
    return all(unicodedata.category(ch)[0] in ('L', 'N', 'P', 'Z') for ch in tag)


def compute_tag_diff(video_id, title, existing_tags):
    removed = []
    kept = []

    thompson_video = is_thompson_video(title)

    for tag in existing_tags:
        # Sanitize — drop tags with emoji or non-printable characters
        if not is_clean_tag(tag):
            removed.append({"tag": tag, "reason": "emoji_or_nonprintable"})
            continue
        removed_global, reason = should_remove_global(tag)
        if removed_global:
            removed.append({"tag": tag, "reason": reason})
            continue
        removed_thompson, reason = should_remove_thompson(tag, thompson_video)
        if removed_thompson:
            removed.append({"tag": tag, "reason": reason})
            continue
        kept.append(tag)

    # Add canonical tags only if there is room (under 25 kept tags after removes)
    added = []
    if len(kept) < 25:
        existing_lower = [t.lower() for t in kept]
        for canonical in CANONICAL_ADD:
            if canonical.lower() not in existing_lower:
                kept.append(canonical)
                added.append(canonical)

    return {
        "video_id": video_id,
        "title": title,
        "is_thompson_video": thompson_video,
        "tags_before": existing_tags,
        "tags_after": kept,
        "removed": removed,
        "added": added,
        "changes": len(removed) + len(added),
    }

# ── FETCH ─────────────────────────────────────────────────────────────────────

def fetch_video_tags(youtube, video_ids):
    """Batch fetch tags for up to 50 videos at a time."""
    results = {}
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        resp = youtube.videos().list(
            part="snippet",
            id=",".join(batch)
        ).execute()
        for item in resp.get("items", []):
            vid = item["id"]
            snippet = item["snippet"]
            results[vid] = {
                "title": snippet.get("title", ""),
                "tags": snippet.get("tags", []),
                "snippet": snippet,
            }
        time.sleep(0.5)
    return results

# ── UPDATE ────────────────────────────────────────────────────────────────────

def update_tags(youtube, video_id, snippet, new_tags):
    snippet["tags"] = new_tags
    youtube.videos().update(
        part="snippet",
        body={"id": video_id, "snippet": snippet}
    ).execute()

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE EXECUTE'}")
    print(f"Loading corpus from {CORPUS_CSV}...")

    # Load video IDs from corpus
    video_ids = []
    with open(CORPUS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vid = row.get("video_id", "").strip()
            if vid:
                video_ids.append(vid)

    print(f"Corpus: {len(video_ids)} videos")

    youtube = get_youtube_client()

    print("Fetching current tags from YouTube API...")
    video_data = fetch_video_tags(youtube, video_ids)
    print(f"Fetched: {len(video_data)} videos")

    log = []
    videos_with_changes = 0

    for video_id in video_ids:
        if video_id not in video_data:
            print(f"  SKIP {video_id} — not found in API response")
            continue

        data = video_data[video_id]
        title = data["title"]
        existing_tags = data["tags"]

        diff = compute_tag_diff(video_id, title, existing_tags)
        log.append(diff)

        if diff["changes"] == 0:
            continue

        videos_with_changes += 1
        print(f"\n[{video_id}] {title[:60]}")
        if diff["removed"]:
            for r in diff["removed"]:
                print(f"  REMOVE [{r['reason']}]: {r['tag']}")
        if diff["added"]:
            for a in diff["added"]:
                print(f"  ADD: {a}")

        if not DRY_RUN:
            try:
                update_tags(youtube, video_id, data["snippet"], diff["tags_after"])
                print(f"  ✓ Updated")
                time.sleep(1)
            except HttpError as e:
                print(f"  ✗ Error: {e}")
                diff["error"] = str(e)

    # Save log
    LOG_PATH.parent.mkdir(exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "mode": "dry_run" if DRY_RUN else "execute",
            "total_videos": len(video_ids),
            "videos_fetched": len(video_data),
            "videos_with_changes": videos_with_changes,
            "results": log,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n{'─'*50}")
    print(f"Videos scanned:       {len(video_data)}")
    print(f"Videos with changes:  {videos_with_changes}")
    print(f"Log saved to:         {LOG_PATH}")
    if DRY_RUN:
        print("\nDRY RUN complete. Run with --execute to apply changes.")

if __name__ == "__main__":
    main()
