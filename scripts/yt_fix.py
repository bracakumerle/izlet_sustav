#!/usr/bin/env python3
# yt_fix.py — fix legacy Facebook handle in ALL channel video descriptions via YouTube Data API v3.
# iZLETofci / iZLET1985 -> bracakumerle. Uses existing OAuth token (youtube.force-ssl).
# Dry-run by default; --apply to write. No browser, no external deps.
import json, sys, urllib.request, urllib.parse, io
from pathlib import Path

APPLY = "--apply" in sys.argv
# find registries/.youtube_token.json relative to this file, its parent, or cwd
_here = Path(__file__).resolve().parent
TOKEN = next((c for c in [_here/"registries/.youtube_token.json",
                          _here.parent/"registries/.youtube_token.json",
                          Path("registries/.youtube_token.json")] if c.exists()),
             _here/"registries/.youtube_token.json")
CHANNEL = "UC8jNEBUrOqCcXqVleV9ccKg"
REPL = [("iZLETofci", "bracakumerle"), ("iZLET1985", "bracakumerle")]

def http(method, url, token=None, data=None):
    hdr = {"Content-Type": "application/json"}
    if token: hdr["Authorization"] = "Bearer " + token
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=hdr, method=method)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

# 1. refresh access token
t = json.loads(TOKEN.read_text(encoding="utf-8"))
tok = urllib.request.urlopen(urllib.request.Request(
    "https://oauth2.googleapis.com/token",
    data=urllib.parse.urlencode({
        "client_id": t["client_id"], "client_secret": t["client_secret"],
        "refresh_token": t["refresh_token"], "grant_type": "refresh_token"}).encode(),
    headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST"))
AT = json.loads(tok.read().decode())["access_token"]
print("auth: OK")

# 2. uploads playlist
ch = http("GET", f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={CHANNEL}", AT)
uploads = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

# 3. all video ids
ids, page = [], ""
while True:
    u = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&playlistId={uploads}"
    if page: u += "&pageToken=" + page
    r = http("GET", u, AT)
    ids += [it["contentDetails"]["videoId"] for it in r["items"]]
    page = r.get("nextPageToken", "")
    if not page: break
print(f"videos: {len(ids)}")

# 4. snippets in batches of 50; find drift
targets = []
for i in range(0, len(ids), 50):
    batch = ids[i:i+50]
    r = http("GET", "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=" + ",".join(batch), AT)
    for v in r["items"]:
        d = v["snippet"].get("description", "")
        if any(a in d for a in ("iZLETofci", "iZLET1985")):
            targets.append(v)
print(f"drift targets: {len(targets)}")

updated, verified, exception = [], [], []
for v in targets:
    vid, sn = v["id"], v["snippet"]
    old = sn.get("description", "")
    new = old
    for a, b in REPL: new = new.replace(a, b)
    title = sn.get("title", "")
    if len(new) > 5000:
        exception.append((vid, title, "5000-char limit")); continue
    print(("APPLY " if APPLY else "WOULD-FIX "), vid, "|", title)
    if APPLY:
        body = {"id": vid, "snippet": {
            "title": title, "categoryId": sn.get("categoryId", "10"),
            "description": new, "tags": sn.get("tags", [])}}
        if sn.get("defaultLanguage"): body["snippet"]["defaultLanguage"] = sn["defaultLanguage"]
        if sn.get("defaultAudioLanguage"): body["snippet"]["defaultAudioLanguage"] = sn["defaultAudioLanguage"]
        try:
            http("PUT", "https://www.googleapis.com/youtube/v3/videos?part=snippet", AT, body)
            updated.append(vid)
            chk = http("GET", f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={vid}", AT)
            cd = chk["items"][0]["snippet"].get("description", "")
            if not any(a in cd for a in ("iZLETofci", "iZLET1985")): verified.append(vid)
        except Exception as e:
            exception.append((vid, title, str(