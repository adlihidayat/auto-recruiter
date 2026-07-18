import os
import sys
from dotenv import load_dotenv

load_dotenv("../.env")
sys.path.append("/home/adli/Documents/auto-recruiter")
sys.path.append("/home/adli/Documents/auto-recruiter/apps/agents")

import importlib
retriever_module = importlib.import_module("question-maker-agent.nodes.retriever")
state_module = importlib.import_module("question-maker-agent.state")

retriever_generator_subgraph = retriever_module.retriever_generator_subgraph
InterviewGoal = state_module.InterviewGoal

def run_simulation():
    goal = InterviewGoal(
        goal_id="sim_123",
        topic="Python Asyncio",
        goal="Evaluate candidate's understanding of event loops and coroutines in Python.",
        interview_time_in_minute=10,
        need_grounding=True
    )

    initial_state = {
        "goal": goal,
        "search_count": 0,
        "messages": [],
        "grounding_theories": []
    }

    print(f"Starting simulation for topic: {goal.topic}")
    print("-" * 50)

    # Use the compiled graph's .stream() method to see intermediate steps
    for step_output in retriever_generator_subgraph.stream(initial_state):
        for node_name, state_update in step_output.items():
            print(f"\n[Node Execution: {node_name}]")
            
            if "messages" in state_update:
                last_message = state_update["messages"][-1]
                print(f"Message Role: {last_message.type}")
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    print(f"Tool Calls: {last_message.tool_calls}")
                elif last_message.content:
                    # Truncate content for readability
                    content = last_message.content
                    print(f"Content: {content[:200]}..." if len(content) > 200 else f"Content: {content}")
            
            if "search_count" in state_update:
                print(f"Search Count updated to: {state_update['search_count']}")
                
            if "grounding_theories" in state_update:
                theories = state_update["grounding_theories"]
                for t in theories:
                    print("\n>>> FINAL GROUNDING THEORY GENERATED <<<")
                    print(f"Theory length: {len(t.theory)} chars")
                    print(f"References: {[ref.url for ref in t.references]}")

    print("\n" + "=" * 50)
    print("Simulation Complete.")

if __name__ == "__main__":
    run_simulation()
