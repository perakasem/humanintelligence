from pydantic import BaseModel, Field


class ProfileData(BaseModel):
    """User profile data (static fields)."""
    age: int | None = Field(None, ge=16, le=100)
    gender: int | None = Field(None, ge=0, le=3)
    year_in_school: int | None = Field(None, ge=0, le=4)
    major: int | None = Field(None, ge=0, le=8)
    preferred_payment_method: int | None = Field(None, ge=0, le=3)


class ProfileResponse(BaseModel):
    """Response schema for profile endpoint."""
    age: int | None = None
    gender: int | None = None
    year_in_school: int | None = None
    major: int | None = None
    preferred_payment_method: int | None = None
    has_profile: bool = False
