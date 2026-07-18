"""
What: Compiles the LangGraph StateGraph workflow for the Question-Maker Agent.
Why: Outlines the sequential and cyclical execution pipeline, from planning and retrieving to generating, validating, and revising.
Boundaries: Does not contain the actual LLM prompts, tool execution logic, or FastAPI endpoints.
"""

from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from .state import QuestionMakerState
from .nodes.planner import plan_node
from .nodes.retriever import retriever_generator_subgraph

def route_to_retriever(state: QuestionMakerState):
    """
    [2] Retriever Routing (Map): Uses LangGraph Send to launch parallel retriever sub-graphs 
    for each goal that requires grounding.
    """
    sends = []
    for goal in state.get("goals", []):
        if goal.need_grounding:
            sends.append(Send("retriever_generator_subgraph", {
                "goal": goal, 
                "messages": [], 
                "search_count": 0,
                "grounding_theories": []
            }))
            
    if not sends:
        # If no goals need grounding, skip directly to generator
        return "generate_node"
    return sends

def generate_node(state: QuestionMakerState) -> Dict[str, Any]:
    """
    [3] Generator: Generates raw question items from the context pack (strictly grounded to snippets).
    Uses: gemini-2.5-flash or gemini-2.5-pro (strict structured JSON, zero tools).
    """
    # TODO: Implement Generator node logic
    return {"generated_questions": []}

def consolidate_node(state: QuestionMakerState) -> Dict[str, Any]:
    """
    [4] Consolidation: Handles cross-question deduplication and difficulty balancing.
    Uses: Single model call.
    """
    # TODO: Implement Consolidation node logic
    return {"consolidated_questions": []}

def validate_node(state: QuestionMakerState) -> Dict[str, Any]:
    """
    [5] Validator/Critic: Evaluates generated questions against their source snippets (grounding check, rubric quality).
    Uses: gemini-2.5-flash-lite.
    """
    # TODO: Implement Validator/Critic node logic
    return {"critic_feedback": {}, "retry_counts": {}}

def assemble_node(state: QuestionMakerState) -> Dict[str, Any]:
    """
    [6/Final] Assemble: Structures final JSON output into the official QuestionSuite schema.
    Uses: Formatting only (no model call).
    """
    # TODO: Implement final formatting
    return {"final_suite": None}


# --- Routing/Conditional Edges ---

def route_validation_results(state: QuestionMakerState) -> Literal["generate_node", "assemble_node"]:
    """
    Decides whether to route back to the Generator for revision or finalize the suite.
    """
    feedback = state.get("critic_feedback")
    if not feedback:
        return "assemble_node"
        
    # Check if there are failures to fix
    has_failures = not feedback.get("is_valid", True)
    
    # Check if we have exceeded the retry budget
    # The rule specifies: "max 2 retries per item, then drop or flag for human review"
    retry_counts = state.get("retry_counts", {})
    all_retries_exhausted = all(count >= 2 for count in retry_counts.values()) if retry_counts else False
    
    if has_failures and not all_retries_exhausted:
        return "generate_node"
    
    return "assemble_node"


# --- Graph Construction ---

workflow = StateGraph(QuestionMakerState)

# Add Nodes
workflow.add_node("plan_node", plan_node)
workflow.add_node("retriever_generator_subgraph", retriever_generator_subgraph)
workflow.add_node("generate_node", generate_node)
workflow.add_node("consolidate_node", consolidate_node)
workflow.add_node("validate_node", validate_node)
workflow.add_node("assemble_node", assemble_node)

# Set Entrypoint
workflow.add_edge(START, "plan_node")

# Define Flow
workflow.add_conditional_edges("plan_node", route_to_retriever, ["retriever_generator_subgraph", "generate_node"])
workflow.add_edge("retriever_generator_subgraph", "generate_node")
workflow.add_edge("generate_node", "consolidate_node")
workflow.add_edge("consolidate_node", "validate_node")

# Add Conditional Routing
workflow.add_conditional_edges(
    "validate_node",
    route_validation_results,
    {
        "generate_node": "generate_node",
        "assemble_node": "assemble_node"
    }
)

workflow.add_edge("assemble_node", END)

# Compile Graph
graph = workflow.compile()
