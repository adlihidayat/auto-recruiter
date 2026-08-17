"""
What: Defines the Candidate entity.
Why: Represents an individual taking a specific interview. Solves dashboard performance by hoisting summary metrics (status, score, recommendation) out of heavy JSON blobs.
Boundaries: Ties candidates to an interview but does not contain actual grading logic or raw interaction logs.
"""

from datetime import datetime, UTC
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, DateTime, ForeignKey
from app.models.base import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    interview_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interviews.id"), nullable=False, index=True)
    
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # enum: not_started, in_progress, finished
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="not_started")
    
    composite_score: Mapped[float] = mapped_column(Float, nullable=True)
    recommendation: Mapped[str] = mapped_column(String(100), nullable=True)
    
    room_token: Mapped[str] = mapped_column(String(1000), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relationships
    interview = relationship("Interview")
