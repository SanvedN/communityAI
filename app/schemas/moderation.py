# --- START OF FILE app/schemas/meeting.py ---
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional, Union


class MeetingCreate(BaseModel):
    title: str


class SpeakerSegment(BaseModel):
    speaker: str
    start_time: float
    end_time: float


class Meeting(BaseModel):
    id: int
    title: str
    date: datetime
    owner_id: int
    transcript: Optional[List[Dict]]
    summary: Optional[str]
    # audio_file: bytes #Removed: Handling separately.
    duration: Optional[int]
    participants: Optional[List[SpeakerSegment]]
    action_items: Optional[List[Dict]]

    class Config:
        orm_mode = True


class MeetingSummary(BaseModel):
    id: int
    title: str
    date: datetime

    class Config:
        orm_mode = True


# --- END OF FILE app/schemas/meeting.py ---


# --- START OF FILE app/schemas/moderation.py ---
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union


class Sentiment(BaseModel):
    neg: float
    neu: float
    pos: float
    compound: float


class ToxicityScore(BaseModel):
    label: str
    score: float


class NSFWDetail(BaseModel):
    label: str
    score: float
    box: List[int]


class ModerationResponse(BaseModel):
    sentiment: Optional[Sentiment] = None
    toxicity: Optional[List[ToxicityScore]] = None
    is_ai_generated: Optional[bool] = None
    is_inappropriate: Optional[bool] = None
    manipulation_score: Optional[float] = None
    nsfw_details: Optional[List[NSFWDetail]] = None
    audio_features: Optional[Dict[str, Any]] = None
    inappropriate_frame_ratio: Optional[float] = None
    ai_generated_frame_ratio: Optional[float] = None


class ModerationRequest(BaseModel):
    content: Union[str, bytes]
    content_type: str = Field(..., example="text")


# --- END OF FILE app/schemas/moderation.py ---
