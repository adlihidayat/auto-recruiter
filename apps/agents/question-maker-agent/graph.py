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
from .nodes.generator import generateQuestionItemFromGoal
from .nodes.validate import validateQuestionSuite

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
        # If no goals need grounding, skip directly to synchronizeRetrieverNodes
        return "synchronizeRetrieverNodes"
    return sends

def synchronizeRetrieverNodes(state: QuestionMakerState) -> Dict[str, Any]:
    """
    Synchronizes state after mapped retriever nodes finish execution.
    
    Args:
        state: The QuestionMakerState after retriever execution.
        
    Returns:
        An empty dictionary.
    """
    return {}

def routeToParallelGenerators(state: QuestionMakerState):
    """
    [3] Generator Routing (Map): Uses LangGraph Send to launch parallel generators
    for ALL goals, pairing them with their grounding theory if one exists.
    """
    sends = []
    goals = state.get("goals", [])
    theories = {t.goal_id: t for t in state.get("grounding_theories", [])}
    
    for goal in goals:
        sends.append(Send("generateQuestionItemFromGoal", {
            "goal": goal,
            "theory": theories.get(goal.goal_id)
        }))
        
    return sends

from .nodes.assemble import assemble_node

# --- Routing/Conditional Edges ---

def route_validation_results(state: QuestionMakerState):
    """
    Decides whether to route back to the Generator for revision or finalize the suite.
    """
    feedback = state.get("critic_feedback")
    if not feedback:
        return "assemble_node"
        
    has_failures = not feedback.get("is_valid", True)
    retry_counts = state.get("retry_counts", {})
    failed_goal_ids = feedback.get("failed_goal_ids", [])
    
    sends = []
    if has_failures:
        goals = {g.goal_id: g for g in state.get("goals", [])}
        theories = {t.goal_id: t for t in state.get("grounding_theories", [])}
        
        for goal_id in failed_goal_ids:
            if retry_counts.get(goal_id, 0) <= 2:
                goal_obj = goals.get(goal_id)
                if goal_obj:
                    feedback_for_goal = feedback.get("feedback_per_question", {}).get(goal_id)
                    
                    prev_question = None
                    for q in reversed(state.get("generated_questions", [])):
                        if q.goal_id == goal_id:
                            prev_question = q
                            break
                            
                    sends.append(Send("generateQuestionItemFromGoal", {
                        "goal": goal_obj,
                        "theory": theories.get(goal_id),
                        "critic_feedback": feedback_for_goal,
                        "previous_generation": prev_question
                    }))
    
    if sends:
        return sends
    
    return "assemble_node"


# --- Graph Construction ---

workflow = StateGraph(QuestionMakerState)

def retriever_wrapper(state: Any):
    result = retriever_generator_subgraph.invoke(state)
    return {"grounding_theories": result.get("grounding_theories", [])}

# Add Nodes
workflow.add_node("plan_node", plan_node)
workflow.add_node("retriever_generator_subgraph", retriever_wrapper)
workflow.add_node("synchronizeRetrieverNodes", synchronizeRetrieverNodes)
workflow.add_node("generateQuestionItemFromGoal", generateQuestionItemFromGoal)
workflow.add_node("validateQuestionSuite", validateQuestionSuite)
workflow.add_node("assemble_node", assemble_node)

# Set Entrypoint
workflow.add_edge(START, "plan_node")

# Define Flow
workflow.add_conditional_edges("plan_node", route_to_retriever, ["retriever_generator_subgraph", "synchronizeRetrieverNodes"])
workflow.add_edge("retriever_generator_subgraph", "synchronizeRetrieverNodes")
workflow.add_conditional_edges("synchronizeRetrieverNodes", routeToParallelGenerators, ["generateQuestionItemFromGoal"])
workflow.add_edge("generateQuestionItemFromGoal", "validateQuestionSuite")

# Add Conditional Routing
workflow.add_conditional_edges(
    "validateQuestionSuite",
    route_validation_results,
    {
        "generateQuestionItemFromGoal": "generateQuestionItemFromGoal",
        "assemble_node": "assemble_node"
    }
)

workflow.add_edge("assemble_node", END)

# Compile Graph
graph = workflow.compile()
