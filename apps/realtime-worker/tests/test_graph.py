"""
What: Standalone graph execution test script for Interviewer Agent.
Why: Verifies in-process invocation of the LangGraph interviewer-agent graph with mock state inputs.
Boundaries: Testing utility; isolated from LiveKit voice runtime.
"""

import sys
import os
import asyncio
import importlib

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
AGENTS_DIR = os.path.join(ROOT_DIR, "apps/agents")
INTERVIEWER_AGENT_DIR = os.path.join(AGENTS_DIR, "interviewer-agent")

for p in [ROOT_DIR, AGENTS_DIR, INTERVIEWER_AGENT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

async def main():
    interviewer_graph_module = importlib.import_module("interviewer-agent.graph")
    interviewer_graph = interviewer_graph_module.graph
    
    input_state = {
        "candidate_id": "test_id",
        "job_name": "Test Job",
        "job_description": "Test Description",
        "domain_hint": "Test",
        "resume_content": "Test",
        "difficulty": "medium",
        "num_goals": 3,
        "communication_weight": 0.5,
        "current_goal": {
            "goal_id": "goal_1",
            "concept_to_test": "test concept",
            "target_depth": 3,
            "status": "pending"
        },
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

if __name__ == "__main__":
    asyncio.run(main())
