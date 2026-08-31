"""
What: Defines the UserRecentInterview entity.
Why: Tracks user-specific recently viewed interviews in PostgreSQL for Notion-like cross-device persistence.
Boundaries: Scoped per user account; max 5 items queried at a time.
"""

from datetime import datetime, UTC
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from app.models.base import Base

class UserRecentInterview(Base):
    __tablename__ = "user_recent_interviews"
    __table_args__ = (
        UniqueConstraint("user_id", "interview_id", name="uq_user_interview_recent"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    interview_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interviews.id"), nullable=False, index=True)
    
    viewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    user = relationship("User")
    interview = relationship("Interview")
