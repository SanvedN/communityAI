# --- START OF FILE app/schemas/auth.py ---

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=6)


# --- END OF FILE app/schemas/auth.py ---
