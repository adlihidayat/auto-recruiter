"""
What: Asynchronous Background Plan Generation Service.
Why: Orchestrates the background execution flow when a new interview is created.
Boundaries: Connects database entities to agent HTTP client; does not run inside the HTTP request loop.
"""

import logging
import uuid
from sqlalchemy import select
from app.core.db import async_session_factory
from app.models.interview import Interview
from app.models.goal import Goal
from app.models.job import Job
from app.services.agent_client import request_question_suite_from_agent

logger = logging.getLogger("plan-service")

async def process_interview_plan_generation(interview_id: uuid.UUID) -> None:
    """
    Background worker task to trigger Question-Maker Agent, parse generated questions, save Goal entities, and transition Interview status.
    
    Args:
        interview_id: The UUID of the interview entity.
    """
    logger.info(f"Starting background plan generation for interview_id: {interview_id}")
    
    async with async_session_factory() as session:
        # 1. Fetch Interview and Job entity
        interview_res = await session.execute(select(Interview).where(Interview.id == interview_id))
        interview = interview_res.scalar_one_or_none()
        
        job_res = await session.execute(
            select(Job).where(
                Job.job_type == "generate_plan",
                Job.payload["interview_id"].as_string() == str(interview_id)
            )
        )
        job = job_res.scalar_one_or_none()
        
        if not interview:
            logger.error(f"Interview {interview_id} not found in database.")
            return

        if job:
            job.status = "processing"
            job.attempts += 1
            await session.commit()

        try:
            # 2. Build payload for Agent Service HTTP call
            agent_payload = {
                "job_name": interview.job_name,
                "job_description": interview.job_description,
                "difficulty": interview.difficulty,
                "num_goals": interview.num_goals,
                "total_duration_minutes": interview.total_duration_minutes,
            }
            
            # 3. Call Agent Service over HTTP
            agent_response = await request_question_suite_from_agent(agent_payload)
            questions = agent_response.get("questions", [])
            
            logger.info(f"Agent Service returned {len(questions)} questions for interview_id: {interview_id}")
            
            # 4. Save Goal entities into PostgreSQL with clean sequential goal_refs (g_01, g_02, ...)
            for idx, q_data in enumerate(questions):
                goal_ref = f"g_{idx + 1:02d}"
                
                goal_entity = Goal(
                    goal_ref=goal_ref,
                    interview_id=interview.id,
                    topic=q_data.get("topic", "Technical Evaluation"),
                    goal=q_data.get("goal", ""),
                    suggested_opening=q_data.get("suggested_opening"),
                    passing_criteria=q_data.get("passing_criteria", []),
                    pushback_triggers=q_data.get("pushback_triggers", []),
                    wrong_answer_signals=q_data.get("wrong_answer_signals", []),
                    grounding_theory=q_data.get("grounding_theory"),
                    references=q_data.get("references", []),
                    weight=1.0,
                    gating=False
                )
                session.add(goal_entity)
                
            # 5. Transition Job status to 'done'
            if job:
                job.status = "done"
                
            await session.commit()
            logger.info(f"✅ Successfully completed plan generation for interview_id: {interview_id}.")
            
            # TODO: Future Action Item - Generate candidate LiveKit meeting room tokens & send email invitations
            
        except Exception as exc:
            logger.error(f"❌ Failed plan generation for interview_id: {interview_id}: {exc}", exc_info=True)
            await session.rollback()
            raise exc
