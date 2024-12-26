from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Dict


class MeetingBase(BaseModel):
    title: str


class MeetingCreate(MeetingBase):
    pass


class MeetingSummary(MeetingBase):
    id: int
    date: datetime
    summary: str
    duration: int
    participants: List[str]
    action_items: List[str]

    class Config:
        from_attributes = True


class Meeting(MeetingBase):
    id: int
    date: datetime
    owner_id: int
    transcript: str
    summary: str
    duration: int
    participants: Dict[str, List[str]]  # speaker_id: [utterances]
    action_items: List[Dict[str, str]]  # [{action: "", assignee: "", due: ""}]

    class Config:
        from_attributes = True
