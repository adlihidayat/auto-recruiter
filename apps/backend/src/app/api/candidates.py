"""
What: Candidate Detail API routes.
Why: Exposes endpoints for the frontend to view a candidate's grading report and turn-by-turn transcripts.
Boundaries: Verifies user ownership via parent interview before returning candidate data.
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import SessionDep, CurrentUser
from app.models.interview import Interview
from app.models.candidate import Candidate
from app.models.report import CandidateReport
from app.models.transcript import Transcript
from app.schemas.report import CandidateReportResponse
from app.schemas.transcript import TranscriptResponse

router = APIRouter()

async def _verify_candidate_ownership(candidate_id: UUID, session: SessionDep, user_id: UUID) -> Candidate:
    """Helper to ensure candidate exists and belongs to an interview created by user_id."""
    result = await session.execute(
        select(Candidate, Interview)
        .join(Interview, Candidate.interview_id == Interview.id)
        .where(Candidate.id == candidate_id, Interview.creator_id == user_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    return row[0]

@router.get("/{candidate_id}/report", response_model=CandidateReportResponse)
async def get_candidate_report(
    candidate_id: UUID,
    session: SessionDep,
    current_user: CurrentUser
):
    """
    Fetch the detailed grading report for a candidate.
    """
    await _verify_candidate_ownership(candidate_id, session, current_user.id)
    
    result = await session.execute(
        select(CandidateReport).where(CandidateReport.candidate_id == candidate_id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grading report not found for candidate"
        )
        
    return report

@router.get("/{candidate_id}/transcripts", response_model=list[TranscriptResponse])
async def get_candidate_transcripts(
    candidate_id: UUID,
    session: SessionDep,
    current_user: CurrentUser
):
    """
    Fetch the conversation transcript turns for a candidate.
    """
    await _verify_candidate_ownership(candidate_id, session, current_user.id)
    
    result = await session.execute(
        select(Transcript)
        .where(Transcript.candidate_id == candidate_id)
        .order_by(Transcript.created_at.asc())
    )
    transcripts = result.scalars().all()
    return list(transcripts)
