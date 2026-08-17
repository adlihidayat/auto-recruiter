"""
What: Defines the Interview entity.
Why: Represents a specific interview opening/position created by a User.
Boundaries: Does not contain candidate details or generated goals directly; those are linked via foreign keys.
"""

from datetime import datetime, UTC
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text
from app.models.base import Base

class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    job_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)
    
    num_goals: Mapped[int] = mapped_column(Integer, default=4)
    total_duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    domain_hint: Mapped[str] = mapped_column(String(100), nullable=True)
    communication_weight: Mapped[float] = mapped_column(Float, default=0.0)
    
    # enum: generating_plan, scheduled, failed_plan_generation
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="generating_plan")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    creator = relationship("User")
