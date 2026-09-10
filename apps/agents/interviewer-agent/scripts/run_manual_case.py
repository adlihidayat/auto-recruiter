"""
What: CLI script to manually execute the Interviewer Agent with a single, highly customizable test case.
Why: Allows developers to quickly iterate on prompts and test specific edge cases, with output traceable in LangSmith.
Boundaries: Used purely for local testing, prompt tuning, and debugging. Not called in production.
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
NextGoalModel = interviewer_state_module.NextGoal

# ==============================================================================
# MANUAL TEST CASE CONFIGURATION
# Edit this dictionary to test specific conversational scenarios and debug outputs.
# ==============================================================================
MANUAL_TEST_CASE = {
    "job_name": "Mid-level Fullstack React/Node Developer",
    
    "goal": GoalModel(**{
        "goal_id": "g_02",
        "goal": "Evaluate whether candidate can diagnose and resolve real PostgreSQL performance problems.",
        "topic": "Database Performance Optimization",
        "suggested_opening": "Walk me through the specific changes you made that reduced DB latency by 60%.",
        "passing_criteria": [
            "Mentions query profiling, index usage, and EXPLAIN ANALYZE.",
            "Explains trade-offs of the solution."
        ],
        "pushback_triggers": [
            {
                "trigger": "just added indexes without profiling",
                "severity": "critical",
                "pushback_type": "concrete"
            }
        ],
        "wrong_answer_signals": [
            "scaling up the server as first resort"
        ],
        "interview_time_in_minute": 15
    }),
    
    "next_goal": NextGoalModel(**{
        "goal_id": "g_03",
        "topic": "JavaScript Event Loop",
        "suggested_opening": "How do non-blocking microtasks work under high event loop load?"
    }),
    
    "goal_history": [
        {
            "role": "interviewer",
            "content": "Walk me through the specific changes you made that reduced DB latency by 60% at your last role."
        }
    ],
    
    "prior_goals_summary": [
        {
            "goal_id": "g_01",
            "topic": "System Architecture",
            "covered": True,
            "score_hint": "strong"
        }
    ],
    
    "latest_candidate_transcript": "The database was lagging so I just added some indexes to the main tables and it fixed the latency issue.",
    
    "turn_count_this_goal": 1,
    "time_elapsed_seconds_this_goal": 45,
    "global_time_elapsed_seconds": 320,
    
    "retry_count": 0,
    "last_error": None
}
# ==============================================================================


def executeManualTestCase() -> None:
    """
    Executes a manual invocation of the interviewer agent with the configured test case and prints results.
    """
    print("=" * 60)
    print("RUNNING INTERVIEWER AGENT: MANUAL TEST CASE")
    print("=" * 60)
    print(f"Job Name: {MANUAL_TEST_CASE.get('job_name')}")
    print(f"Active Goal: {MANUAL_TEST_CASE.get('goal').topic}")
    print(f"Candidate Transcript: '{MANUAL_TEST_CASE.get('latest_candidate_transcript')}'")
    print("-" * 60)
    print("Invoking graph...\n")
    
    try:
        # We stream the events to get step-by-step visibility
        for graph_event in compiled_interviewer_graph.stream(MANUAL_TEST_CASE, stream_mode="updates"):
            for active_node_name, state_update in graph_event.items():
                print(f"--- Finished Node: {active_node_name} ---")
                
                turn_decision = state_update.get("decision")
                if turn_decision:
                    print(f"\n[DECISION OUTPUT]")
                    print(f"Action:                  {turn_decision.action}")
                    print(f"Message to Candidate:    '{turn_decision.message_to_candidate}'")
                    print(f"Progression Override:    {turn_decision.progression_override}")
                    print(f"Trigger Matched:         {turn_decision.trigger_matched}")
                    print(f"Flag for Human Review:   {turn_decision.flag_for_human_review}")
                    
        print("\n" + "=" * 60)
        print("EXECUTION COMPLETE.")
        print("Check LangSmith for detailed tracing and prompt token usage.")
        print("=" * 60)
            
    except Exception as execution_error:
        print(f"\n❌ Execution failed: {execution_error}")

if __name__ == "__main__":
    executeManualTestCase()
