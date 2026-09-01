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

from fastapi import BackgroundTasks
from app.schemas.transcript import CandidateFinishRequest
from app.services.grader_service import process_candidate_grading

@router.post("/{candidate_id}/finish", status_code=status.HTTP_202_ACCEPTED)
async def finish_candidate_interview(
    candidate_id: UUID,
    request: CandidateFinishRequest,
    background_tasks: BackgroundTasks,
    session: SessionDep
):
    """
    Called by the Realtime Worker when an interview completes.
    Saves the full transcript history and dispatches a background task to grade the candidate.
    Note: Realtime Worker might not pass a user token, so this endpoint might need to be unprotected
    or protected by a service token in production. For now we assume internal access.
    """
    # Fetch candidate
    result = await session.execute(
        select(Candidate).where(Candidate.id == candidate_id)
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
        
    # Save transcripts
    for t_data in request.transcripts:
        transcript = Transcript(
            candidate_id=candidate.id,
            goal_id=t_data.goal_id,
            role=t_data.role,
            content=t_data.content,
            action=t_data.action,
            reasoning=t_data.reasoning,
            trigger_matched=t_data.trigger_matched,
            flag_for_human_review=t_data.flag_for_human_review,
        )
        # only override created_at if provided
        if t_data.created_at:
            transcript.created_at = t_data.created_at
            
        session.add(transcript)
        
    # Update candidate status to on-progress (since grading takes time)
    candidate.status = "on-progress"

    # Update parent interview status to on-progress
    interview_res = await session.execute(
        select(Interview).where(Interview.id == candidate.interview_id)
    )
    parent_interview = interview_res.scalar_one_or_none()
    if parent_interview and parent_interview.status != "finished":
        parent_interview.status = "on-progress"
    
    await session.commit()
    
    # Dispatch Background Task for grading
    background_tasks.add_task(process_candidate_grading, candidate.id)
    
    return {"status": "accepted", "message": "Interview finished, grading in progress"}
