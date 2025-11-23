from pydantic import BaseModel, ConfigDict
from uuid import UUID


class GoogleAuthRequest(BaseModel):
    """Request schema for Google OAuth callback."""
    credential: str  # Google ID token


class UserResponse(BaseModel):
    """Response schema for user data."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str  # Using str instead of EmailStr to avoid email-validator dependency
    name: str | None = None
    picture: str | None = None


class AuthResponse(BaseModel):
    """Response schema for authentication."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    is_new_user: bool
