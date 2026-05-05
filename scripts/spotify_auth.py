#!/usr/bin/env python3
"""
spotify_auth.py — Spotify OAuth2 Authorization Code Flow
iZLET_sustav | Layer: auth

Otvara browser, čeka callback na localhost:8888, zamjenjuje code za token
i sprema ga u registries/.spotify_token.json.

Usage:
    python scripts/spotify_auth.py
"""

import base64
import hashlib
import http.server
import json
import os
import secrets
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

# ── Config ─────────────────────────────────────────────────────────────────

CLIENT_ID     = "a638c04d2b6043b1a4c3adda6db5bad9"
REDIRECT_URI  = "http://localhost:8888/callback"
SCOPE         = "user-read-private"
PORT          = 8888
TOKEN_URL     = "https://accounts.spotify.com/api/token"
AUTH_URL      = "https://accounts.spotify.com/authorize"
TOKEN_PATH    = Path(__file__).parent.parent / "registries" / ".spotify_token.json"

# ── Load secret ────────────────────────────────────────────────────────────

load_dotenv(Path(__file__).parent.parent / ".env")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
if not CLIENT_SECRET:
    raise SystemExit("❌  SPOTIFY_CLIENT_SECRET not found in .env")

# ── Local callback server ───────────────────────────────────────────────────

_captured_code: str | None = None
_server_error:  str | None = None


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global _captured_code, _server_error
        parsed = urllib.parse.urlparse(self.path)
        params = dict(urllib.parse.parse_qsl(parsed.query))

        if "error" in params:
            _server_error = params["error"]
            body = b"<h2>Authorization denied. You can close this tab.</h2>"
        elif "code" in params:
            _captured_code = params["code"]
            body = b"<h2>Authorization successful. You can close this tab.</h2>"
        else:
            body = b"<h2>Unexpected callback. Check terminal.</h2>"

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # suppress request logs


def _start_server() -> http.server.HTTPServer:
    server = http.server.HTTPServer(("localhost", PORT), _CallbackHandler)
    t = threading.Thread(target=server.handle_request, daemon=True)
    t.start()
    return server


# ── Token exchange ──────────────────────────────────────────────────────────

def _exchange_code(code: str) -> dict:
    credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    r = requests.post(
        TOKEN_URL,
        data={
            "grant_type":   "authorization_code",
            "code":         code,
            "redirect_uri": REDIRECT_URI,
        },
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type":  "application/x-www-form-urlencoded",
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def _save_token(token: dict) -> None:
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        **token,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "client_id":    CLIENT_ID,
        "scope":        SCOPE,
    }
    with open(TOKEN_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    state = secrets.token_urlsafe(16)

    auth_params = urllib.parse.urlencode({
        "client_id":     CLIENT_ID,
        "response_type": "code",
        "redirect_uri":  REDIRECT_URI,
        "scope":         SCOPE,
        "state":         state,
    })
    auth_link = f"{AUTH_URL}?{auth_params}"

    print("  Starting local callback server on port 8888…")
    server = _start_server()

    print(f"  Opening browser for Spotify authorization…")
    webbrowser.open(auth_link)
    print(f"  If browser did not open, visit:\n  {auth_link}\n")

    print("  Waiting for callback", end="", flush=True)
    for _ in range(120):
        if _captured_code or _server_error:
            break
        time.sleep(0.5)
        print(".", end="", flush=True)
    print()

    server.server_close()

    if _server_error:
        raise SystemExit(f"❌  Authorization denied: {_server_error}")
    if not _captured_code:
        raise SystemExit("❌  Timeout — no callback received within 60s")

    print("  Exchanging code for token…")
    token = _exchange_code(_captured_code)

    _save_token(token)

    expires_in = token.get("expires_in", 3600)
    expiry_min = expires_in // 60
    print(f"\n  ✅  Token saved → {TOKEN_PATH}")
    print(f"      access_token : {token['access_token'][:24]}…")
    print(f"      token_type   : {token.get('token_type')}")
    print(f"      expires_in   : {expires_in}s ({expiry_min} min)")
    print(f"      scope        : {token.get('scope')}")
    print(f"      refresh_token: {'yes' if token.get('refresh_token') else 'no'}\n")


if __name__ == "__main__":
    main()
