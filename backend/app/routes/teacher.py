from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID
from typing import Optional
from datetime import date

from ..database import get_db
from ..schemas.teacher import (
    TeacherChatRequest,
    TeacherChatResponse,
    ChatHistoryResponse,
    ChatHistory
)
from ..schemas.intake import SnapshotData
from ..schemas.ml import MLInput, MLOutput
from ..models.user import User
from ..models.snapshot import SpendingSnapshot
from ..models.interaction import TeacherInteraction
from ..services import ClaudeTeacherService, AnalyticsService, SpendingRiskModelService, ClaudeSummarizerService
from ..utils.auth import get_current_user

router = APIRouter()


@router.post("/chat", response_model=TeacherChatResponse)
async def teacher_chat(
    request: TeacherChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the teacher agent and get a response.

    Uses the latest snapshot (or specified snapshot) to provide
    context-aware financial guidance.
    """
    # Get the relevant snapshot
    if request.snapshot_id:
        snapshot = (
            db.query(SpendingSnapshot)
            .filter(
                SpendingSnapshot.id == request.snapshot_id,
                SpendingSnapshot.user_id == user.id
            )
            .first()
        )
        if not snapshot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Snapshot not found"
            )
    else:
        # Get latest snapshot
        snapshot = (
            db.query(SpendingSnapshot)
            .filter(SpendingSnapshot.user_id == user.id)
            .order_by(desc(SpendingSnapshot.created_at))
            .first()
        )

    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No spending data available. Please complete onboarding first."
        )

    # Get previous snapshot for comparison (if exists)
    previous_snapshot = (
        db.query(SpendingSnapshot)
        .filter(
            SpendingSnapshot.user_id == user.id,
            SpendingSnapshot.created_at < snapshot.created_at
        )
        .order_by(desc(SpendingSnapshot.created_at))
        .first()
    )

    # Initialize services
    teacher_service = ClaudeTeacherService()
    analytics_service = AnalyticsService()

    # Convert snapshot to Pydantic model
    snapshot_data = SnapshotData(
        age=snapshot.age,
        gender=snapshot.gender,
        year_in_school=snapshot.year_in_school,
        major=snapshot.major,
        monthly_income=snapshot.monthly_income,
        financial_aid=snapshot.financial_aid,
        tuition=snapshot.tuition,
        housing=snapshot.housing,
        food=snapshot.food,
        transportation=snapshot.transportation,
        books_supplies=snapshot.books_supplies,
        entertainment=snapshot.entertainment,
        personal_care=snapshot.personal_care,
        technology=snapshot.technology,
        health_wellness=snapshot.health_wellness,
        miscellaneous=snapshot.miscellaneous,
        preferred_payment_method=snapshot.preferred_payment_method
    )

    # Get ML outputs
    ml_output = MLOutput(
        overspending_prob=snapshot.overspending_prob or 0.0,
        financial_stress_prob=snapshot.financial_stress_prob or 0.0
    )

    # Compute analytics
    analytics = analytics_service.compute(snapshot_data)

    # Prepare previous data if available
    previous_data = None
    previous_analytics = None
    if previous_snapshot:
        previous_data = SnapshotData(
            age=previous_snapshot.age,
            gender=previous_snapshot.gender,
            year_in_school=previous_snapshot.year_in_school,
            major=previous_snapshot.major,
            monthly_income=previous_snapshot.monthly_income,
            financial_aid=previous_snapshot.financial_aid,
            tuition=previous_snapshot.tuition,
            housing=previous_snapshot.housing,
            food=previous_snapshot.food,
            transportation=previous_snapshot.transportation,
            books_supplies=previous_snapshot.books_supplies,
            entertainment=previous_snapshot.entertainment,
            personal_care=previous_snapshot.personal_care,
            technology=previous_snapshot.technology,
            health_wellness=previous_snapshot.health_wellness,
            miscellaneous=previous_snapshot.miscellaneous,
            preferred_payment_method=previous_snapshot.preferred_payment_method
        )
        previous_analytics = analytics_service.compute(previous_data)

    # Generate teacher response
    teacher_output = await teacher_service.generate_response(
        snapshot=snapshot_data,
        ml_output=ml_output,
        analytics=analytics,
        user_message=request.user_message,
        previous_snapshot=previous_data,
        previous_analytics=previous_analytics
    )

    # Process field updates if any were detected
    if teacher_output.field_updates:
        # Create updated snapshot data
        updated_data = snapshot_data.model_dump()
        for update in teacher_output.field_updates:
            if update.field in updated_data:
                updated_data[update.field] = int(update.value)

        # Create new snapshot with updates
        new_snapshot_data = SnapshotData(**updated_data)

        # Run ML prediction
        ml_service = SpendingRiskModelService()
        ml_input = MLInput(**new_snapshot_data.model_dump())
        new_ml_output = await ml_service.predict(ml_input)

        # Compute new analytics
        new_analytics = analytics_service.compute(new_snapshot_data)

        # Generate new summary
        summarizer_service = ClaudeSummarizerService()
        new_summary = await summarizer_service.summarize(
            new_snapshot_data, new_ml_output, new_analytics
        )

        # Check if current snapshot was created today - if so, update it instead of creating new
        snapshot_date = snapshot.created_at.date()
        today = date.today()

        if snapshot_date == today:
            # Update existing snapshot
            for key, value in new_snapshot_data.model_dump().items():
                setattr(snapshot, key, value)
            snapshot.overspending_prob = new_ml_output.overspending_prob
            snapshot.financial_stress_prob = new_ml_output.financial_stress_prob
            snapshot.summary = new_summary.model_dump()
            db.commit()
            db.refresh(snapshot)
        else:
            # Create new snapshot for new day/month
            new_snapshot = SpendingSnapshot(
                user_id=user.id,
                **new_snapshot_data.model_dump(),
                overspending_prob=new_ml_output.overspending_prob,
                financial_stress_prob=new_ml_output.financial_stress_prob,
                summary=new_summary.model_dump()
            )
            db.add(new_snapshot)
            db.commit()
            db.refresh(new_snapshot)

            # Use the new snapshot for the interaction
            snapshot = new_snapshot

    # Save interaction
    interaction = TeacherInteraction(
        user_id=user.id,
        snapshot_id=snapshot.id,
        user_message=request.user_message,
        teacher_response=teacher_output.model_dump()
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    return TeacherChatResponse(
        interaction_id=interaction.id,
        teacher_output=teacher_output,
        created_at=interaction.created_at
    )


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the user's chat history with the teacher."""
    interactions = (
        db.query(TeacherInteraction)
        .filter(TeacherInteraction.user_id == user.id)
        .order_by(desc(TeacherInteraction.created_at))
        .limit(limit)
        .all()
    )

    from ..schemas.teacher import TeacherOutput

    history = [
        ChatHistory(
            interaction_id=i.id,
            user_message=i.user_message,
            teacher_response=TeacherOutput(**i.teacher_response),
            created_at=i.created_at
        )
        for i in reversed(interactions)
    ]

    return ChatHistoryResponse(history=history)
