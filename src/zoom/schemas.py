from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import IntEnum

class MeetingType(IntEnum):
    INSTANT = 1
    SCHEDULED = 2
    RECURRING_NO_FIXED = 3
    RECURRING_FIXED = 8

class RecurrenceSchema(BaseModel):
    type: int  # 1=Daily, 2=Weekly, 3=Monthly
    repeat_interval: int = 1
    end_times: Optional[int] = None
    end_date_time: Optional[datetime] = None

class CreateMeetingSchema(BaseModel):
    topic: str
    type: MeetingType = MeetingType.SCHEDULED
    start_time: Optional[datetime] = None   # ISO 8601
    duration: Optional[int] = 60            # minutes
    timezone: str = "UTC"
    agenda: Optional[str] = None
    password: Optional[str] = None
    host_email: Optional[str] = None        # defaults to account owner
    recurrence: Optional[RecurrenceSchema] = None

class UpdateMeetingSchema(BaseModel):
    topic: Optional[str] = None
    start_time: Optional[datetime] = None
    duration: Optional[int] = None
    agenda: Optional[str] = None
    password: Optional[str] = None

class AddRegistrantSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str = ""

class MeetingResponseSchema(BaseModel):
    id: int
    topic: str
    start_time: Optional[datetime]
    duration: Optional[int]
    join_url: str
    start_url: str
    password: Optional[str]
    status: Optional[str]