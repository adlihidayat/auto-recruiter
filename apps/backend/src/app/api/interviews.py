"""
What: Interview API routes.
Why: Exposes endpoints for the frontend to list interviews and their associated candidates.
Boundaries: Connects HTTP layer to Database layer without housing complex business logic.
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import SessionDep, CurrentUser
from app.models.interview import Interview
from app.models.candidate import Candidate
from app.schemas.interview import InterviewResponse
from app.schemas.candidate import CandidateResponse

router = APIRouter()

@router.get("", response_model=list[InterviewResponse])
async def list_interviews(session: SessionDep, current_user: CurrentUser):
    """
    List all interviews created by the current user.
    """
    result = await session.execute(
        select(Interview)
        .where(Interview.creator_id == current_user.id)
        .order_by(Interview.created_at.desc())
    )
    interviews = result.scalars().all()
    return list(interviews)

@router.get("/{interview_id}/candidates", response_model=list[CandidateResponse])
async def list_interview_candidates(
    interview_id: UUID,
    session: SessionDep,
    current_user: CurrentUser
):
    """
    List all candidates associated with a specific interview.
    Verifies that the interview belongs to the current user.
    """
    # Verify ownership
    result = await session.execute(
        select(Interview).where(
            Interview.id == interview_id,
            Interview.creator_id == current_user.id
        )
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
        
    # Fetch candidates
    candidates_result = await session.execute(
        select(Candidate)
        .where(Candidate.interview_id == interview_id)
        .order_by(Candidate.created_at.desc())
    )
    candidates = candidates_result.scalars().all()
    return list(candidates)
