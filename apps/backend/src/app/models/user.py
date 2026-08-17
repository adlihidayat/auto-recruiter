"""
What: Defines the User entity.
Why: Represents the HR user or system administrator who creates and manages interviews.
Boundaries: Contains no authentication or business logic, strictly DB schema.
"""

from datetime import datetime, UTC
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
