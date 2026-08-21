"""
Simulates the realtime worker sending the POST /api/candidates/{candidate_id}/finish signal with transcripts.
"""

import asyncio
import httpx
from sqlalchemy import select
import sys
import os

# Ensure src/ is in the path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from app.core.db import async_session_factory
from app.models.candidate import Candidate
from app.models.goal import Goal

async def simulate():
    print("Finding a candidate to finish...")
    async with async_session_factory() as session:
        result = await session.execute(
            select(Candidate).where(Candidate.status != "finished")
        )
        candidate = result.scalars().first()
        
        if not candidate:
            print("No unfinished candidate found. Run seed script first.")
            return
            
        print(f"Found Candidate: {candidate.id} ({candidate.first_name} {candidate.last_name})")
        
        # Get one of their goals to attach transcripts to
        goals_result = await session.execute(
            select(Goal).where(Goal.interview_id == candidate.interview_id)
        )
        goal = goals_result.scalars().first()
        
        if not goal:
            print("No goals found for candidate's interview.")
            return

        payload = {
            "transcripts": [
                {
                    "goal_id": str(goal.id),
                    "role": "interviewer",
                    "content": "Can you explain how you handle adverse selection?",
                    "action": "evaluate_goal",
                    "reasoning": "Starting goal"
                },
                {
                    "goal_id": str(goal.id),
                    "role": "candidate",
                    "content": "I use a depth-weighted micro-price to dynamically widen the spread.",
                }
            ]
        }
        
        print(f"Sending POST to /api/candidates/{candidate.id}/finish ...")
        
        async with httpx.AsyncClient() as client:
            # We don't have authentication on this endpoint right now according to the code comments
            try:
                response = await client.post(
                    f"http://127.0.0.1:8000/api/candidates/{candidate.id}/finish",
                    json=payload
                )
                print(f"Response status: {response.status_code}")
                print(f"Response body: {response.text}")
            except Exception as e:
                print(f"Error connecting to server: {e}")
                print("Make sure both backend and agents servers are running (e.g. via 'npm run dev' or 'uv run uvicorn')")

if __name__ == "__main__":
    asyncio.run(simulate())
