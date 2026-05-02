import requests
import json
import os
import re
import time
from pathlib import Path
from datetime import datetime, timezone

CHANNEL_ID = "UC8jNEBUrOqCcXqVleV9ccKg"
DATA_DIR   = Path(__file__).parent.parent.parent / "data"
ENV_PATH   = Path(__file__).parent.parent.parent / ".env"

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


def _load_api_key() -> str:
    """Read YOUTUBE_API_KEY from .env or environment."""
    key = os.environ.get("YOUTUBE_API_KEY", "")
    if not key and ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if line.startswith("YOUTUBE_API_KEY="):
                key = line.split("=", 1)[1].strip()
                break
    if not key:
        raise ValueError("YOUTUBE_API_KEY is not set in .env or environment")
    return key


def _iso_to_seconds(duration: str) -> int:
    """Convert ISO 8601 duration (PT4M13S) to total seconds."""
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration or "")
    if not m:
        return 0
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + s


class YouTubeAgent:
    def __init__(self):
        self.api_key    = _load_api_key()
        self.channel_id = CHANNEL_ID

    def _get(self, url: str, params: dict) -> dict:
        params = {**params, "key": self.api_key}
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        return r.json()

    def fetch_all_video_ids(self) -> list:
        """Page through search results to collect every video ID + snippet."""
        videos = []
        params = {
            "channelId":  self.channel_id,
            "type":       "video",
            "order":      "date",
            "maxResults": 50,
            "part":       "snippet",
        }

        while True:
            data  = self._get(SEARCH_URL, params)
            items = data.get("items", [])

            for item in items:
                vid_id  = item["id"]["videoId"]
                snippet = item.get("snippet", {})
                videos.append({
                    "video_id":     vid_id,
                    "title":        snippet.get("title"),
                    "published_at": snippet.get("publishedAt"),
                    "description":  snippet.get("description", ""),
                    "thumbnail":    snippet.get("thumbnails", {}).get("medium", {}).get("url"),
                })

            next_token = data.get("nextPageToken")
            if not next_token:
                break

            params["pageToken"] = next_token
            time.sleep(0.5)  # stay within quota

        return videos

    def fetch_video_stats(self, video_ids: list) -> dict:
        """Fetch statistics + contentDetails in batches of 50."""
        stats = {}
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i + 50]
            data  = self._get(VIDEOS_URL, {
                "part": "statistics,contentDetails",
                "id":   ",".join(batch),
            })
            for item in data.get("items", []):
                vid_id   = item["id"]
                s        = item.get("statistics", {})
                cd       = item.get("contentDetails", {})
                duration = cd.get("duration", "")
                stats[vid_id] = {
                    "view_count":    int(s.get("viewCount",    0)),
                    "like_count":    int(s.get("likeCount",    0)),
                    "comment_count": int(s.get("commentCount", 0)),
                    "duration_iso":  duration,
                    "duration_sec":  _iso_to_seconds(duration),
                }
            time.sleep(0.3)
        return stats

    def snapshot(self) -> tuple:
        DATA_DIR.mkdir(exist_ok=True)

        # 1. Collect all video IDs + snippets
        videos  = self.fetch_all_video_ids()
        all_ids = [v["video_id"] for v in videos]

        # 2. Enrich with stats
        stats = self.fetch_video_stats(all_ids)

        # 3. Merge into full archive list
        archive = []
        for v in videos:
            vid_id = v["video_id"]
            s      = stats.get(vid_id, {})
            archive.append({
                "video_id":      vid_id,
                "title":         v["title"],
                "published_at":  v["published_at"],
                "description":   v["description"],
                "thumbnail":     v["thumbnail"],
                "url":           f"https://www.youtube.com/watch?v={vid_id}",
                "view_count":    s.get("view_count",    0),
                "like_count":    s.get("like_count",    0),
                "comment_count": s.get("comment_count", 0),
                "duration_iso":  s.get("duration_iso",  ""),
                "duration_sec":  s.get("duration_sec",  0),
            })

        now = datetime.now(timezone.utc).isoformat()

        # 4. Full archive
        archive_doc = {
            "fetched_at":   now,
            "channel_id":   self.channel_id,
            "total_videos": len(archive),
            "videos":       archive,
        }
        archive_path = DATA_DIR / "youtube_archive.json"
        with open(archive_path, "w", encoding="utf-8") as f:
            json.dump(archive_doc, f, ensure_ascii=False, indent=2)

        # 5. Summary snapshot
        total_views = sum(v["view_count"] for v in archive)
        total_likes = sum(v["like_count"]  for v in archive)
        dates = sorted(v["published_at"] for v in archive if v["published_at"])

        snapshot_doc = {
            "fetched_at":        now,
            "channel_id":        self.channel_id,
            "total_videos":      len(archive),
            "total_views":       total_views,
            "total_likes":       total_likes,
            "latest_video_date": dates[-1] if dates else None,
            "oldest_video_date": dates[0]  if dates else None,
            "top_5_by_views": sorted(
                [{"title": v["title"], "view_count": v["view_count"], "url": v["url"]}
                 for v in archive],
                key=lambda x: x["view_count"], reverse=True
            )[:5],
        }
        snapshot_path = DATA_DIR / "youtube_snapshot.json"
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(snapshot_doc, f, ensure_ascii=False, indent=2)

        return archive_doc, snapshot_doc, archive_path, snapshot_path

    def check_video(self, video_id: str) -> bool:
        """Legacy: check if a single video is accessible."""
        if not video_id:
            return False
        try:
            r = requests.get(
                f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}",
                timeout=5,
            )
            return r.status_code == 200
        except Exception:
            return False


if __name__ == "__main__":
    agent = YouTubeAgent()
    archive, snapshot, arch_path, snap_path = agent.snapshot()
    print(f"✅ YouTube archive saved  → {arch_path}")
    print(f"✅ YouTube snapshot saved → {snap_path}")
    print(f"   Total videos : {snapshot['total_videos']}")
    print(f"   Total views  : {snapshot['total_views']:,}")
    print(f"   Latest video : {snapshot['latest_video_date']}")
    print(f"   Oldest video : {snapshot['oldest_video_date']}")
