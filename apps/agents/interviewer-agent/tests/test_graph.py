"""
What: Pytest test suite for the Interviewer Agent graph state schemas and topology.
Why: Ensures state models validate correctly and the LangGraph compiles without errors.
Boundaries: Does not mock LLM network calls or test live server endpoints.
"""

import pytest
from ..graph import graph
from ..state import InterviewerState, Goal

def test_graph_compiles() -> None:
    """
    Verifies that the StateGraph compiles successfully and registers the decision node.
    """
    assert graph is not None
    assert "decideNextConversationalTurn" in graph.nodes

def test_state_schema_validation() -> None:
    """
    Verifies that the Goal Pydantic model correctly parses input dictionaries.
    """
    sample_goal_payload = {
        "goal_id": "g_02",
        "goal": "Test goal description",
        "topic": "Database Optimization",
        "suggested_opening": "Hello, let's discuss DBs.",
        "passing_criteria": ["Mentions indexing"],
        "pushback_triggers": [
            {"trigger": "No profiling", "severity": "high", "pushback_type": "concrete"}
        ],
        "wrong_answer_signals": ["Reboot server"],
        "interview_time_in_minute": 15
    }
    
    parsed_goal = Goal(**sample_goal_payload)
    assert parsed_goal.goal_id == "g_02"
    assert parsed_goal.topic == "Database Optimization"
