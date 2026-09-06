"""
What: HTTP client for communicating with the backend.
Why: Isolates backend API calls from the rest of the worker logic.
Boundaries: Only performs HTTP requests and returns raw or parsed data. Does not handle business logic.
"""

import httpx
from src.worker.core.config import settings
from src.worker.session.schemas import FinishGoalPayload

class BackendClient:
    """
    Client for interacting with the backend API.
    """
    def __init__(self):
        self.base_url = settings.backend_url
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def save_goal_transcripts(self, candidate_id: str, goal_ref: str, transcripts: list[dict]) -> None:
        """
        Sends the transcripts of a completed goal to the backend incrementally.
        
        Args:
            candidate_id (str): The unique identifier of the candidate.
            goal_ref (str): The reference of the goal (e.g., g_01).
            transcripts (list[dict]): The transcript data to submit.
        """
        endpoint = f"/api/candidates/{candidate_id}/goals/{goal_ref}/transcripts"
        response = await self.client.post(endpoint, json=transcripts)
        response.raise_for_status()

    async def finish_interview(self, candidate_id: str) -> None:
        """
        Finalizes the session and triggers the grader agent in the background.
        
        Args:
            candidate_id (str): The unique identifier of the candidate.
        """
        endpoint = f"/api/candidates/{candidate_id}/finish"
        response = await self.client.post(endpoint, json={"transcripts": []})
        response.raise_for_status()

    async def close(self):
        """
        Closes the underlying HTTP client.
        """
        await self.client.aclose()
