"""
What: Interview API routes.
Why: Exposes endpoints for the frontend to create and list interviews and their associated candidates.
Boundaries: Connects HTTP layer to Database layer without housing complex business logic.
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from sqlalchemy import select, delete
from livekit import api

from app.core.config import application_settings
from app.api.deps import SessionDep, CurrentUser
from app.models.interview import Interview
from app.models.candidate import Candidate
from app.models.goal import Goal
from app.models.transcript import Transcript
from app.models.report import CandidateReport
from app.models.job import Job
from app.schemas.interview import InterviewCreate, InterviewResponse, InterviewCreationResponse, InterviewUpdate
from app.schemas.candidate import CandidateResponse
from app.services.plan_service import process_interview_plan_generation

router = APIRouter()

@router.post("", response_model=InterviewCreationResponse, status_code=status.HTTP_201_CREATED)
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
            status="not-started"
        )
        session.add(new_candidate)
        await session.flush() # flush to get candidate ID

        # Generate LiveKit Token
        token = api.AccessToken(
            application_settings.LIVEKIT_API_KEY, 
            application_settings.LIVEKIT_API_SECRET
        ) \
            .with_identity(str(new_candidate.id)) \
            .with_name(f"{cand_data.first_name} {cand_data.last_name}") \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=str(new_candidate.id)
            ))
            
        new_candidate.room_token = token.tojwt() if hasattr(token, 'tojwt') else token.to_jwt()

        # Explicitly dispatch the interviewer agent for this room
        try:
            livekit_api = api.LiveKitAPI(
                application_settings.LIVEKIT_URL,
                application_settings.LIVEKIT_API_KEY,
                application_settings.LIVEKIT_API_SECRET
            )
            await livekit_api.agent_dispatch.create_dispatch(
                api.CreateAgentDispatchRequest(
                    agent_name="interviewer-agent",
                    room=str(new_candidate.id)
                )
            )
            await livekit_api.aclose()
        except Exception as e:
            # We log it but do not fail interview creation if dispatch fails
            import logging
            logging.error(f"Failed to explicitly dispatch agent: {e}")

    # 3. Enqueue background Job to generate evaluation plan via AI agent
    background_job = Job(
        job_type="generate_plan",
        status="pending",
        payload={"interview_id": str(new_interview.id)}
    )
    session.add(background_job)

    await session.commit()
    await session.refresh(new_interview)

    # 4. Trigger synchronous plan generation (calls Agents Service over HTTP)
    # The frontend is mocking a loading screen and expects this to block until ready.
    await process_interview_plan_generation(new_interview.id)

    # Re-fetch candidates to ensure their status/info is up to date (though we just created them)
    candidates_result = await session.execute(
        select(Candidate).where(Candidate.interview_id == new_interview.id)
    )
    final_candidates = candidates_result.scalars().all()

    # Re-fetch the interview since the background job processing updates its status
    await session.refresh(new_interview)

    return {
        "interview": new_interview,
        "candidates": final_candidates
    }

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

@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: UUID,
    session: SessionDep,
    current_user: CurrentUser
):
    """
    Get a single interview by ID. Verifies ownership.
    """
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
    return interview

@router.patch("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: UUID,
    payload: InterviewUpdate,
    session: SessionDep,
    current_user: CurrentUser
):
    """
    Update an interview position's details (job_name, job_description, difficulty, scheduled_at, etc.).
    """
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

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(interview, field, value)

    await session.commit()
    await session.refresh(interview)
    return interview

@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview(
    interview_id: UUID,
    session: SessionDep,
    current_user: CurrentUser
):
    """
    Delete an interview position and all associated candidates, goals, transcripts, reports, and jobs.
    """
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

    # 1. Fetch candidate IDs associated with this interview
    cand_result = await session.execute(
        select(Candidate.id).where(Candidate.interview_id == interview_id)
    )
    candidate_ids = cand_result.scalars().all()

    if candidate_ids:
        # Delete reports for these candidates
        await session.execute(
            delete(CandidateReport).where(CandidateReport.candidate_id.in_(candidate_ids))
        )
        # Delete transcripts for these candidates
        await session.execute(
            delete(Transcript).where(Transcript.candidate_id.in_(candidate_ids))
        )
        # Delete candidates
        await session.execute(
            delete(Candidate).where(Candidate.interview_id == interview_id)
        )

    # 2. Delete goals associated with this interview
    await session.execute(
        delete(Goal).where(Goal.interview_id == interview_id)
    )

    # 3. Delete background jobs associated with this interview
    # Job.payload is JSONB: payload['interview_id']
    await session.execute(
        delete(Job).where(Job.payload["interview_id"].as_string() == str(interview_id))
    )

    # 4. Delete the interview record itself
    await session.delete(interview)
    await session.commit()
    return None
