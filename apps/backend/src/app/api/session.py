"""
What: Public Interview Session API routes.
Why: Handles candidate initialization and entry using only the secure LiveKit token.
Boundaries: Does not require JWT auth; public facing for candidates only.
"""

import logging
import json
from uuid import UUID
import jwt
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from livekit import api

from app.api.deps import SessionDep
from app.models.candidate import Candidate
from app.models.interview import Interview
from app.models.goal import Goal
from app.schemas.session import SessionStatusResponse
from app.core.config import application_settings

logger = logging.getLogger(__name__)

router = APIRouter()

def _extract_candidate_id_from_token(token: str) -> UUID | None:
    try:
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        sub = unverified_payload.get("sub") or unverified_payload.get("identity")
        if sub:
            return UUID(sub)
        video = unverified_payload.get("video", {})
        if isinstance(video, dict) and video.get("room"):
            return UUID(video["room"])
    except Exception:
        pass
    return None

@router.get("/{token}", response_model=SessionStatusResponse)
async def get_session_status(token: str, session: SessionDep):
    """
    Called when candidate opens the invite link.
    Verifies token, returns candidate status and interview basics.
    """
    cand_id = _extract_candidate_id_from_token(token)
    stmt = select(Candidate, Interview).join(Interview, Candidate.interview_id == Interview.id)
    if cand_id:
        stmt = stmt.where((Candidate.room_token == token) | (Candidate.id == cand_id))
    else:
        stmt = stmt.where(Candidate.room_token == token)

    result = await session.execute(stmt)
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired interview token."
        )
        
    candidate, interview = row
    
    return SessionStatusResponse(
        candidate_id=candidate.id,
        first_name=candidate.first_name,
        last_name=candidate.last_name,
        status=candidate.status,
        job_name=interview.job_name,
        total_duration_minutes=interview.total_duration_minutes,
    )

@router.post("/{token}/start", status_code=status.HTTP_200_OK)
async def start_interview_session(token: str, session: SessionDep):
    """
    Called when candidate clicks 'Enter Interview Room'.
    Transitions candidate to on-progress and dispatches the LiveKit agent.
    """
    cand_id = _extract_candidate_id_from_token(token)
    stmt = select(Candidate)
    if cand_id:
        stmt = stmt.where((Candidate.room_token == token) | (Candidate.id == cand_id))
    else:
        stmt = stmt.where(Candidate.room_token == token)

    result = await session.execute(stmt)
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired interview token."
        )
        
    if candidate.status == "finished":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview has already been completed."
        )

    # 1. Fetch Goal records for the interview
    goal_res = await session.execute(
        select(Goal)
        .where(Goal.interview_id == candidate.interview_id)
        .order_by(Goal.goal_ref.asc())
    )
    goals = goal_res.scalars().all()
    
    # Serialize goals to pass into agent dispatch metadata
    goals_data = [
        {
            "id": str(g.id),
            "goal_ref": g.goal_ref,
            "topic": g.topic,
            "goal": g.goal,
            "passing_criteria": g.passing_criteria,
            "pushback_triggers": g.pushback_triggers,
            "wrong_answer_signals": g.wrong_answer_signals,
            "references": g.references,
            "grounding_theory": g.grounding_theory,
            "suggested_opening": g.suggested_opening,
            "weight": g.weight,
            "gating": g.gating
        } for g in goals
    ]
    goals_json = json.dumps(goals_data)

    # 2. Dispatch LiveKit Agent
    try:
        livekit_api = api.LiveKitAPI(
            application_settings.LIVEKIT_URL,
            application_settings.LIVEKIT_API_KEY,
            application_settings.LIVEKIT_API_SECRET
        )
        await livekit_api.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name="interviewer-agent",
                room=str(candidate.id),
                metadata=goals_json
            )
        )
        await livekit_api.aclose()
        logger.info(f"Dispatched agent for room/candidate: {candidate.id} with {len(goals)} goals")
    except Exception as e:
        logger.error(f"Failed to explicitly dispatch agent: {e}")
        # Note: Depending on business rules, we might want to return a 500 here if dispatch is strictly required.
        # But often, retries or fallback manual starts might be preferred. We'll raise 500 for strictness.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize AI interviewer. Please try again."
        )

    # 2. Update status
    if candidate.status == "not-started":
        candidate.status = "on-progress"
        await session.commit()

    return {"status": "started"}
