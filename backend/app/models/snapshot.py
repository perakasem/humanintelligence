import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base


class SpendingSnapshot(Base):
    """Spending snapshot model for storing ML input features and outputs."""
    __tablename__ = "spending_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # ML Input Features (all integers as per spec)
    age = Column(Integer, nullable=False)
    gender = Column(Integer, nullable=False)
    year_in_school = Column(Integer, nullable=False)
    major = Column(Integer, nullable=False)
    monthly_income = Column(Integer, nullable=False)
    financial_aid = Column(Integer, nullable=False)
    tuition = Column(Integer, nullable=False)
    housing = Column(Integer, nullable=False)
    food = Column(Integer, nullable=False)
    transportation = Column(Integer, nullable=False)
    books_supplies = Column(Integer, nullable=False)
    entertainment = Column(Integer, nullable=False)
    personal_care = Column(Integer, nullable=False)
    technology = Column(Integer, nullable=False)
    health_wellness = Column(Integer, nullable=False)
    miscellaneous = Column(Integer, nullable=False)
    preferred_payment_method = Column(Integer, nullable=False)

    # ML Outputs
    overspending_prob = Column(Float, nullable=True)
    financial_stress_prob = Column(Float, nullable=True)

    # Summarizer output (cached)
    summary = Column(JSON, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="snapshots")
    interactions = relationship("TeacherInteraction", back_populates="snapshot")

    def __repr__(self):
        return f"<SpendingSnapshot {self.id} for user {self.user_id}>"

    def to_ml_input(self) -> dict:
        """Convert snapshot to ML model input format."""
        return {
            "age": self.age,
            "gender": self.gender,
            "year_in_school": self.year_in_school,
            "major": self.major,
            "monthly_income": self.monthly_income,
            "financial_aid": self.financial_aid,
            "tuition": self.tuition,
            "housing": self.housing,
            "food": self.food,
            "transportation": self.transportation,
            "books_supplies": self.books_supplies,
            "entertainment": self.entertainment,
            "personal_care": self.personal_care,
            "technology": self.technology,
            "health_wellness": self.health_wellness,
            "miscellaneous": self.miscellaneous,
            "preferred_payment_method": self.preferred_payment_method,
        }

    @property
    def total_resources(self) -> [int]:
        """Calculate total monthly resources (income + aid)."""
        return self.monthly_income + self.financial_aid

    @property
    def total_spending(self) -> [int]:
        """Calculate total monthly spending."""
        return (
            self.tuition + self.housing + self.food + self.transportation +
            self.books_supplies + self.entertainment + self.personal_care +
            self.technology + self.health_wellness + self.miscellaneous
        )

    @property
    def discretionary_spending(self) -> [int]:
        """Calculate discretionary spending (entertainment, personal care, misc)."""
        return self.entertainment + self.personal_care + self.miscellaneous
