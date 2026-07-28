"""
What: Defines the conditional routing functions for the grader's LangGraph.
Why: Evaluates intermediate state to efficiently skip expensive LLM calls (e.g., bypassing communication if not required, or skipping citations if not borderline).
Boundaries: Only reads state to return node routing strings; does not mutate state or invoke LLMs.
"""
from .state import GraderState

def route_after_core(state: GraderState) -> str:
    """
    Determine next step after core analysis.
    If communication_weight is not 'low', run communication analysis.
    Otherwise, check if citations are needed.
    """
    plan_meta = state.get("plan_meta")
    
    # Safely handle if it's parsed as a Pydantic model vs dict vs not present
    if plan_meta:
        comm_weight = plan_meta.communication_weight if hasattr(plan_meta, 'communication_weight') else plan_meta.get("communication_weight", "low")
        if comm_weight != "low":
            return "communication"
            
    return route_after_comm(state)

def route_after_comm(state: GraderState) -> str:
    """
    Determine next step after communication (or skipped communication).
    Check if any goals need citations (score 4-6 or low/medium confidence).
    """
    core_analysis = state.get("core_analysis")
    if not core_analysis:
        return "aggregation"
        
    needs_citations = False
    
    # Handle if core_analysis is a Pydantic model or dict
    goals = core_analysis.goals if hasattr(core_analysis, 'goals') else core_analysis.get("goals", [])
    
    for goal in goals:
        # Pydantic vs dict accessor
        score = goal.score if hasattr(goal, 'score') else goal.get("score")
        confidence = goal.confidence if hasattr(goal, 'confidence') else goal.get("confidence")
        
        if score is not None and 4 <= score <= 6:
            needs_citations = True
            break
            
        if confidence in ["low", "medium"]:
            needs_citations = True
            break
            
    if needs_citations:
        return "citations"
        
    return "aggregation"
