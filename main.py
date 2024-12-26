from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import meeting, moderation, auth
from app.core.config import settings
from app.db.session import engine
from app.db import models

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(meeting.router, prefix="/api/meeting", tags=["meeting"])
app.include_router(moderation.router, prefix="/api/moderation", tags=["moderation"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
