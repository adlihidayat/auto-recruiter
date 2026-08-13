"""
What: Defines the conditional routing functions for the grader's LangGraph.
Why: Evaluates intermediate state to efficiently skip expensive LLM calls (e.g., bypassing communication if not required, or skipping citations if not borderline).
Boundaries: Only reads state to return node routing strings; does not mutate state or invoke LLMs.
"""
from .state import GraderState

from typing import List

def route_phase_1(state: GraderState) -> List[str]:
    """
    Determine which Phase 1 nodes to execute in parallel.
    Core Analysis and Injection Check always run.
    Communication runs conditionally based on plan_meta.
    """
    nodes = ["core_analysis", "injection_check"]
    
    plan_meta = state.get("plan_meta")
    
    if plan_meta:
        comm_weight = plan_meta.communication_weight if hasattr(plan_meta, 'communication_weight') else plan_meta.get("communication_weight", "low")
        if comm_weight != "low":
            nodes.append("communication")
            
    return nodes

def route_after_phase_1_join(state: GraderState) -> str:
    """
    Determine next step after Phase 1 parallel execution completes.
    Check if any goals need citations (score 4-6 or low/medium confidence) from core_analysis.
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
