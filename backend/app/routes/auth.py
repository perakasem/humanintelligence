from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime

from ..database import get_db
from ..config import get_settings
from ..schemas.auth import GoogleAuthRequest, AuthResponse, UserResponse
from ..models.user import User
from ..utils.auth import create_access_token

router = APIRouter()
settings = get_settings()


@router.post("/google/callback", response_model=AuthResponse)
async def google_auth_callback(
    auth_request: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Exchange Google ID token for app JWT.
    Creates user if first time, otherwise returns existing user.
    """
    try:
        # Verify the Google ID token
        idinfo = id_token.verify_oauth2_token(
            auth_request.credential,
            requests.Request(),
            settings.google_client_id
        )

        # Get user info from token
        google_sub = idinfo["sub"]
        email = idinfo.get("email", "")
        name = idinfo.get("name", "")
        picture = idinfo.get("picture", "")

        # Check if user exists
        user = db.query(User).filter(User.google_sub == google_sub).first()
        is_new_user = False

        if not user:
            # Create new user
            user = User(
                google_sub=google_sub,
                email=email,
                name=name,
                picture=picture
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            is_new_user = True
        else:
            # Update user info if changed
            if user.email != email or user.name != name or user.picture != picture:
                user.email = email
                user.name = name
                user.picture = picture
                user.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(user)

        # Create JWT token
        access_token = create_access_token({"sub": str(user.id)})

        return AuthResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user),
            is_new_user=is_new_user
        )

    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )
