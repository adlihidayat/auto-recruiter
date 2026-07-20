"""
What: Executes a full end-to-end local test of the Question-Maker Agent graph.
Why: Used to verify that all nodes (Planner, Retriever, Generator, Validator, Assemble) correctly sequence data and handle fallbacks without needing to deploy the service.
Boundaries: This is a standalone test script. It does not run as part of the core agent graph.
"""

import os
import sys
import json

# Setup paths for monorepo structure
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env")))

import importlib
graph_module = importlib.import_module("question-maker-agent.graph")
graph = graph_module.graph

def test_workflow():
    inputs = {
        "job_name": "Senior Backend Engineer",
        "job_description": "We need a senior engineer who can design scalable microservices and write high-performance Go code. Strong understanding of gRPC and Kubernetes is required.",
        "difficulty": "senior",
        "num_goals": 1,
        "total_duration_minutes": 15
    }

    print("Invoking full Question-Maker workflow (Planner -> Retriever -> Generator -> Validator -> Assemble)...")
    
    final_suite = None
    try:
        # We will stream the events so we can see the graph traverse node by node
        for event in graph.stream(inputs, stream_mode="updates"):
            for node_name, state_update in event.items():
                print(f"--- Finished Node: {node_name} ---")
                
                # Print some useful state updates to observe progress
                if node_name == "plan_node":
                    goals = state_update.get("goals", [])
                    print(f"Planner generated {len(goals)} goals.")
                    for g in goals:
                        print(f"  - {g.topic} (Grounding: {g.need_grounding})")
                        
                elif node_name == "retriever_generator_subgraph":
                    theories = state_update.get("grounding_theories", [])
                    if theories:
                        print(f"Retrieved theory for goal: {theories[0].goal_id}")
                        
                elif node_name == "generateQuestionItemFromGoal":
                    questions = state_update.get("generated_questions", [])
                    if questions:
                        print(f"Generated question for goal: {questions[0].goal_id}")
                        
                elif node_name == "validateQuestionSuite":
                    feedback = state_update.get("critic_feedback", {})
                    print(f"Validation Result: Is Valid? {feedback.get('is_valid')}")
                    if feedback.get("failed_goal_ids"):
                        print(f"Failed Goals: {feedback.get('failed_goal_ids')}")
                        
                elif node_name == "assemble_node":
                    suite = state_update.get("final_suite")
                    if suite:
                        print(f"Final Suite Assembled with {len(suite.questions)} questions.")
                        final_suite = suite
        
        print("\n=== FINAL SUITE OUTPUT ===")
        if final_suite:
            print(final_suite.model_dump_json(indent=2))
        else:
            print("No final suite was produced.")
            
    except Exception as e:
        print(f"Workflow failed: {e}")

if __name__ == "__main__":
    test_workflow()
