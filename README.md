# 🎥 Zoom Integration — FastAPI

A production-ready Zoom integration built with FastAPI using **Server-to-Server OAuth**. Supports meeting management, registrants, cloud recordings, user listing, and real-time webhook event handling.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Zoom Account Setup](#zoom-account-setup)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
  - [Create Meeting](#1-post-apizoomeetings)
  - [Update Meeting](#2-patch-apizoomeetingsmeeting_id)
  - [Delete Meeting](#3-delete-apizoomeetingsmeeting_id)
  - [Add Registrant](#4-post-apizoomeetingsmeeting_idregistrants)
  - [List Registrants](#5-get-apizoomeetingsmeeting_idregistrants)
  - [Get Recordings](#6-get-apizoomeetingsmeeting_idrecordings)
  - [List Users](#7-get-apizoomusers)
  - [Webhook](#8-post-apizoomwebhook)
- [Webhook Events](#webhook-events)
- [Authentication Flow](#authentication-flow)
- [Common Errors](#common-errors)

---

## Prerequisites

- Python 3.10+
- A [Zoom Account](https://zoom.us) (Free or Pro)
- FastAPI application running

---

## Zoom Account Setup

### Step 1 — Create a Server-to-Server OAuth App

1. Go to [marketplace.zoom.us](https://marketplace.zoom.us) and sign in
2. Click **Develop** → **Build App**
3. Choose **Server-to-Server OAuth** → Click **Create**
4. Enter an app name (e.g. `zoom-backend-integration`) → **Create**
5. From the **App Credentials** tab, copy:
   - `Account ID`
   - `Client ID`
   - `Client Secret`

### Step 2 — Add Required Scopes

In your app, go to the **Scopes** tab and add:

| Scope | Purpose |
|-------|---------|
| `meeting:write:admin` | Create, update, delete meetings |
| `meeting:read:admin` | Read and list meetings |
| `user:read:admin` | List users in your account |
| `recording:read:admin` | Access cloud recordings |
| `webinar:write:admin` | *(Optional)* Create webinars |

### Step 3 — Activate the App

> ⚠️ Click **Activate App** at the top of the page. Without activation all API calls return `401 Unauthorized`.

### Step 4 — Host Email Note

> ⚠️ The `host_email` field must belong to a user **already inside your Zoom account**.  
> To add a user: [zoom.us/account/user](https://zoom.us/account/user) → **Add Users** → invite the email.  
> To avoid this entirely, simply **omit `host_email`** and the account owner is used by default.

---

## Installation
Install:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Add to your `.env` file:

```env
ZOOM_ACCOUNT_ID=your_account_id_here
ZOOM_CLIENT_ID=your_client_id_here
ZOOM_CLIENT_SECRET=your_client_secret_here
ZOOM_BASE_URL=https://api.zoom.us/v2
```

---

## Project Structure

```
src/
  zoom/
    __init__.py
    models.py        # SQLAlchemy DB models (optional)
    schemas.py       # Pydantic request/response schemas
    service.py       # Business logic + Zoom API calls
    router.py        # FastAPI route definitions
    settings.py      # Zoom credentials loaded from .env
    utils.py         # Token cache + helper functions
```

---

## API Endpoints

### 1. `POST /api/zoom/meetings`

Create a new Zoom meeting.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `topic` | string | ✅ | Meeting title shown to participants |
| `type` | integer | ✅ | `1`=Instant, `2`=Scheduled, `3`=Recurring no end, `8`=Recurring fixed end |
| `start_time` | datetime | ❌ | ISO 8601 format e.g. `2026-03-20T10:00:00Z`. Only for type `2` and `8` |
| `duration` | integer | ❌ | Duration in minutes. Default: `60` |
| `timezone` | string | ❌ | IANA timezone e.g. `Asia/Karachi`, `UTC`. Default: `UTC` |
| `agenda` | string | ❌ | Meeting description shown in the invitation |
| `password` | string | ❌ | Join password, max 10 characters |
| `host_email` | string | ❌ | Must be an existing user in your Zoom account |
| `recurrence` | object | ❌ | Only for type `3` or `8`. See recurrence fields below |

**Recurrence Object:**

| Field | Type | Description |
|-------|------|-------------|
| `type` | integer | `1`=Daily, `2`=Weekly, `3`=Monthly |
| `repeat_interval` | integer | Repeat every N days/weeks/months |
| `end_times` | integer | Number of occurrences before series ends |
| `end_date_time` | datetime | End date in ISO 8601 (alternative to `end_times`) |

**Example Request:**

```json
{
  "topic": "Team Standup",
  "type": 2,
  "start_time": "2026-03-20T10:00:00Z",
  "duration": 60,
  "timezone": "Asia/Karachi",
  "agenda": "Weekly sync meeting",
  "password": "abc123"
}
```

**Success Response `201`:**

```json
{
  "status": true,
  "message": "Meeting created successfully",
  "data": {
    "id": 81837459991,
    "topic": "Team Standup",
    "start_time": "2026-03-20T10:00:00Z",
    "duration": 60,
    "join_url": "https://us05web.zoom.us/j/81837459991?pwd=xxx",
    "start_url": "https://us05web.zoom.us/s/81837459991?zak=xxx",
    "password": "abc123",
    "status": "waiting"
  }
}
```

> 💡 `join_url` → share with attendees (never expires).  
> `start_url` → host only, expires in ~2 hours. Fetch fresh via `GET /meetings/{id}` when needed.

---

### 2. `PATCH /api/zoom/meetings/{meeting_id}`

Update an existing meeting. All fields are optional — send only what you want to change.

**Path Parameter:** `meeting_id` — integer (e.g. `81837459991`)

**Request Body:**

| Field | Type | Description |
|-------|------|-------------|
| `topic` | string | New meeting title |
| `start_time` | datetime | New start time in ISO 8601 format |
| `duration` | integer | New duration in minutes |
| `agenda` | string | Updated meeting description |
| `password` | string | New password, max 10 characters |

**Example Request:**

```json
{
  "topic": "Updated Meeting Title",
  "start_time": "2026-03-21T11:00:00Z",
  "duration": 45,
  "agenda": "Revised agenda",
  "password": "newpass1"
}
```

**Success Response `200`:**

```json
{
  "status": true,
  "message": "Meeting updated successfully",
  "data": { "message": "Meeting updated successfully" }
}
```

---

### 3. `DELETE /api/zoom/meetings/{meeting_id}`

Delete a meeting permanently.

**Path Parameter:** `meeting_id` — integer

No request body required.

**Success Response `200`:**

```json
{
  "status": true,
  "message": "Meeting deleted",
  "data": { "message": "Meeting deleted" }
}
```

---

### 4. `POST /api/zoom/meetings/{meeting_id}/registrants`

Register an attendee for a meeting.

> ⚠️ Registration must be enabled on the meeting. Each registrant gets their own unique `join_url`.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | ✅ | Valid email address |
| `first_name` | string | ✅ | Registrant first name |
| `last_name` | string | ❌ | Registrant last name (default: empty) |

**Example Request:**

```json
{
  "email": "attendee@example.com",
  "first_name": "Ali",
  "last_name": "Khan"
}
```

**Success Response `200`:**

```json
{
  "status": true,
  "message": "Registrant added successfully",
  "data": {
    "id": "abcd1234",
    "join_url": "https://us05web.zoom.us/w/81837459991?tk=xxx",
    "registrant_id": "abcd1234",
    "topic": "Team Standup"
  }
}
```

---

### 5. `GET /api/zoom/meetings/{meeting_id}/registrants`

List all registered attendees for a meeting.

No request body required.

**Success Response `200`:**

```json
{
  "status": true,
  "message": "Registrants listed successfully",
  "data": {
    "registrants": [
      {
        "id": "abcd1234",
        "email": "attendee@example.com",
        "first_name": "Ali",
        "last_name": "Khan",
        "status": "approved",
        "join_url": "https://us05web.zoom.us/w/81837459991?tk=xxx",
        "create_time": "2026-03-16T08:00:00Z"
      }
    ],
    "total_records": 1
  }
}
```

---

### 6. `GET /api/zoom/meetings/{meeting_id}/recordings`

Get cloud recording files for a meeting.

No request body required. Only available after the meeting has ended and recording processing is complete.

**Recording `file_type` values:**

| file_type | Description |
|-----------|-------------|
| `MP4` | Full video recording |
| `M4A` | Audio-only recording |
| `TRANSCRIPT` | Auto-generated text transcript |
| `CHAT` | In-meeting chat log |
| `CC` | Closed captions file |

**Success Response `200`:**

```json
{
  "status": true,
  "message": "Recordings listed successfully",
  "data": {
    "id": 81837459991,
    "topic": "Team Standup",
    "duration": 60,
    "recording_files": [
      {
        "file_type": "MP4",
        "file_size": 104857600,
        "play_url": "https://zoom.us/rec/play/xxx",
        "download_url": "https://zoom.us/rec/download/xxx",
        "status": "completed",
        "recording_type": "shared_screen_with_speaker_view"
      }
    ]
  }
}
```

---

### 7. `GET /api/zoom/users`

List all users in your Zoom account.

No request body required. Use the returned `email` or `id` as `host_email` when creating meetings to avoid the `1001` error.

**Success Response `200`:**

```json
{
  "status": true,
  "message": "Users listed successfully",
  "data": {
    "users": [
      {
        "id": "fLP_D-goSV-pn6K9Hro2NQ",
        "first_name": "Hassan",
        "last_name": "Mahmood",
        "email": "hm86052002@gmail.com",
        "type": 2,
        "status": "active",
        "timezone": "Asia/Karachi"
      }
    ],
    "total_records": 1
  }
}
```

---

### 8. `POST /api/zoom/webhook`

Receives Zoom event notifications. **You do not call this yourself** — Zoom posts to it automatically.

**Setup in Zoom Marketplace:**

1. In your app → **Feature** → **Event Subscriptions** → **Add Subscription**
2. Set endpoint URL to: `https://yourdomain.com/api/zoom/webhook`
3. Select events: `Meeting Started`, `Meeting Ended`, `Participant Joined`, `Participant Left`, `Recording Completed`
4. Save — Zoom will send a URL validation challenge first

> 💡 For local development use [ngrok](https://ngrok.com): `ngrok http 8000` and use the HTTPS URL as your webhook endpoint.

---

## Webhook Events

### `meeting.started`
```json
{
  "event": "meeting.started",
  "payload": {
    "object": {
      "id": "81837459991",
      "topic": "Team Standup",
      "host_id": "fLP_D-goSV-pn6K9Hro2NQ",
      "start_time": "2026-03-20T10:00:00Z"
    }
  }
}
```

### `meeting.ended`
```json
{
  "event": "meeting.ended",
  "payload": {
    "object": {
      "id": "81837459991",
      "topic": "Team Standup",
      "end_time": "2026-03-20T11:00:00Z",
      "duration": 60
    }
  }
}
```

### `meeting.participant_joined`
```json
{
  "event": "meeting.participant_joined",
  "payload": {
    "object": {
      "id": "81837459991",
      "participant": {
        "user_id": "participant-user-id",
        "user_name": "Ali Khan",
        "email": "ali@example.com",
        "join_time": "2026-03-20T10:02:00Z"
      }
    }
  }
}
```

### `recording.completed`
```json
{
  "event": "recording.completed",
  "payload": {
    "object": {
      "id": "81837459991",
      "topic": "Team Standup",
      "recording_files": [
        {
          "file_type": "MP4",
          "download_url": "https://zoom.us/rec/download/xxx",
          "status": "completed"
        }
      ]
    }
  }
}
```

---

## Authentication Flow

Server-to-Server OAuth requires no user interaction. Tokens are fetched and cached automatically.

```
1. First API call triggers utils.get_zoom_access_token()
2. POST https://zoom.us/oauth/token
   Header: Authorization: Basic base64(client_id:client_secret)
   Params: grant_type=account_credentials&account_id=xxx
3. Token cached in memory with expiry timestamp
4. All subsequent calls reuse the cached token
5. Token auto-refreshes 60 seconds before expiry (every ~1 hour)
```

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `1001` User does not exist | `host_email` not in your Zoom account | Remove `host_email` or add user at [zoom.us/account/user](https://zoom.us/account/user) |
| `124` Invalid access token | Wrong credentials in `.env` | Check `ZOOM_CLIENT_ID`, `CLIENT_SECRET`, `ACCOUNT_ID` |
| `3001` Meeting does not exist | Wrong `meeting_id` | Verify via `GET /api/zoom/users` then list meetings |
| `429` Too many requests | Rate limit hit | Add exponential backoff retry logic |
| `500` datetime not serializable | `model_dump()` returns datetime objects | Use `model_dump(mode="json")` in `service.py` |
| `401` Unauthorized | App not activated or missing scopes | Activate app and verify all scopes are added |

---

## Quick Reference

| Endpoint | Body | Required Fields | Notes |
|----------|------|-----------------|-------|
| `POST /meetings` | Yes | `topic`, `type` | Omit `host_email` to use account owner |
| `PATCH /meetings/{id}` | Yes | None (all optional) | Send only fields to change |
| `DELETE /meetings/{id}` | No | — | Permanent, cannot be undone |
| `POST /{id}/registrants` | Yes | `email`, `first_name` | Registration must be enabled on meeting |
| `GET /{id}/registrants` | No | — | Returns all registered attendees |
| `GET /{id}/recordings` | No | — | Available after meeting ends |
| `GET /users` | No | — | Use returned `email` as `host_email` |
| `POST /webhook` | Auto (Zoom) | — | Zoom posts events automatically |

---

> Built with [FastAPI](https://fastapi.tiangolo.com) · [Zoom API Docs](https://developers.zoom.us/docs/api/)
