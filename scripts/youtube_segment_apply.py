"""
youtube_segment_apply.py — Executor za ratificirani segment diff.

Čita registries/youtube_segment_diff_<datum>.json i primjenjuje promjene
(tagovi + naslovi) kroz YouTube Data API v3, istom OAuth infrastrukturom
kao youtube_tag_audit_bulk.py (registries/.youtube_token.json).

Modes:
  python scripts/youtube_segment_apply.py                → dry-run (ispis plana, nema writeova)
  python scripts/youtube_segment_apply.py --execute      → live write na YouTube

Sigurnosna pravila:
  - title_change s confidence != "confirmed" se NIKAD ne primjenjuje (skip + warning)
  - svaki write se logira u registries/youtube_segment_apply_log_<datum>.json
  - quota: videos.update = 50 jedinica; ~43 videa = ~2150 jedinica (dnevni limit 10k)
"""

import os
import sys
import json
import time
import datetime
from pathlib import Path

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
TOKEN_PATH = ROOT / "registries" / ".youtube_token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
EXECUTE = "--execute" in sys.argv
TODAY = datetime.date.today().isoformat()


def latest_diff() -> Path:
    diffs = sorted((ROOT / "registries").glob("youtube_segment_diff_*.json"))
    if not diffs:
        sys.exit("Nema diff datoteke — prvo pokreni youtube_segment_audit.py")
    return diffs[-1]


def _full_oauth_flow():
    cs = ROOT / "client_secrets.json"
    if not cs.exists():
        sys.exit("Token nevaljan i nema client_secrets.json u rootu repoa — "
                 "preuzmi ga iz Google Cloud Console (Credentials -> OAuth client -> Download JSON).")
    flow = InstalledAppFlow.from_client_secrets_file(str(cs), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_PATH.write_text(json.dumps({
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
    }, indent=2), encoding="utf-8")
    print(f"Novi token spremljen: {TOKEN_PATH}")
    return creds


def get_client():
    creds = None
    if TOKEN_PATH.exists():
        td = json.loads(TOKEN_PATH.read_text())
        creds = Credentials(
            token=td.get("token"),
            refresh_token=td.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=td.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
            client_secret=td.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
            scopes=SCOPES,
        )
        try:
            creds.refresh(Request())
        except RefreshError:
            print("Refresh token opozvan/istekao — pokrećem puni OAuth flow (browser)...")
            creds = _full_oauth_flow()
    else:
        creds = _full_oauth_flow()
    return build("youtube", "v3", credentials=creds)


def main():
    diff_path = latest_diff()
    diff = json.loads(diff_path.read_text(encoding="utf-8"))
    plan = diff["diffs"]
    print(f"Diff: {diff_path.name} | videa s promjenama: {len(plan)} | mode: {'EXECUTE' if EXECUTE else 'DRY-RUN'}")

    yt = get_client() if EXECUTE else None
    log = {"date": TODAY, "mode": "execute" if EXECUTE else "dry_run",
           "diff_source": diff_path.name, "results": []}

    for item in plan:
        vid = item["video_id"]
        remove = {t["tag"].lower() for t in item.get("tags_remove", [])}
        add = item.get("tags_add", [])
        tc = item.get("title_change")
        apply_title = bool(tc and tc.get("confidence") == "confirmed")
        if tc and not apply_title:
            print(f"  SKIP TITLE (nije confirmed): {vid} — {tc.get('proposed')}")

        entry = {"video_id": vid, "title": item["title"], "applied": False,
                 "tags_removed": sorted(remove), "tags_added": add,
                 "title_applied": None, "error": None}

        if not EXECUTE:
            new_t = f' | NASLOV → "{tc["proposed"]}"' if apply_title else ""
            print(f"  PLAN {vid}: -{len(remove)} tagova, +{len(add)}{new_t}")
            log["results"].append(entry)
            continue

        try:
            resp = yt.videos().list(part="snippet", id=vid).execute()
            if not resp.get("items"):
                entry["error"] = "video_not_found_or_private"
                log["results"].append(entry)
                continue
            sn = resp["items"][0]["snippet"]
            current = sn.get("tags", []) or []
            kept = [t for t in current if t.lower() not in remove]
            kept_lower = {t.lower() for t in kept}
            new_tags = kept + [t for t in add if t.lower() not in kept_lower]
            # YouTube limit: 500 znakova ukupno
            while sum(len(t) + 2 for t in new_tags) > 480 and new_tags:
                new_tags.pop()
            body = {"id": vid, "snippet": {
                "title": tc["proposed"] if apply_title else sn["title"],
                "description": sn.get("description", ""),
                "tags": new_tags,
                "categoryId": sn.get("categoryId", "10"),
            }}
            if sn.get("defaultLanguage"):
                body["snippet"]["defaultLanguage"] = sn["defaultLanguage"]
            yt.videos().update(part="snippet", body=body).execute()
            entry["applied"] = True
            entry["title_applied"] = tc["proposed"] if apply_title else None
            print(f"  OK {vid}: -{len(remove)}/+{len(add)} tagova"
                  + (f' | naslov → "{tc["proposed"]}"' if apply_title else ""))
            time.sleep(0.5)
        except HttpError as e:
            entry["error"] = str(e)
            print(f"  ERROR {vid}: {e}")
        log["results"].append(entry)

    log_path = ROOT / "registries" / f"youtube_segment_apply_log_{TODAY}.json"
    log_path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(1 for r in log["results"] if r["applied"])
    print(f"\nGotovo. Primijenjeno: {ok}/{len(plan)} | log: {log_path}")


if __name__ == "__main__":
    main()
