"""
What: Interview API routes.
Why: Exposes endpoints for the frontend to create and list interviews and their associated candidates.
Boundaries: Connects HTTP layer to Database layer without housing complex business logic.
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from sqlalchemy import select

from app.api.deps import SessionDep, CurrentUser
from app.models.interview import Interview
from app.models.candidate import Candidate
from app.models.job import Job
from app.schemas.interview import InterviewCreate, InterviewResponse
from app.schemas.candidate import CandidateResponse
from app.services.plan_service import process_interview_plan_generation

router = APIRouter()

@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    payload: InterviewCreate,
    session: SessionDep,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks
):
    """
    Create a new interview position, register initial candidates, and enqueue an async plan generation job.
    """
    # 1. Create Interview
    new_interview = Interview(
        creator_id=current_user.id,
        job_name=payload.job_name,
        job_description=payload.job_description,
        difficulty=payload.difficulty,
        num_goals=payload.num_goals,
        total_duration_minutes=payload.total_duration_minutes,
        domain_hint=payload.domain_hint,
        communication_weight=payload.communication_weight,
        status="generating_plan"
    )
    session.add(new_interview)
    await session.flush()

    # 2. Register initial candidates if provided
    for cand_data in payload.candidates:
        new_candidate = Candidate(
            interview_id=new_interview.id,
            email=cand_data.email,
            first_name=cand_data.first_name,
            last_name=cand_data.last_name,
            status="not_started"
        )
        session.add(new_candidate)

    # 3. Enqueue background Job to generate evaluation plan via AI agent
    background_job = Job(
        job_type="generate_plan",
        status="pending",
        payload={"interview_id": str(new_interview.id)}
    )
    session.add(background_job)

    await session.commit()
    await session.refresh(new_interview)

    # 4. Trigger asynchronous background plan generation (calls Agents Service over HTTP)
    background_tasks.add_task(process_interview_plan_generation, new_interview.id)

    return new_interview

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
