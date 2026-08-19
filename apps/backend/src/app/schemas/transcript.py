from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class TranscriptResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    goal_id: UUID
    role: str
    content: str
    action: str | None = None
    reasoning: str | None = None
    trigger_matched: str | None = None
    flag_for_human_review: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
