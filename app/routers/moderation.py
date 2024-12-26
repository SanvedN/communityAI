# --- START OF FILE app/routers/moderation.py ---

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.services.moderation_service import ModerationService
from app.core.config import settings
from app.schemas.moderation import ModerationRequest, ModerationResponse
import io
from typing import Union


router = APIRouter()

moderation_service = ModerationService()


@router.post("/", response_model=ModerationResponse)
async def moderate_content(
    content: Union[str, UploadFile] = File(...), content_type: str = "text"
):  # Correct type hint
    """
    Moderates text, image, or video content.


    """
    if content_type == "text":
        if isinstance(content, str):
            text_content = content

        else:
            # text_content = content.file.read().decode("utf-8") # Removed
            raise HTTPException(
                status_code=400, detail="Invalid content format for text."
            )  # Added exception

        analysis = moderation_service.analyze_text(text_content)
        return ModerationResponse(**analysis)

    elif content_type in ["image", "audio", "video"]:
        if not isinstance(content, UploadFile):
            raise HTTPException(
                status_code=400,
                detail="Invalid content format for image/audio/video. UploadFile expected.",
            )

        content_data = content.file.read()

        if content_type == "image":
            file_ext = content.filename.split(".")[-1].lower()
            if file_ext not in settings.ALLOWED_IMAGE_FORMATS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported image format. Allowed formats are {settings.ALLOWED_IMAGE_FORMATS}",
                )

            analysis = moderation_service.analyze_image(content_data)

        elif content_type == "audio":
            analysis = moderation_service.analyze_audio(content_data)

        else:  # video
            analysis = moderation_service.analyze_video(content_data)

        return ModerationResponse(**analysis)

    else:
        raise HTTPException(status_code=400, detail="Unsupported content type.")


# --- END OF FILE app/routers/moderation.py ---
