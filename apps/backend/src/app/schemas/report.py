from datetime import datetime
from uuid import UUID
from typing import Any
from pydantic import BaseModel, ConfigDict

class CandidateReportResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    overall_confidence: str
    reasoning: str
    raw_report: dict[str, Any]
    grader_version: str
    graded_at: datetime

    model_config = ConfigDict(from_attributes=True)
