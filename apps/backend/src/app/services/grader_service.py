"""
What: Asynchronous Background Grading Service.
Why: Orchestrates the background execution flow when a candidate finishes an interview.
Boundaries: Connects database entities to agent HTTP client; does not run inside the HTTP request loop.
"""

import logging
import uuid
from sqlalchemy import select
from app.core.db import async_session_factory
from app.models.interview import Interview
from app.models.goal import Goal
from app.models.candidate import Candidate
from app.models.transcript import Transcript
from app.models.report import CandidateReport
from app.services.agent_client import request_grading_from_agent

logger = logging.getLogger("grader-service")

async def process_candidate_grading(candidate_id: uuid.UUID) -> None:
    """
    Background worker task to trigger Grader Agent, parse report, and transition Candidate status.
    """
    logger.info(f"Starting background grading for candidate_id: {candidate_id}")
    
    async with async_session_factory() as session:
        # Fetch Candidate
        candidate_res = await session.execute(select(Candidate).where(Candidate.id == candidate_id))
        candidate = candidate_res.scalar_one_or_none()
        
        if not candidate:
            logger.error(f"Candidate {candidate_id} not found in database.")
            return

        # Fetch Interview
        interview_res = await session.execute(select(Interview).where(Interview.id == candidate.interview_id))
        interview = interview_res.scalar_one_or_none()
        
        # Fetch Goals
        goals_res = await session.execute(select(Goal).where(Goal.interview_id == candidate.interview_id))
        goals = goals_res.scalars().all()
        
        # Fetch Transcripts for this candidate
        transcripts_res = await session.execute(
            select(Transcript)
            .where(Transcript.candidate_id == candidate_id)
            .order_by(Transcript.created_at.asc())
        )
        transcripts = transcripts_res.scalars().all()
        
        try:
            # Build Payload
            payload = {
                "job_context": {
                    "job_name": interview.job_name,
                    "job_description": interview.job_description,
                },
                "plan_meta": {
                    "difficulty": interview.difficulty,
                    # We might not have communication_weight on interview model directly yet, default to 0.5
                    "communication_weight": getattr(interview, 'communication_weight', 0.5) 
                },
                "goals": []
            }
            
            for g in goals:
                goal_interactions = []
                for t in transcripts:
                    if t.goal_id == g.id:
                        goal_interactions.append({
                            "turn_id": str(t.id),
                            "role": t.role,
                            "content": t.content
                        })
                
                payload["goals"].append({
                    "goal_id": str(g.id),
                    "topic": g.topic,
                    "goal": g.goal,
                    "passing_criteria": [{"id": str(i), "criteria": c} for i, c in enumerate(g.passing_criteria)] if g.passing_criteria else [],
                    "wrong_answer_signals": [{"id": str(i), "signal": s} for i, s in enumerate(g.wrong_answer_signals)] if g.wrong_answer_signals else [],
                    "pushback_triggers": g.pushback_triggers if g.pushback_triggers else [],
                    "grounding_theory": g.grounding_theory or "",
                    "weight": g.weight or 1.0,
                    "gating": False,
                    "interaction_history": goal_interactions
                })

            # Call Agent
            logger.info("Payload built. Sending to Grader Agent.")
            agent_response = await request_grading_from_agent(payload)
            
            logger.info("Grader Agent response received. Saving report.")
            
            # Save Report
            report = CandidateReport(
                candidate_id=candidate.id,
                overall_confidence=agent_response.get("final_report", {}).get("confidence_level", "medium"),
                reasoning=agent_response.get("final_report", {}).get("executive_summary", ""),
                raw_report=agent_response.get("final_report", {}),
                grader_version="v1.0.0"
            )
            session.add(report)
            
            # Update Candidate Status
            candidate.status = "finished"
            candidate.composite_score = agent_response.get("overall_score")
            candidate.recommendation = agent_response.get("recommendation")
            
            await session.commit()
            logger.info(f"Successfully finished grading candidate {candidate_id}")
            
        except Exception as e:
            logger.error(f"Error during candidate grading for {candidate_id}: {e}", exc_info=True)
            await session.rollback()
