from fastapi import APIRouter, HTTPException, status
from src.zoom.schemas import CreateMeetingSchema, UpdateMeetingSchema, AddRegistrantSchema
from src.zoom import service
import httpx
from src.response import BuildJSONResponses

router = APIRouter(prefix="/zoom", tags=["Zoom"])



# ─── MEETINGS ──────────────────────────────────────────────

@router.post("/meetings", status_code=status.HTTP_201_CREATED)
async def create_meeting(data: CreateMeetingSchema):
    try:
        response= await service.create_meeting(data)
        return BuildJSONResponses.success_response(data=response, message="Meeting created successfully")
    except httpx.HTTPStatusError as e:
        return BuildJSONResponses.raise_exception(message=e.response.text)



@router.patch("/meetings/{meeting_id}")
async def update_meeting(meeting_id: int, data: UpdateMeetingSchema):
    try:
        response = await service.update_meeting(meeting_id, data)
        return BuildJSONResponses.success_response(data=response, message="Meeting updated successfully")
    except httpx.HTTPStatusError as e:
        return BuildJSONResponses.raise_exception(message=e.response.text)


@router.delete("/meetings/{meeting_id}", status_code=status.HTTP_200_OK)
async def delete_meeting(meeting_id: int):
    try:
        response = await service.delete_meeting(meeting_id)
        return BuildJSONResponses.success_response(data=response, message="Meeting deleted")
    except httpx.HTTPStatusError as e:
        return BuildJSONResponses.raise_exception(message=e.response.text)


# ─── REGISTRANTS ───────────────────────────────────────────

@router.post("/meetings/{meeting_id}/registrants")
async def add_registrant(meeting_id: int, data: AddRegistrantSchema):
    try:
        response = await service.add_registrant(meeting_id, data)
        return BuildJSONResponses.success_response(data=response, message="Registrant added successfully")
    except httpx.HTTPStatusError as e:
        return BuildJSONResponses.raise_exception(message=e.response.text)


@router.get("/meetings/{meeting_id}/registrants")
async def list_registrants(meeting_id: int):
    try:
        response = await service.list_registrants(meeting_id)
        return BuildJSONResponses.success_response(data=response, message="Registrants listed successfully")
    except httpx.HTTPStatusError as e:
        return BuildJSONResponses.raise_exception(message=e.response.text)


# ─── RECORDINGS ────────────────────────────────────────────

@router.get("/meetings/{meeting_id}/recordings")
async def get_recordings(meeting_id: int):
    try:
        response = await service.get_recordings(meeting_id)
        return BuildJSONResponses.success_response(data=response, message="Recordings listed successfully")
    except httpx.HTTPStatusError as e:
        return BuildJSONResponses.raise_exception(message=e.response.text)


# ─── USERS ─────────────────────────────────────────────────

@router.get("/users")
async def list_users():
    try:
        response = await service.list_users()
        return BuildJSONResponses.success_response(data=response, message="Users listed successfully")
    except httpx.HTTPStatusError as e:
        return BuildJSONResponses.raise_exception(message=e.response.text)


# ─── WEBHOOK ───────────────────────────────────────────────

@router.post("/webhook")
async def zoom_webhook(payload: dict):
    """
    Handle Zoom event webhooks.
    Validate using Zoom's secret token header in production.
    Also do this implementation in background using Celery/RabbitMQ/etc.
    """
    try:
        event = payload.get("event")
        
        if event == "meeting.started":
            meeting_id = payload["payload"]["object"]["id"]
            # TODO: trigger your logic (notify via SendGrid, update DB, etc.)

        elif event == "meeting.ended":
            meeting_id = payload["payload"]["object"]["id"]
            # TODO: send follow-up emails, save recordings, etc.

        elif event == "meeting.participant_joined":
            participant = payload["payload"]["object"]["participant"]
            # TODO: log attendance

        elif event == "meeting.participant_left":
            pass

        elif event == "recording.completed":
            recording_files = payload["payload"]["object"]["recording_files"]
            # TODO: save recording URLs to DB

        response = {"status": "success", "message": "Event handled successfully"}
        return BuildJSONResponses.success_response(data=response, message="Event handled successfully")
    except httpx.HTTPStatusError as e:
        return BuildJSONResponses.raise_exception(message=e.response.text)