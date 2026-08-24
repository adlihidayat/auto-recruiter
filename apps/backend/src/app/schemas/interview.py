from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class CandidateCreate(BaseModel):
    email: str
    first_name: str | None = None
    last_name: str | None = None

class InterviewBase(BaseModel):
    job_name: str
    job_description: str
    difficulty: str = "mid"
    num_goals: int = 4
    total_duration_minutes: int = 30
    domain_hint: str | None = None
    communication_weight: float = 0.0
    scheduled_at: datetime | None = None

class InterviewCreate(InterviewBase):
    candidates: list[CandidateCreate] = []

from app.schemas.candidate import CandidateResponse

class InterviewResponse(InterviewBase):
    id: UUID
    creator_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InterviewCreationResponse(BaseModel):
    interview: InterviewResponse
    candidates: list[CandidateResponse]
