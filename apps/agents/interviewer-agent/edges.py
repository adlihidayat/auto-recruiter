"""
What: Defines conditional routing functions for the Interviewer Agent LangGraph.
Why: Manages the 3-strike self-correction loop when schema validation errors occur.
Boundaries: Does not contain prompt templates, LLM client logic, or state definitions.
"""

from typing import Literal
from .state import InterviewerState

def routeTurnDecisionOrRetry(current_state: InterviewerState) -> Literal["__end__", "decideNextConversationalTurn"]:
    """
    Evaluates whether the node completed successfully or requires a self-correction retry attempt.
    
    Args:
        current_state: The state updated by the decision node.
        
    Returns:
        The target node name to route to, or '__end__' if successful.
    """
    validation_error = current_state.get("last_error")
    current_retry_count = current_state.get("retry_count", 0)
    
    if validation_error:
        if current_retry_count >= 3:
            raise RuntimeError(
                f"Failed to generate a valid InterviewerDecision after 3 consecutive attempts. Last error: {validation_error}"
            )
        return "decideNextConversationalTurn"
        
    return "__end__"
