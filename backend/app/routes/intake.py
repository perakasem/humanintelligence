from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.intake import IntakeRequest, IntakeResponse, SnapshotData
from ..schemas.dashboard import Analytics
from ..schemas.ml import MLInput
from ..models.user import User
from ..models.snapshot import SpendingSnapshot
from ..services import (
    ClaudeParserService,
    ClaudeSummarizerService,
    SpendingRiskModelService,
    AnalyticsService
)
from ..utils.auth import get_current_user

router = APIRouter()


@router.post("/intake", response_model=IntakeResponse)
async def submit_intake(
    intake: IntakeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process intake form (onboarding or check-in).

    Flow:
    1. Parse raw answers into structured snapshot using Claude parser
    2. Validate the parsed data
    3. Save snapshot to database
    4. Run ML model to get risk scores
    5. Update snapshot with ML outputs
    6. Compute analytics
    7. Generate summary using Claude summarizer
    8. Return complete response
    """
    # Initialize services
    parser_service = ClaudeParserService()
    ml_service = SpendingRiskModelService()
    analytics_service = AnalyticsService()
    summarizer_service = ClaudeSummarizerService()

    try:
        # Step 1: Parse raw answers into structured snapshot
        # Pass user for profile data (used in check-ins)
        snapshot_data = await parser_service.parse(intake.raw_answers, user)

        # Step 2: Create ML input and run prediction
        ml_input = MLInput(**snapshot_data.model_dump())
        ml_output = await ml_service.predict(ml_input)

        # Step 3: Compute analytics
        analytics = analytics_service.compute(snapshot_data)

        # Step 4: Generate summary
        summary = await summarizer_service.summarize(
            snapshot_data, ml_output, analytics
        )

        # Step 5: Save snapshot to database
        snapshot = SpendingSnapshot(
            user_id=user.id,
            **snapshot_data.model_dump(),
            overspending_prob=ml_output.overspending_prob,
            financial_stress_prob=ml_output.financial_stress_prob,
            summary=summary.model_dump()
        )
        db.add(snapshot)
        # Commit both snapshot and any user profile changes from parser
        db.commit()
        db.refresh(snapshot)
        db.refresh(user)  # Ensure user profile changes are persisted

        # Step 6: Return response
        return IntakeResponse(
            snapshot_id=snapshot.id,
            overspending_prob=ml_output.overspending_prob,
            financial_stress_prob=ml_output.financial_stress_prob,
            summary=summary,
            analytics=analytics,
            created_at=snapshot.created_at
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse intake data: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process intake: {str(e)}"
        )
