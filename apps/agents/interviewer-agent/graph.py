"""
What: Constructs and compiles the LangGraph topology for the Interviewer Agent.
Why: Wires the decision node and retry routing edges into an executable state machine.
Boundaries: Does not instantiate server endpoints, database connections, or audio streams.
"""

from langgraph.graph import StateGraph, START, END

from .state import InterviewerState
from .nodes.decide import decideNextConversationalTurn
from .edges import routeTurnDecisionOrRetry

# 1. Initialize state graph builder
graph_builder = StateGraph(InterviewerState)

# 2. Register execution nodes
graph_builder.add_node("decideNextConversationalTurn", decideNextConversationalTurn)

# 3. Configure flow edges
graph_builder.add_edge(START, "decideNextConversationalTurn")
graph_builder.add_conditional_edges(
    "decideNextConversationalTurn",
    routeTurnDecisionOrRetry,
    {
        "__end__": END,
        "decideNextConversationalTurn": "decideNextConversationalTurn"
    }
)

# 4. Export compiled graph instance
graph = graph_builder.compile()
