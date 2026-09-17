from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class CandidateBase(BaseModel):
    email: str
    first_name: str | None = None
    last_name: str | None = None

class CandidateResponse(CandidateBase):
    id: UUID
    interview_id: UUID
    status: str
    composite_score: float | None = None
    recommendation: str | None = None
    room_token: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
