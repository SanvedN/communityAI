# --- START OF FILE app/db/models.py ---

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    LargeBinary,
    Float,
    JSON,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    meetings = relationship("Meeting", back_populates="owner")
    moderated_contents = relationship("ContentModeration", back_populates="user")


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    transcript = Column(JSON)  # changed to json
    summary = Column(String)
    # audio_file = Column(LargeBinary) #Removed this to store as individual files
    duration = Column(Integer)  # in seconds
    participants = Column(JSON)  # Store speaker information
    action_items = Column(JSON)  # Store extracted action items

    owner = relationship("User", back_populates="meetings")


class ContentModeration(Base):
    __tablename__ = "content_moderation"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_type = Column(String)  # text, image, audio, video
    content_hash = Column(String, index=True)
    content_path = Column(String)  # Store file path instead of binary
    is_inappropriate = Column(Boolean)
    is_ai_generated = Column(Boolean)
    sentiment_score = Column(Float)
    toxicity_score = Column(Float)
    moderation_details = Column(JSON)  # Store detailed analysis
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="moderated_contents")


# --- END OF FILE app/db/models.py ---
