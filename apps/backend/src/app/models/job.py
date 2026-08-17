"""
What: Defines the Job entity.
Why: Postgres-backed background job queue for async tasks (like generating plans or grading interviews) that survive process restarts.
Boundaries: Just the schema; job runner and dispatch logic belong in src/app/jobs/.
"""

from datetime import datetime, UTC
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import Base

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    
    # enum: generate_plan, grade_interview
    job_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # enum: pending, processing, done, failed
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
