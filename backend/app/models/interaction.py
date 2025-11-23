import uuid
from datetime import datetime
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from ..database import Base


class TeacherInteraction(Base):
    """Teacher interaction model for storing chat history."""
    __tablename__ = "teacher_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("spending_snapshots.id"), nullable=True)

    # Chat content
    user_message = Column(Text, nullable=False)
    teacher_response = Column(JSONB, nullable=False)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="interactions")
    snapshot = relationship("SpendingSnapshot", back_populates="interactions")

    def __repr__(self):
        return f"<TeacherInteraction {self.id}>"
