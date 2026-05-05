#!/usr/bin/env python3
"""
spotify_auth.py — Spotify OAuth2 PKCE Authorization Code Flow
iZLET_sustav | Layer: auth

No client secret required. Uses PKCE (RFC 7636) for secure token exchange.

Usage:
    python scripts/spotify_auth.py
"""

import base64
import hashlib
import json
import secrets
import urllib.parse
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

import requests

# ── Config ─────────────────────────────────────────────────────────────────

CLIENT_ID    = "a638c04d2b6043b1a4c3adda6db5bad9"
REDIRECT_URI = "https://bracakumerle.com/callback"
SCOPE        = ""  # public endpoints only — no user scope required
TOKEN_URL    = "https://accounts.spotify.com/api/token"
AUTH_URL     = "https://accounts.spotify.com/authorize"
TOKEN_PATH   = Path(__file__).parent.parent / "registries" / ".spotify_token.json"


# ── PKCE helpers ────────────────────────────────────────────────────────────

def _generate_pkce() -> tuple[str, str]:
    """Return (code_verifier, code_challenge)."""
    code_verifier = secrets.token_urlsafe(64)[:96]
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return code_verifier, code_challenge


# ── Token exchange ──────────────────────────────────────────────────────────

def _exchange_code(code: str, code_verifier: str) -> dict:
    r = requests.post(
        TOKEN_URL,
        data={
            "grant_type":    "authorization_code",
            "code":          code,
            "redirect_uri":  REDIRECT_URI,
            "client_id":     CLIENT_ID,
            "code_verifier": code_verifier,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    if not r.ok:
        raise SystemExit(f"❌  Token exchange failed: HTTP {r.status_code} — {r.text}")
    return r.json()


def _save_token(token: dict) -> None:
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        **token,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "client_id":    CLIENT_ID,
        "scope":        SCOPE,
        "flow":         "pkce",
    }
    with open(TOKEN_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    code_verifier, code_challenge = _generate_pkce()
    state = secrets.token_urlsafe(16)

    params: dict = {
        "client_id":             CLIENT_ID,
        "response_type":         "code",
        "redirect_uri":          REDIRECT_URI,
        "state":                 state,
        "code_challenge_method": "S256",
        "code_challenge":        code_challenge,
    }
    if SCOPE:
        params["scope"] = SCOPE
    auth_params = urllib.parse.urlencode(params)
    auth_link = f"{AUTH_URL}?{auth_params}"

    print("\n  Opening browser for Spotify authorization…")
    webbrowser.open(auth_link)
    print(f"\n  If browser did not open, visit:\n  {auth_link}\n")

    print("  After approving, copy the full callback URL from browser and paste here:")
    print("  (URL will start with https://bracakumerle.com/callback?code=…)\n")

    raw = input("  Callback URL: ").strip()
    if not raw:
        raise SystemExit("❌  No URL provided.")

    parsed = urllib.parse.urlparse(raw)
    params = dict(urllib.parse.parse_qsl(parsed.query))

    if "error" in params:
        raise SystemExit(f"❌  Authorization denied: {params['error']}")
    if "code" not in params:
        raise SystemExit(f"❌  No code found in URL: {raw}")
    if params.get("state") != state:
        raise SystemExit("❌  State mismatch — possible CSRF. Aborting.")

    code = params["code"]
    print("\n  Exchanging code for token…")
    token = _exchange_code(code, code_verifier)

    _save_token(token)

    expires_in = token.get("expires_in", 3600)
    print(f"\n  ✅  Token saved → {TOKEN_PATH}")
    print(f"      access_token : {token['access_token'][:24]}…")
    print(f"      token_type   : {token.get('token_type')}")
    print(f"      expires_in   : {expires_in}s ({expires_in // 60} min)")
    print(f"      scope        : {token.get('scope')}")
    print(f"      refresh_token: {'yes' if token.get('refresh_token') else 'no'}\n")


if __name__ == "__main__":
    main()
