import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base


class User(Base):
    """Class for storing user information."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    google_sub = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    picture = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Profile fields (collected once during initial onboarding)
    age = Column(Integer, nullable=True)
    gender = Column(Integer, nullable=True)  # 0=Male, 1=Female, 2=Non-binary, 3=Prefer not to say
    year_in_school = Column(Integer, nullable=True)  # 0=Freshman, 1=Sophomore, 2=Junior, 3=Senior, 4=Graduate
    major = Column(Integer, nullable=True)  # 0=STEM, 1=Business, etc.
    preferred_payment_method = Column(Integer, nullable=True)  # 0=Cash, 1=Credit, 2=Debit, 3=Mobile

    # Relationships
    snapshots = relationship("SpendingSnapshot", back_populates="user", cascade="all, delete-orphan")
    interactions = relationship("TeacherInteraction", back_populates="user", cascade="all, delete-orphan")

    @property
    def has_profile(self) -> bool:
        """Check if user has completed their profile."""
        return all([
            self.age is not None,
            self.gender is not None,
            self.year_in_school is not None,
            self.major is not None,
            self.preferred_payment_method is not None
        ])

    def __repr__(self):
        return f"<User {self.email}>"
