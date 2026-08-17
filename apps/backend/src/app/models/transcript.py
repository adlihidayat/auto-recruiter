"""
What: Defines the Transcript entity.
Why: Stores individual conversational turns per candidate per goal, plus the interviewer-agent's internal reasoning.
Boundaries: Exposes clean interaction history for the grader, but keeps internal reasoning private to the backend.
"""

from datetime import datetime, UTC
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from app.models.base import Base

class Transcript(Base):
    __tablename__ = "transcripts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    goal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("goals.id"), nullable=False, index=True)
    
    # enum: interviewer, candidate
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Internal Interviewer fields (populated only when role == 'interviewer')
    action: Mapped[str] = mapped_column(String(50), nullable=True)
    reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    trigger_matched: Mapped[str] = mapped_column(String(255), nullable=True)
    flag_for_human_review: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)

    # Relationships
    candidate = relationship("Candidate")
    goal = relationship("Goal")
