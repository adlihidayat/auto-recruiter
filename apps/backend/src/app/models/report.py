"""
What: Defines the CandidateReport entity.
Why: Stores the full, granular grading output from the interview-grader-agent.
Boundaries: Used primarily for detailed UI popups; high-level metrics are already hoisted to the Candidate table for fast listing.
"""

from datetime import datetime, UTC
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import Base

class CandidateReport(Base):
    __tablename__ = "candidate_reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # One-to-one relationship with candidate
    candidate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidates.id"), nullable=False, unique=True, index=True)
    
    overall_confidence: Mapped[str] = mapped_column(String(50), nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Stores criteria_match, injection_findings, communication_traits, etc.
    raw_report: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    grader_version: Mapped[str] = mapped_column(String(50), nullable=False)
    graded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relationships
    candidate = relationship("Candidate")
