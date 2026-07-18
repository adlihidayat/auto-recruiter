"""
What: Implements the Retriever Generator Subgraph (ReAct loop) for gathering technical grounding theories.
Why: Ensures generated questions are grounded in factual, domain-specific information retrieved via web search.
Boundaries: Restricted to searching via Tavily and formatting theories. Does not generate final interview questions.
"""

import operator
from typing import Annotated, Dict, Any, List, Literal, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, BaseMessage
from langchain_community.tools.tavily_search import TavilySearchResults

from apps.agents.shared.clients import gemini_flash_lite
from ..state import InterviewGoal, GroundingTheory, ReferenceSource
from ..prompts.retriever_prompt import RETRIEVER_SYSTEM_INSTRUCTION, FORCED_GENERATION_SYSTEM_INSTRUCTION

# --- Tools & Schemas ---

tavily_tool = TavilySearchResults(max_results=5)

class FinalGroundingTheory(BaseModel):
    """Call this tool to submit the final grounding theory once sufficient information is gathered."""
    theory: str = Field(description="The complete grounding theory text generated from web search.")
    references: List[ReferenceSource] = Field(default_factory=list, description="Verified sources for this theory.")

# --- State ---

class RetrieverState(TypedDict):
    goal: InterviewGoal
    messages: Annotated[list, add_messages]
    search_count: int
    grounding_theories: List[GroundingTheory]  # Will be merged back into parent state

# --- Nodes ---

def brain_node(state: RetrieverState) -> Dict[str, Any]:
    """
    Executes the primary ReAct LLM to analyze the goal and generate search queries or finalize the theory.
    """
    goal = state["goal"]
    messages = state.get("messages", [])
    
    search_count = state.get("search_count", 0)
    current_round = search_count + 1
    rounds_remaining = 3 - current_round
    rounds_remaining_note = f"You have {rounds_remaining} search rounds remaining after this one." if rounds_remaining > 0 else "This is your LAST search round. If you don't find it now, you won't."
    
    sys_msg = SystemMessage(content=RETRIEVER_SYSTEM_INSTRUCTION.format(
        goal=goal.goal, 
        topic=goal.topic,
        current_round=current_round,
        rounds_remaining_note=rounds_remaining_note
    ))
    
    if not messages:
        messages = [sys_msg, HumanMessage(content="Begin research for this goal.")]
    else:
        if messages and isinstance(messages[0], SystemMessage):
            messages[0] = sys_msg
        else:
            messages.insert(0, sys_msg)
        
        # Ensure there's a HumanMessage to satisfy Gemini's 'contents are required' error
        has_human = any(isinstance(m, HumanMessage) for m in messages)
        if not has_human:
            messages.insert(1, HumanMessage(content="Begin research for this goal."))
        
    llm_with_tools = gemini_flash_lite.bind_tools([tavily_tool, FinalGroundingTheory])
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}

def tool_node(state: RetrieverState) -> Dict[str, Any]:
    """
    Executes Tavily search queries requested by the brain_node and increments the search counter.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    tool_responses = []
    # Execute tools
    for tool_call in last_message.tool_calls:
        if tool_call["name"] == "tavily_search_results_json":
            result = tavily_tool.invoke(tool_call["args"])
            tool_responses.append(ToolMessage(
                tool_call_id=tool_call["id"],
                name=tool_call["name"],
                content=str(result)
            ))
            
    # Increment search count
    return {
        "messages": tool_responses, 
        "search_count": state.get("search_count", 0) + 1
    }

def forced_generation_node(state: RetrieverState) -> Dict[str, Any]:
    """
    Deterministically generates the final GroundingTheory without tools, used as a fallback to break loops.
    """
    goal = state["goal"]
    messages = state["messages"]
    
    # We remove previous system messages and inject the forced generation one
    # Or just append a new instruction
    sys_msg = SystemMessage(content=FORCED_GENERATION_SYSTEM_INSTRUCTION.format(goal=goal.goal, topic=goal.topic))
    
    # Use structured output directly for forced generation
    structured_llm = gemini_flash_lite.with_structured_output(FinalGroundingTheory)
    
    # We pass the sys_msg and the tool responses (history)
    response = structured_llm.invoke([sys_msg] + messages[1:])
    
    final_theory = GroundingTheory(
        goal_id=goal.goal_id,
        theory=response.theory,
        references=response.references
    )
    
    # We return grounding_theories so it merges back to parent
    return {"grounding_theories": [final_theory]}

# --- Routing ---

def route_brain(state: RetrieverState) -> Literal["tool_node", "END", "forced_generation_node"]:
    """
    Evaluates the LLM's response to route to tool execution, termination, or forced fallback.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the model called FinalGroundingTheory, we extract and end
    if last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            if tool_call["name"] == "FinalGroundingTheory":
                return "END"
        return "tool_node"
        
    # If it didn't call any tools and didn't call FinalGroundingTheory, we force generation
    return "forced_generation_node"

def route_tools(state: RetrieverState) -> Literal["brain_node", "forced_generation_node"]:
    """
    Routes back to the brain unless the maximum allowed search depth (3 loops) has been reached.
    """
    if state.get("search_count", 0) >= 3:
        return "forced_generation_node"
    return "brain_node"

# --- Edge hook for extracting FinalGroundingTheory ---

def extract_final_theory(state: RetrieverState) -> Dict[str, Any]:
    """Helper node that runs before END to parse the FinalGroundingTheory tool call if the brain called it."""
    messages = state["messages"]
    last_message = messages[-1]
    
    if last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            if tool_call["name"] == "FinalGroundingTheory":
                args = tool_call["args"]
                theory = GroundingTheory(
                    goal_id=state["goal"].goal_id,
                    theory=args.get("theory", ""),
                    references=args.get("references", [])
                )
                return {"grounding_theories": [theory]}
    return {}

# --- Sub-graph Definition ---

retriever_workflow = StateGraph(RetrieverState)

retriever_workflow.add_node("brain_node", brain_node)
retriever_workflow.add_node("tool_node", tool_node)
retriever_workflow.add_node("forced_generation_node", forced_generation_node)
retriever_workflow.add_node("extract_final_theory", extract_final_theory)

retriever_workflow.add_edge(START, "brain_node")

retriever_workflow.add_conditional_edges("brain_node", route_brain, {
    "tool_node": "tool_node",
    "END": "extract_final_theory",
    "forced_generation_node": "forced_generation_node"
})

retriever_workflow.add_conditional_edges("tool_node", route_tools, {
    "brain_node": "brain_node",
    "forced_generation_node": "forced_generation_node"
})

retriever_workflow.add_edge("forced_generation_node", END)
retriever_workflow.add_edge("extract_final_theory", END)

retriever_generator_subgraph = retriever_workflow.compile()
