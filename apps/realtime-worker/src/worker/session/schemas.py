"""
What: Defines the Pydantic data models for the Realtime Worker's session handling.
Why: Centralizes schema definitions for backend communication (like transcripts).
Boundaries: These schemas are specific to the worker's API contracts with the backend.
"""

from typing import List
from pydantic import BaseModel, Field

class TranscriptTurn(BaseModel):
    """
    Represents a single conversational turn to be submitted when a goal finishes.
    """
    goal_id: str = Field(description="Unique identifier for the goal.")
    role: str = Field(description="Role of the speaker (e.g., 'interviewer' or 'candidate').")
    content: str = Field(description="The spoken text content.")
    action: str | None = Field(default=None, description="The action determined by the agent, if applicable.")
    reasoning: str | None = Field(default=None, description="Internal reasoning for the decision, if applicable.")

class FinishGoalPayload(BaseModel):
    """
    Payload sent to the backend when a goal is finished.
    """
    transcripts: List[TranscriptTurn] = Field(description="List of transcript turns for the completed goal.")
