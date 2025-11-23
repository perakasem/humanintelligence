from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..services.claude_survey import ClaudeSurveyService
from ..utils.auth import get_current_user

router = APIRouter()


class ConversationMessage(BaseModel):
    role: str  # "assistant" or "user"
    content: str
    field: str | None = None


class NextQuestionRequest(BaseModel):
    conversation: list[ConversationMessage]
    collected_fields: list[str]


class NextQuestionResponse(BaseModel):
    field: str | None = None
    question: str | None = None
    context: str | None = None
    is_complete: bool
    suggested_type: str | None = None
    options: list[str] | None = None
    progress: float = 0.0


@router.post("/next-question", response_model=NextQuestionResponse)
async def get_next_question(
    request: NextQuestionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the next survey question based on conversation history.
    Uses Claude to generate adaptive, conversational questions.
    For check-ins (users with profile), skips profile fields.
    """
    survey_service = ClaudeSurveyService()

    result = await survey_service.generate_next_question(
        conversation_history=[msg.model_dump() for msg in request.conversation],
        collected_fields=request.collected_fields,
        has_profile=user.has_profile
    )

    return NextQuestionResponse(**result)
