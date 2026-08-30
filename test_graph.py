import sys
import os
import asyncio
import importlib

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('apps/agents'))
from dotenv import load_dotenv
load_dotenv(".env")

async def main():
    interviewer_graph_module = importlib.import_module("interviewer-agent.graph")
    interviewer_graph = interviewer_graph_module.graph
    
    interviewer_state = importlib.import_module("interviewer-agent.state")
    Goal = interviewer_state.Goal
    
    goal_obj = Goal(
        goal_id="goal_1",
        goal="test concept",
        topic="test",
        suggested_opening="hi",
        passing_criteria=[],
        pushback_triggers=[],
        wrong_answer_signals=[],
        interview_time_in_minute=10
    )
    
    input_state = {
        "candidate_id": "test_id",
        "job_name": "Test Job",
        "job_description": "Test Description",
        "domain_hint": "Test",
        "resume_content": "Test",
        "difficulty": "medium",
        "num_goals": 3,
        "communication_weight": 0.5,
        "goal": goal_obj,
        "goal_history": [
            {"role": "interviewer", "content": "hello", "action": None, "reasoning": None},
            {"role": "candidate", "content": "hi"}
        ],
        "decision": None
    }
    
    try:
        print("Invoking graph...")
        result = await interviewer_graph.ainvoke(input_state)
        print(f"Success! Result: {result.get('decision')}")
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
