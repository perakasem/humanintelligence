from pydantic import BaseModel
from typing import Literal
from uuid import UUID
from datetime import datetime


class LessonOutline(BaseModel):
    """Structure for a mini financial literacy lesson."""
    title: str
    bullet_points: list[str]


class FieldUpdate(BaseModel):
    """A single field update detected from user message."""
    field: str
    value: int | float


class TeacherOutput(BaseModel):
    """Output from the teacher agent."""
    response_type: Literal["coaching", "feedback", "update"] = "coaching"
    priority_issues: list[str]
    explanation: str
    actions_for_week: list[str] = []  # Optional - empty for feedback responses
    lesson_outline: LessonOutline | None = None  # Optional - not always needed
    field_updates: list[FieldUpdate] = []  # Detected updates from user message


class TeacherChatRequest(BaseModel):
    """Request schema for teacher chat."""
    snapshot_id: UUID | None = None  # If None, uses latest snapshot
    user_message: str


class TeacherChatResponse(BaseModel):
    """Response schema for teacher chat."""
    interaction_id: UUID
    teacher_output: TeacherOutput
    created_at: datetime


class ChatHistory(BaseModel):
    """Single chat history entry."""
    interaction_id: UUID
    user_message: str
    teacher_response: TeacherOutput
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    """Response schema for chat history."""
    history: list[ChatHistory]
