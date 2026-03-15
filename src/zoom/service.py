import httpx
from typing import Optional
from src.settings import settings as zoom_settings
from src.zoom.utils import get_zoom_access_token
from src.zoom.schemas import CreateMeetingSchema, UpdateMeetingSchema, AddRegistrantSchema

BASE_URL = zoom_settings.ZOOM_BASE_URL

async def _get_headers() -> dict:
    token = await get_zoom_access_token(
        zoom_settings.ZOOM_ACCOUNT_ID,
        zoom_settings.ZOOM_CLIENT_ID,
        zoom_settings.ZOOM_CLIENT_SECRET,
    )
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ─── MEETINGS ──────────────────────────────────────────────

async def create_meeting(data: CreateMeetingSchema) -> dict:
    headers = await _get_headers()
    user_id = data.host_email or "me"
    payload = data.model_dump(exclude_none=True, exclude={"host_email"})
    if "start_time" in payload and payload["start_time"]:
        payload["start_time"] = payload["start_time"].strftime("%Y-%m-%dT%H:%M:%SZ")

    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/users/{user_id}/meetings", json=payload, headers=headers)
        r.raise_for_status()
        return r.json()


async def list_meetings(user_id: str = "me") -> dict:
    headers = await _get_headers()
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/users/{user_id}/meetings", headers=headers)
        r.raise_for_status()
        return r.json()


async def get_meeting(meeting_id: int) -> dict:
    headers = await _get_headers()
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/meetings/{meeting_id}", headers=headers)
        r.raise_for_status()
        return r.json()


async def update_meeting(meeting_id: int, data: UpdateMeetingSchema) -> dict:
    headers = await _get_headers()
    payload = data.model_dump(exclude_none=True)
    
    if "start_time" in payload and payload["start_time"]:
        payload["start_time"] = payload["start_time"].strftime("%Y-%m-%dT%H:%M:%SZ")
    
    async with httpx.AsyncClient() as client:
        r = await client.patch(f"{BASE_URL}/meetings/{meeting_id}", json=payload, headers=headers)
        r.raise_for_status()
        return {"message": "Meeting updated successfully"}


async def delete_meeting(meeting_id: int) -> dict:
    headers = await _get_headers()
    async with httpx.AsyncClient() as client:
        r = await client.delete(f"{BASE_URL}/meetings/{meeting_id}", headers=headers)
        r.raise_for_status()
        return {"message": "Meeting deleted"}


# ─── REGISTRANTS ───────────────────────────────────────────

async def add_registrant(meeting_id: int, data: AddRegistrantSchema) -> dict:
    headers = await _get_headers()
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/meetings/{meeting_id}/registrants",
            json=data.model_dump(),
            headers=headers,
        )
        r.raise_for_status()
        return r.json()


async def list_registrants(meeting_id: int) -> dict:
    headers = await _get_headers()
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/meetings/{meeting_id}/registrants", headers=headers)
        r.raise_for_status()
        return r.json()


# ─── RECORDINGS ────────────────────────────────────────────

async def get_recordings(meeting_id: int) -> dict:
    headers = await _get_headers()
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/meetings/{meeting_id}/recordings", headers=headers)
        r.raise_for_status()
        return r.json()


# ─── USERS ─────────────────────────────────────────────────

async def list_users() -> dict:
    headers = await _get_headers()
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/users", headers=headers)
        r.raise_for_status()
        return r.json()