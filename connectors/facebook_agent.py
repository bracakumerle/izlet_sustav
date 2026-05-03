import requests
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

PAGE_ID  = "142089129226973"
DATA_DIR = Path(__file__).parent.parent / "data"
ENV_PATH = Path(__file__).parent.parent / ".env"

GRAPH_BASE = "https://graph.facebook.com/v19.0"

PAGE_FIELDS = (
    "name,fan_count,followers_count,about,website,"
    "category,verification_status,picture.type(large)"
)
# Minimal fields — works with basic page token; no engagement metrics needed
POST_FIELDS = "id,message,story,created_time"


def _load_token() -> str:
    token = os.environ.get("FACEBOOK_PAGE_TOKEN", "")
    if not token and ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if line.startswith("FACEBOOK_PAGE_TOKEN="):
                token = line.split("=", 1)[1].strip()
                break
    if not token:
        raise ValueError("FACEBOOK_PAGE_TOKEN is not set in .env or environment")
    return token


def _get(url: str, params: dict) -> dict:
    r = requests.get(url, params=params, timeout=15)
    if not r.ok:
        try:
            err = r.json()
        except Exception:
            err = r.text
        raise requests.HTTPError(
            f"HTTP {r.status_code}: {err}", response=r
        )
    return r.json()


def _exchange_page_token(user_token: str, page_id: str) -> str:
    """Exchange a user token for the Page Access Token of the given page.

    Pages managed via Business Suite don't appear in /me/accounts, so we fetch
    the access_token field directly from the page endpoint instead.
    """
    r = requests.get(
        f"{GRAPH_BASE}/{page_id}",
        params={"fields": "access_token", "access_token": user_token},
        timeout=15,
    )
    if r.ok:
        page_token = r.json().get("access_token")
        if page_token and page_token != user_token:
            return page_token
    return user_token


class FacebookAgent:
    def __init__(self):
        raw   = _load_token()
        self.token = _exchange_page_token(raw, PAGE_ID)
        if self.token != raw:
            print(f"[Facebook] Exchanged user token for Page Access Token")

    def fetch_page_info(self) -> dict:
        data = _get(
            f"{GRAPH_BASE}/{PAGE_ID}",
            {"fields": PAGE_FIELDS, "access_token": self.token},
        )
        return {
            "id":                  data.get("id"),
            "name":                data.get("name"),
            "fan_count":           data.get("fan_count", 0),
            "followers_count":     data.get("followers_count", 0),
            "about":               data.get("about"),
            "website":             data.get("website"),
            "category":            data.get("category"),
            "verified":            data.get("verification_status") == "blue_verified",
            "picture_url":         data.get("picture", {}).get("data", {}).get("url"),
        }

    def fetch_posts(self, limit: int = 100) -> list[dict]:
        posts = []
        # Try /posts first, fall back to /feed
        for endpoint in (f"{GRAPH_BASE}/{PAGE_ID}/posts", f"{GRAPH_BASE}/{PAGE_ID}/feed"):
            url    = endpoint
            params = {
                "fields":       POST_FIELDS,
                "limit":        min(limit, 100),
                "access_token": self.token,
            }
            try:
                while url and len(posts) < limit:
                    data = _get(url, params)
                    for p in data.get("data", []):
                        posts.append({
                            "id":           p.get("id"),
                            "message":      p.get("message") or p.get("story"),
                            "created_time": p.get("created_time"),
                        })
                    next_page = data.get("paging", {}).get("next")
                    url    = next_page if next_page else None
                    params = {}
                    time.sleep(0.3)
                break  # success — stop trying endpoints
            except requests.HTTPError as e:
                print(f"[Facebook] {endpoint.split('/')[-1]} endpoint failed: {e}")
                posts = []
                continue

        return posts

    def snapshot(self) -> dict:
        print(f"[Facebook] Fetching page info for page {PAGE_ID}…")
        page = self.fetch_page_info()
        print(f"[Facebook] Page: {page['name']} | fans={page['fan_count']} | followers={page['followers_count']}")

        print("[Facebook] Fetching posts…")
        posts = self.fetch_posts(limit=200)
        print(f"[Facebook] Fetched {len(posts)} posts")

        fetched_at = datetime.now(timezone.utc).isoformat()

        archive = {
            "fetched_at":   fetched_at,
            "page":         page,
            "total_posts":  len(posts),
            "posts":        posts,
        }

        snapshot_summary = {
            "fetched_at":      fetched_at,
            "page_id":         page["id"],
            "page_name":       page["name"],
            "fan_count":       page["fan_count"],
            "followers_count": page["followers_count"],
            "total_posts":     len(posts),
            "latest_post":     posts[0]["created_time"] if posts else None,
        }

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "facebook_posts.json").write_text(
            json.dumps(archive, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (DATA_DIR / "facebook_snapshot.json").write_text(
            json.dumps(snapshot_summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        print(f"[Facebook] Saved facebook_posts.json ({len(posts)} posts) + facebook_snapshot.json")
        return snapshot_summary


if __name__ == "__main__":
    try:
        result = FacebookAgent().snapshot()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except ValueError as e:
        print(f"[Facebook] ERROR: {e}", file=sys.stderr)
        sys.exit(1)
