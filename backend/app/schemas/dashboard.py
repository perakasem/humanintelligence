from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class SnapshotHistory(BaseModel):
    """Historical snapshot data for charts."""
    snapshot_id: UUID
    created_at: datetime
    overspending_prob: float
    financial_stress_prob: float
    total_spending: int
    total_resources: int


class SpendingBreakdown(BaseModel):
    """Spending breakdown by category."""
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


class Analytics(BaseModel):
    """Computed analytics for dashboard."""
    total_resources: int
    total_spending: int
    net_balance: int
    is_overspending: bool
    overspending_amount: int  # Positive when overspending, 0 otherwise
    savings_potential: int  # Positive when under budget, 0 otherwise
    food_share: float
    housing_share: float
    entertainment_share: float
    discretionary_share: float
    tuition_share: float


class SummaryOutput(BaseModel):
    """Cached summary from summarizer agent."""
    summary_paragraph: str
    key_points: list[str]


class DashboardResponse(BaseModel):
    """Response schema for dashboard endpoint."""
    user_id: UUID
    latest_snapshot_id: UUID | None = None
    spending_breakdown: SpendingBreakdown | None = None
    analytics: Analytics | None = None
    risk_scores: dict | None = None
    summary: SummaryOutput | None = None
    history: list[SnapshotHistory] = []
    has_data: bool = False
