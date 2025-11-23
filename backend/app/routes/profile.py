from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.profile import ProfileData, ProfileResponse
from ..models.user import User
from ..utils.auth import get_current_user

router = APIRouter()


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's profile data."""
    return ProfileResponse(
        age=user.age,
        gender=user.gender,
        year_in_school=user.year_in_school,
        major=user.major,
        preferred_payment_method=user.preferred_payment_method,
        has_profile=user.has_profile
    )


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    profile: ProfileData,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's profile data."""
    if profile.age is not None:
        user.age = profile.age
    if profile.gender is not None:
        user.gender = profile.gender
    if profile.year_in_school is not None:
        user.year_in_school = profile.year_in_school
    if profile.major is not None:
        user.major = profile.major
    if profile.preferred_payment_method is not None:
        user.preferred_payment_method = profile.preferred_payment_method

    db.commit()
    db.refresh(user)

    return ProfileResponse(
        age=user.age,
        gender=user.gender,
        year_in_school=user.year_in_school,
        major=user.major,
        preferred_payment_method=user.preferred_payment_method,
        has_profile=user.has_profile
    )
