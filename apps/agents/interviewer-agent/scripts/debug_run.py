"""
What: CLI debug script to execute a local end-to-end simulation of the Interviewer Agent graph.
Why: Validates graph invocation, state updates, and LangSmith tracing without deploying services.
Boundaries: Used purely for local testing and debugging. Not called in production.
"""

import os
import sys
import importlib

# Resolve parent paths for monorepo imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env")))

interviewer_graph_module = importlib.import_module("interviewer-agent.graph")
interviewer_state_module = importlib.import_module("interviewer-agent.state")

compiled_interviewer_graph = interviewer_graph_module.graph
GoalModel = interviewer_state_module.Goal

def debugInterviewerWorkflow() -> None:
    """
    Executes a test invocation of the interviewer agent with mock state and prints results.
    """
    mock_input_state = {
        "goal": GoalModel(**{
            "goal_id": "g_02",
            "goal": "Evaluate whether candidate can diagnose and resolve real PostgreSQL performance problems.",
            "topic": "Database Performance Optimization",
            "suggested_opening": "Walk me through the specific changes you made that reduced DB latency by 60%.",
            "passing_criteria": ["Mentions query profiling, index usage, and EXPLAIN ANALYZE."],
            "pushback_triggers": [
                {"trigger": "just added indexes without profiling", "severity": "critical", "pushback_type": "concrete"}
            ],
            "wrong_answer_signals": ["scaling up the server as first resort"],
            "interview_time_in_minute": 15
        }),
        "next_goal": None,
        "goal_history": [],
        "prior_goals_summary": [],
        "latest_candidate_transcript": "I noticed the database was slow so I just added some indexes and it fixed the problem.",
        "turn_count_this_goal": 1,
        "time_elapsed_seconds_this_goal": 30,
        "global_time_elapsed_seconds": 300,
        "retry_count": 0,
        "last_error": None
    }

    print("Invoking Interviewer Agent debug workflow...")
    
    try:
        for graph_event in compiled_interviewer_graph.stream(mock_input_state, stream_mode="updates"):
            for active_node_name, state_update in graph_event.items():
                print(f"--- Finished Node: {active_node_name} ---")
                
                turn_decision = state_update.get("decision")
                if turn_decision:
                    print(f"Action: {turn_decision.action}")
                    print(f"Message: {turn_decision.message_to_candidate}")
                    print(f"Reasoning: {turn_decision.reasoning}")
                    print(f"Trigger Matched: {turn_decision.trigger_matched}")
                    
        print("\n=== DEBUG WORKFLOW COMPLETE ===")
            
    except Exception as execution_error:
        print(f"Debug workflow failed: {execution_error}")

if __name__ == "__main__":
    debugInterviewerWorkflow()
