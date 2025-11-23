from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

from .dashboard import SummaryOutput, Analytics


class RawAnswer(BaseModel):
    """Single raw answer from the adaptive form."""
    question_id: str
    answer: str


class IntakeRequest(BaseModel):
    """Request schema for intake (onboarding/check-in)."""
    raw_answers: list[RawAnswer]


class SnapshotData(BaseModel):
    """Structured snapshot data matching ML input schema."""
    age: int = Field(..., ge=16, le=100)
    gender: int = Field(..., ge=0, le=3)
    year_in_school: int = Field(..., ge=0, le=4)
    major: int = Field(..., ge=0, le=8)
    monthly_income: int = Field(..., ge=0)
    financial_aid: int = Field(..., ge=0)
    tuition: int = Field(..., ge=0)
    housing: int = Field(..., ge=0)
    food: int = Field(..., ge=0)
    transportation: int = Field(..., ge=0)
    books_supplies: int = Field(..., ge=0)
    entertainment: int = Field(..., ge=0)
    personal_care: int = Field(..., ge=0)
    technology: int = Field(..., ge=0)
    health_wellness: int = Field(..., ge=0)
    miscellaneous: int = Field(..., ge=0)
    preferred_payment_method: int = Field(..., ge=0, le=3)


class IntakeResponse(BaseModel):
    """Response schema for intake endpoint."""
    snapshot_id: UUID
    overspending_prob: float
    financial_stress_prob: float
    summary: SummaryOutput
    analytics: Analytics
    created_at: datetime
