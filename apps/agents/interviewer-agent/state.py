"""
What: Defines the Pydantic data models and LangGraph TypedDict state for the Interviewer Agent.
Why: Centralizes schema definitions for input context, execution state, and structured decisions.
Boundaries: Does not contain LLM prompts, graph wiring, or decision execution logic.
"""

from typing import TypedDict, List, Optional, Literal
from pydantic import BaseModel, Field

class PushbackTrigger(BaseModel):
    """
    Defines a specific condition that requires the interviewer to push back on the candidate.
    """
    trigger: str = Field(description="Description of the candidate response pattern that triggers pushback.")
    severity: str = Field(description="Severity level of the triggered issue (e.g. 'critical', 'warning').")
    pushback_type: str = Field(description="Category of pushback to apply (e.g. 'concrete', 'conceptual').")

class Goal(BaseModel):
    """
    Represents the active evaluation goal assigned for the current phase of the interview.
    """
    goal_id: str = Field(description="Unique identifier for the goal.")
    goal: str = Field(description="Full text description of the target skill or evaluation goal.")
    topic: str = Field(description="High-level topic area for the goal.")
    suggested_opening: str = Field(description="Recommended opening line to introduce the goal.")
    passing_criteria: List[str] = Field(description="Criteria indicating satisfactory understanding.")
    pushback_triggers: List[PushbackTrigger] = Field(description="Triggers that mandate a pushback response.")
    wrong_answer_signals: List[str] = Field(description="Red flag responses or misconceptions.")
    interview_time_in_minute: int = Field(description="Allocated duration in minutes for this goal.")

class NextGoal(BaseModel):
    """
    Represents brief metadata for the upcoming goal to assist in transition planning.
    """
    goal_id: str = Field(description="Unique identifier for the next goal.")
    topic: str = Field(description="High-level topic area for the next goal.")
    suggested_opening: str = Field(description="Recommended opening line for the next topic.")

class GoalHistoryItem(BaseModel):
    """
    Represents a single conversational turn in the current goal's transcript history.
    """
    role: Literal["interviewer", "candidate"] = Field(description="Speaker role for this transcript turn.")
    content: str = Field(description="Spoken text content of the turn.")

class PriorGoalSummary(BaseModel):
    """
    Summary of previously completed goals within the current session.
    """
    goal_id: str = Field(description="Unique identifier for the completed goal.")
    topic: str = Field(description="Topic area of the completed goal.")
    covered: bool = Field(description="Whether the goal was sufficiently covered.")
    score_hint: str = Field(description="Advisory evaluation hint from prior goal coverage.")

class InterviewerDecision(BaseModel):
    """
    Structured output schema returned by the LLM for every conversational turn.
    """
    action: Literal["advance", "pushback", "clarify", "next_question", "stop_interview"] = Field(
        description="The target action to perform for this turn."
    )
    message_to_candidate: str = Field(
        description="The exact spoken text to deliver to the candidate."
    )
    reasoning: str = Field(
        description="Internal justification for the decision, never shown to the candidate."
    )
    trigger_matched: Optional[str] = Field(
        default=None, description="Trigger ID matched from goal.pushback_triggers, if applicable."
    )
    flag_for_human_review: bool = Field(
        default=False, description="Flag indicating potential prompt injection, distress, or abuse."
    )

class InterviewerState(TypedDict):
    """
    LangGraph execution state containing turn inputs, execution metrics, and decision outputs.
    """
    goal: Goal
    next_goal: Optional[NextGoal]
    goal_history: List[GoalHistoryItem]
    prior_goals_summary: List[PriorGoalSummary]
    latest_candidate_transcript: str
    turn_count_this_goal: int
    time_elapsed_seconds_this_goal: int
    global_time_elapsed_seconds: int
    
    # Retry state for self-correction
    retry_count: int
    last_error: Optional[str]
    
    # Target output
    decision: Optional[InterviewerDecision]
