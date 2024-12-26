from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, WebSocket
from sqlalchemy.orm import Session
from app.services.meeting_service import MeetingService
from app.services.audio_service import AudioService
from app.db.session import get_db
from app.db import models
from app.schemas.meeting import MeetingCreate, Meeting, MeetingSummary
from typing import List
import asyncio

router = APIRouter()
meeting_service = MeetingService()
audio_service = AudioService()


@router.post("/", response_model=Meeting)
async def create_meeting(
    meeting: MeetingCreate, user_id: int, db: Session = Depends(get_db)
):
    db_meeting = models.Meeting(title=meeting.title, owner_id=user_id)
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting


@router.websocket("/record/{meeting_id}")
async def record_meeting(
    websocket: WebSocket, meeting_id: int, db: Session = Depends(get_db)
):
    await websocket.accept()

    # Get meeting from database
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        await websocket.close(code=4004)
        return

    try:
        # Initialize audio buffers for each participant
        audio_buffers = {}

        while True:
            # Receive audio chunks from participants
            data = await websocket.receive_bytes()
            participant_id = await websocket.receive_text()

            if participant_id not in audio_buffers:
                audio_buffers[participant_id] = []

            audio_buffers[participant_id].append(data)

            # Process audio if buffer is large enough
            if len(audio_buffers[participant_id]) >= 10:  # Process every 10 chunks
                audio_data = b"".join(audio_buffers[participant_id])

                # Transcribe audio
                transcript = audio_service.transcribe_audio(audio_data)

                # Clear buffer
                audio_buffers[participant_id] = []

                # Send transcription back to client
                await websocket.send_json(
                    {"participant": participant_id, "transcript": transcript}
                )

    except Exception as e:
        print(f"Error in WebSocket: {str(e)}")
    finally:
        await websocket.close()


@router.post("/{meeting_id}/finalize")
async def finalize_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Merge all audio streams
    audio_data = audio_service.merge_audio_streams(meeting.audio_file)

    # Perform speaker diarization
    speakers = audio_service.detect_speakers(audio_data)

    # Generate complete transcript
    transcript = audio_service.transcribe_audio(audio_data)

    # Generate meeting summary
    analysis = meeting_service.generate_summary(transcript)

    # Extract action items
    action_items = meeting_service.extract_action_items(transcript)

    # Update meeting record
    meeting.transcript = transcript
    meeting.summary = analysis["summary"]
    meeting.participants = speakers
    meeting.action_items = action_items

    db.commit()
    db.refresh(meeting)

    return meeting


@router.get("/{meeting_id}", response_model=Meeting)
async def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.get("/user/{user_id}", response_model=List[MeetingSummary])
async def get_user_meetings(user_id: int, db: Session = Depends(get_db)):
    meetings = db.query(models.Meeting).filter(models.Meeting.owner_id == user_id).all()
    return meetings
