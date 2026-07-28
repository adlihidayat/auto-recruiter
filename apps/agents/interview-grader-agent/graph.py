"""
What: Initializes and compiles the StateGraph for the interview grader agent.
Why: Serves as the central orchestrator wiring together the core analysis, conditional nodes (communication, citations), and final aggregation.
Boundaries: Does not implement node logic or define state schemas; delegates routing to edges.py.
"""
from langgraph.graph import StateGraph, END
from .state import GraderState
from .nodes import run_core_analysis, run_communication, run_citations, run_aggregation
from .edges import route_after_core, route_after_comm

def create_grader_graph() -> StateGraph:
    """
    Initializes and compiles the interview grader LangGraph.
    """
    workflow = StateGraph(GraderState)
    
    # Add all nodes
    workflow.add_node("core_analysis", run_core_analysis)
    workflow.add_node("communication", run_communication)
    workflow.add_node("citations", run_citations)
    workflow.add_node("aggregation", run_aggregation)
    
    # Set the entry point
    workflow.set_entry_point("core_analysis")
    
    # Routing after Core Analysis
    workflow.add_conditional_edges(
        "core_analysis",
        route_after_core
    )
    
    # Routing after Communication
    workflow.add_conditional_edges(
        "communication",
        route_after_comm
    )
    
    # Citations always goes to Aggregation
    workflow.add_edge("citations", "aggregation")
    
    # Aggregation is the final step
    workflow.add_edge("aggregation", END)
    
    return workflow.compile()
