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

    async def finish_goal(self, candidate_id: str, payload: FinishGoalPayload) -> None:
        """
        Sends the transcripts of a completed goal to the backend.
        
        Args:
            candidate_id (str): The unique identifier of the candidate.
            payload (FinishGoalPayload): The transcript data to submit.
        """
        endpoint = f"/api/candidates/{candidate_id}/finish"
        response = await self.client.post(endpoint, json=payload.model_dump())
        response.raise_for_status()

    async def close(self):
        """
        Closes the underlying HTTP client.
        """
        await self.client.aclose()
