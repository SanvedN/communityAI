# --- START OF FILE app/core/config.py ---
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "Community AI"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")  # MUST CHANGE
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")  # Set this env variable
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

    # Audio settings
    ALLOWED_AUDIO_FORMATS: list = ["wav", "mp3", "m4a"]
    MAX_AUDIO_SIZE_MB: int = 100

    # Content moderation settings
    MAX_CONTENT_SIZE_MB: int = 50
    ALLOWED_IMAGE_FORMATS: list = ["jpg", "jpeg", "png"]
    ALLOWED_VIDEO_FORMATS: list = ["mp4", "mov"]
    MODERATION_THRESHOLD: float = 0.7


settings = Settings()
# --- END OF FILE app/core/config.py ---
