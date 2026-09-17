from pydantic import BaseModel, ConfigDict
from uuid import UUID

class SessionStatusResponse(BaseModel):
    candidate_id: UUID
    first_name: str | None
    last_name: str | None
    status: str
    job_name: str
    total_duration_minutes: int

    model_config = ConfigDict(from_attributes=True)
