from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..database import get_db
from ..schemas.dashboard import (
    DashboardResponse,
    SpendingBreakdown,
    Analytics,
    SummaryOutput,
    SnapshotHistory
)
from ..models.user import User
from ..models.snapshot import SpendingSnapshot
from ..services import AnalyticsService
from ..utils.auth import get_current_user

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard data for the current user.

    Returns:
    - Latest snapshot with spending breakdown
    - Computed analytics
    - Risk scores
    - Cached summary
    - Historical data for charts
    """
    # Get user's snapshots ordered by date
    snapshots = (
        db.query(SpendingSnapshot)
        .filter(SpendingSnapshot.user_id == user.id)
        .order_by(desc(SpendingSnapshot.created_at))
        .limit(10)
        .all()
    )

    if not snapshots:
        # No data yet
        return DashboardResponse(
            user_id=user.id,
            has_data=False
        )

    # Latest snapshot
    latest = snapshots[0]

    # Build spending breakdown
    spending_breakdown = SpendingBreakdown(
        tuition=latest.tuition,
        housing=latest.housing,
        food=latest.food,
        transportation=latest.transportation,
        books_supplies=latest.books_supplies,
        entertainment=latest.entertainment,
        personal_care=latest.personal_care,
        technology=latest.technology,
        health_wellness=latest.health_wellness,
        miscellaneous=latest.miscellaneous
    )

    # Compute analytics
    analytics_service = AnalyticsService()
    analytics = analytics_service.compute(latest)

    # Risk scores
    risk_scores = {
        "overspending_prob": latest.overspending_prob,
        "financial_stress_prob": latest.financial_stress_prob
    }

    # Get cached summary or create default
    if latest.summary:
        summary = SummaryOutput(**latest.summary)
    else:
        summary = SummaryOutput(
            summary_paragraph="Your financial data is being analyzed.",
            key_points=["Complete a check-in to get personalized insights."]
        )

    # Build history for charts (reverse to chronological order)
    history = [
        SnapshotHistory(
            snapshot_id=s.id,
            created_at=s.created_at,
            overspending_prob=s.overspending_prob or 0,
            financial_stress_prob=s.financial_stress_prob or 0,
            total_spending=s.total_spending,
            total_resources=s.total_resources
        )
        for s in reversed(snapshots)
    ]

    return DashboardResponse(
        user_id=user.id,
        latest_snapshot_id=latest.id,
        spending_breakdown=spending_breakdown,
        analytics=analytics,
        risk_scores=risk_scores,
        summary=summary,
        history=history,
        has_data=True
    )
