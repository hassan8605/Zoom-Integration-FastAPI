import time
import base64
import httpx
from typing import Optional

# Simple in-memory token cache
_token_cache: dict = {"access_token": None, "expires_at": 0}

def _get_basic_auth(client_id: str, client_secret: str) -> str:
    credentials = f"{client_id}:{client_secret}"
    return base64.b64encode(credentials.encode()).decode()

async def get_zoom_access_token(account_id: str, client_id: str, client_secret: str) -> str:
    """Fetch and cache Zoom OAuth token."""
    now = time.time()
    if _token_cache["access_token"] and now < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    url = "https://zoom.us/oauth/token"
    headers = {
        "Authorization": f"Basic {_get_basic_auth(client_id, client_secret)}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    params = {
        "grant_type": "account_credentials",
        "account_id": account_id,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = now + data.get("expires_in", 3600) - 60  # buffer
    return _token_cache["access_token"]