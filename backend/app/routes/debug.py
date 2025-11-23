from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..models.snapshot import SpendingSnapshot
from ..models.interaction import TeacherInteraction
from ..utils.auth import get_current_user

router = APIRouter()


@router.delete("/clear-user-data")
async def clear_user_data(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear all data for the current user (snapshots and interactions).
    For development/testing purposes only.
    """
    # Delete interactions first (FK constraint)
    db.query(TeacherInteraction).filter(
        TeacherInteraction.user_id == user.id
    ).delete()

    # Delete snapshots
    db.query(SpendingSnapshot).filter(
        SpendingSnapshot.user_id == user.id
    ).delete()

    # Reset user profile fields so onboarding starts fresh
    user.age = None
    user.gender = None
    user.year_in_school = None
    user.major = None
    user.preferred_payment_method = None

    db.commit()

    return {
        "message": "User data cleared successfully",
        "user_id": str(user.id)
    }
