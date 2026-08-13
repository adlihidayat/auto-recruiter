"""
What: Initializes and compiles the StateGraph for the interview grader agent.
Why: Serves as the central orchestrator wiring together the core analysis, conditional nodes (communication, citations), and final aggregation.
Boundaries: Does not implement node logic or define state schemas; delegates routing to edges.py.
"""
from langgraph.graph import StateGraph, START, END
from typing import Dict, Any
from .state import GraderState
from .nodes import run_core_analysis, run_communication, run_injection_check, run_citations, run_aggregation
from .edges import route_phase_1, route_after_phase_1_join

def dummy_join(state: GraderState) -> Dict[str, Any]:
    """Dummy node to serve as a convergence point for Phase 1 parallel execution."""
    return {}

def create_grader_graph() -> StateGraph:
    """
    Initializes and compiles the interview grader LangGraph.
    """
    workflow = StateGraph(GraderState)
    
    # Add all nodes
    workflow.add_node("core_analysis", run_core_analysis)
    workflow.add_node("communication", run_communication)
    workflow.add_node("injection_check", run_injection_check)
    workflow.add_node("phase_1_join", dummy_join)
    workflow.add_node("citations", run_citations)
    workflow.add_node("aggregation", run_aggregation)
    
    # Phase 1 Parallel Dispatch
    workflow.add_conditional_edges(
        START,
        route_phase_1
    )
    
    # Phase 1 Convergence
    workflow.add_edge("core_analysis", "phase_1_join")
    workflow.add_edge("communication", "phase_1_join")
    workflow.add_edge("injection_check", "phase_1_join")
    
    # Routing after Phase 1 Convergence
    workflow.add_conditional_edges(
        "phase_1_join",
        route_after_phase_1_join
    )
    
    # Citations always goes to Aggregation
    workflow.add_edge("citations", "aggregation")
    
    # Aggregation is the final step
    workflow.add_edge("aggregation", END)
    
    return workflow.compile()
