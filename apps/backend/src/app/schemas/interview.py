from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class InterviewBase(BaseModel):
    job_name: str
    job_description: str
    difficulty: str
    num_goals: int
    total_duration_minutes: int
    domain_hint: str | None = None
    communication_weight: float = 0.0

class InterviewResponse(InterviewBase):
    id: UUID
    creator_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
