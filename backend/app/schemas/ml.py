from pydantic import BaseModel, Field


class MLInput(BaseModel):
    """Input schema for ML model prediction."""
    age: int
    gender: int
    year_in_school: int
    major: int
    monthly_income: int
    financial_aid: int
    tuition: int
    housing: int
    food: int
    transportation: int
    books_supplies: int
    entertainment: int
    personal_care: int
    technology: int
    health_wellness: int
    miscellaneous: int
    preferred_payment_method: int


class MLOutput(BaseModel):
    """Output schema from ML model prediction."""
    overspending_prob: float = Field(..., ge=0.0, le=1.0)
    financial_stress_prob: float = Field(..., ge=0.0, le=1.0)
