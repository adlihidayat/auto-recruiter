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
    icon: str | None = "💼"

class InterviewCreate(InterviewBase):
    candidates: list[CandidateCreate] = []

class InterviewUpdate(BaseModel):
    job_name: str | None = None
    job_description: str | None = None
    difficulty: str | None = None
    num_goals: int | None = None
    total_duration_minutes: int | None = None
    domain_hint: str | None = None
    communication_weight: float | None = None
    scheduled_at: datetime | None = None
    icon: str | None = None

from app.schemas.candidate import CandidateResponse

class GoalResponse(BaseModel):
    id: UUID
    goal_ref: str
    interview_id: UUID
    topic: str
    goal: str
    passing_criteria: list[str] = []
    pushback_triggers: list[dict] = []
    wrong_answer_signals: list[str] = []
    suggested_opening: str | None = None
    weight: float = 1.0

    model_config = ConfigDict(from_attributes=True)

class CreatorInfo(BaseModel):
    id: UUID
    username: str | None = None
    email: str

    model_config = ConfigDict(from_attributes=True)

class InterviewResponse(InterviewBase):
    id: UUID
    creator_id: UUID
    creator: CreatorInfo | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InterviewCreationResponse(BaseModel):
    interview: InterviewResponse
    candidates: list[CandidateResponse]

class BatchDeleteInterviewsRequest(BaseModel):
    interview_ids: list[UUID]

