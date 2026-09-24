import asyncio
import sys
import os
import uuid
from datetime import datetime, UTC, timedelta

# Ensure src/ is in the path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from sqlalchemy import select
from app.core.db import async_session_factory
from app.models.interview import Interview
from app.models.goal import Goal
from app.models.candidate import Candidate
from app.models.transcript import Transcript
from app.services.grader_service import process_candidate_grading

async def run():
    async with async_session_factory() as session:
        # Find an interview that actually has goals
        res = await session.execute(select(Interview))
        interviews = res.scalars().all()
        
        interview = None
        goals = []
        for inv in interviews:
            goals_res = await session.execute(select(Goal).where(Goal.interview_id == inv.id))
            g = goals_res.scalars().all()
            if g:
                interview = inv
                goals = g
                break
        
        if not interview:
            print("No interview with goals found. Please run seed scripts first.")
            return

        print(f"Using Interview: {interview.job_name} ({interview.id})")
        print(f"Found {len(goals)} goals.")

        # Create a new candidate
        candidate = Candidate(
            interview_id=interview.id,
            first_name="Jane",
            last_name="Doe_AgentTest",
            email=f"jane.doe.{uuid.uuid4().hex[:6]}@example.com",
            status="on-progress", # Will be moved to finished by grader
        )
        session.add(candidate)
        await session.flush()
        print(f"Created Candidate: {candidate.first_name} {candidate.last_name} ({candidate.id})")

        # Create some transcripts for each goal
        now = datetime.now(UTC) - timedelta(minutes=30)
        
        for idx, goal in enumerate(goals):
            t_q = Transcript(
                candidate_id=candidate.id,
                goal_id=goal.id,
                role="interviewer",
                content=f"Let's discuss {goal.topic}. What are your thoughts?",
                action="advance" if idx > 0 else "evaluate_goal",
                created_at=now + timedelta(minutes=idx*10)
            )
            t_a = Transcript(
                candidate_id=candidate.id,
                goal_id=goal.id,
                role="candidate",
                content=f"Here is a very detailed and excellent answer about {goal.topic} which perfectly addresses all the passing criteria. I would use advanced techniques and ensure all edge cases are handled.",
                created_at=now + timedelta(minutes=idx*10, seconds=45)
            )
            session.add_all([t_q, t_a])
            
        await session.commit()
        print(f"Added transcripts. Firing grader agent for Candidate ID: {candidate.id}")
        
    # Now run the grader outside the transaction
    try:
        await process_candidate_grading(candidate.id)
        print("Grading completed successfully!")
    except Exception as e:
        print(f"Error during grading: {e}")

if __name__ == "__main__":
    asyncio.run(run())
