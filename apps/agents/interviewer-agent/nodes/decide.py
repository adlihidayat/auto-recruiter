"""
What: Implements the decision node for evaluating candidate turns in the Interviewer Agent.
Why: Formats context payloads, invokes Gemini with structured output, and captures validation errors.
Boundaries: Does not manage graph edges, session storage, or audio TTS generation.
"""

from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from ..state import InterviewerState, InterviewerDecision
from ..prompts.system import INTERVIEWER_SYSTEM_PROMPT
from apps.agents.shared.clients import gemini_flash_lite

# Initialize structured output runnable using the shared rotating model client
structured_llm_client = gemini_flash_lite.with_structured_output(InterviewerDecision)

def decideNextConversationalTurn(current_state: InterviewerState) -> Dict[str, Any]:
    """
    Evaluates the current interview state and candidate transcript to select the next action and spoken response.
    
    Args:
        current_state: The current graph execution state containing active goals, history, and metrics.
        
    Returns:
        State update dictionary containing the decision output or validation error tracking.
    """
    attempt_count = current_state.get("retry_count", 0)
    active_goal = current_state.get("goal")
    
    # 1. Format system prompt with active goal context
    formatted_system_prompt = f"{INTERVIEWER_SYSTEM_PROMPT}\n\n=== ACTIVE GOAL ===\n{active_goal.model_dump_json(indent=2)}\n"
    
    next_goal = current_state.get("next_goal")
    if next_goal:
        formatted_system_prompt += f"\n=== NEXT GOAL ===\n{next_goal.model_dump_json(indent=2)}\n"
        
    conversation_messages = [SystemMessage(content=formatted_system_prompt)]
    
    # 2. Append turn history
    for history_item in current_state.get("goal_history", []):
        if history_item.role == "interviewer":
            conversation_messages.append(AIMessage(content=history_item.content))
        else:
            conversation_messages.append(HumanMessage(content=history_item.content))
            
    # 3. Format candidate input and execution metrics
    turn_context_summary = (
        f"Turn Count: {current_state.get('turn_count_this_goal')}\n"
        f"Time Elapsed This Goal: {current_state.get('time_elapsed_seconds_this_goal')}s\n"
        f"Global Time Elapsed: {current_state.get('global_time_elapsed_seconds')}s\n"
        f"LATEST CANDIDATE TRANSCRIPT: {current_state.get('latest_candidate_transcript')}"
    )
    
    previous_attempt_error = current_state.get("last_error")
    if previous_attempt_error:
        turn_context_summary += f"\n\nERROR ON PREVIOUS ATTEMPT: {previous_attempt_error}\nPlease correct your output schema."
        
    conversation_messages.append(HumanMessage(content=turn_context_summary))
    
    # 4. Invoke LLM and capture output or handle error state
    try:
        generated_decision: InterviewerDecision = structured_llm_client.invoke(conversation_messages)
        
        return {
            "last_error": None,
            "retry_count": attempt_count,
            "decision": generated_decision
        }
    except Exception as execution_error:
        return {
            "last_error": str(execution_error),
            "retry_count": attempt_count + 1
        }
