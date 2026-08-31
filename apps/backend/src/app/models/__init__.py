"""
What: Model exports.
Why: Centralizes model imports for Alembic migration discovery and clean app imports.
"""

from app.models.base import Base
from app.models.user import User
from app.models.interview import Interview
from app.models.candidate import Candidate
from app.models.goal import Goal
from app.models.transcript import Transcript
from app.models.report import CandidateReport
from app.models.job import Job
from app.models.user_recent import UserRecentInterview

__all__ = [
    "Base",
    "User",
    "Interview",
    "Candidate",
    "Goal",
    "Transcript",
    "CandidateReport",
    "Job",
    "UserRecentInterview",
]
