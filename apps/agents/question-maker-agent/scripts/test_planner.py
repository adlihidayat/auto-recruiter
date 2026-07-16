"""
What: CLI tool to debug, test, and tune the Planner node.
Why: Runs the plan_node synchronously using mock data to inspect the generated InterviewGoals.
Boundaries: Does not expose production API endpoints or run the full web server.
"""

import os
import sys
import importlib

# Add workspace path and agent path to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

# Load modules dynamically to bypass dot-notation restrictions on directories with dashes
planner_module = importlib.import_module("question-maker-agent.nodes.planner")
plan_node = planner_module.plan_node

state_module = importlib.import_module("question-maker-agent.state")
QuestionMakerState = state_module.QuestionMakerState

# Sample Job Information for testing
MOCK_JOB_NAME = "Senior Backend Engineer (Python & PostgreSQL)"
MOCK_JOB_DESCRIPTION = """
We are looking for a Senior Backend Engineer to join our core team. In this role, you will design, build, and optimize high-throughput data processing systems.

Key Requirements:
- 5+ years of experience with Python (FastAPI, Asyncio)
- Expert-level understanding of database performance tuning, specifically PostgreSQL (indexing, query execution plans, connection pooling, deadlock resolution).
- Solid experience with Redis for caching and pub/sub.
- Proven track record of scaling RESTful APIs to handle millions of requests.
- Experience with background task workers like Celery.

No textbook trivia here please! We need someone who can jump into a production database that is pegging at 99% CPU, diagnose the bottleneck using EXPLAIN ANALYZE, and restructure queries or indexes to bring it down.
"""

def main():
    print("=" * 60)
    print("Testing the Question-Maker Agent: Planner Node (Updated)")
    print("=" * 60)
    
    # 1. Prepare input state
    state: QuestionMakerState = {
        "job_name": MOCK_JOB_NAME,
        "job_description": MOCK_JOB_DESCRIPTION,
        "difficulty": "infer", # Testing the inference engine!
        "num_goals": 3,
        "total_duration_minutes": 45,
        "goals": None,
        "research_brief": None,
        "context_pack": None,
        "generated_questions": None,
        "consolidated_questions": None,
        "critic_feedback": None,
        "retry_counts": None,
        "final_suite": None,
    }
    
    print(f"Inputs:\n  Job Name: {state['job_name']}\n  Difficulty: {state['difficulty']}")
    print(f"  Target Goals: {state['num_goals']}\n  Target Duration: {state['total_duration_minutes']} minutes\n")
    print("Calling plan_node via Gemini 3.1 Flash-Lite...")
    
    try:
        # 2. Invoke the plan node
        output = plan_node(state)
        
        goals = output.get("goals", [])
        resolved_difficulty = output.get("difficulty")
        
        print("\nSUCCESS! Execution Complete:")
        print(f"Resolved/Inferred Seniority Level: {resolved_difficulty.upper()}")
        print(f"Number of Goals Generated: {len(goals)}")
        print(f"Total Time Summed: {sum(g.interview_time_in_minute for g in goals)} minutes\n")
        
        for i, goal in enumerate(goals, 1):
            print(f"Goal #{i}:")
            print(f"  ID: {goal.goal_id}")
            print(f"  Topic: {goal.topic}")
            print(f"  Goal: {goal.goal}")
            print(f"  Allocated Time: {goal.interview_time_in_minute} minutes")
            print("-" * 40)
            
    except Exception as e:
        print(f"\nERROR during plan_node execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
