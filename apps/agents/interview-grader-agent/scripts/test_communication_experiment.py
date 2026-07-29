"""
What: Evaluates Call 2 (Communication & Interpersonal) node using LangSmith Datasets and Experiments.
Why: Automates continuous benchmarking of Communication node outputs against Layer 1 deterministic checks and Layer 2 Communication LLM Judge.
Boundaries: Dev/test evaluation script; does not run in live production FastAPI endpoints.
"""
import os
import sys
import json
import importlib
from typing import Dict, Any, List
from dotenv import load_dotenv

# Setup path mapping for monorepo imports
agent_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
agents_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))

for path in [agent_root, agents_parent, workspace_root]:
    if path not in sys.path:
        sys.path.insert(0, path)

load_dotenv(os.path.join(agents_parent, ".env"))

if "GEMINI_API_KEY1" in os.environ and "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["GEMINI_API_KEY1"]

from langsmith import Client, evaluate

# Dynamic imports
state_mod = importlib.import_module("interview-grader-agent.state")
JobContext = state_mod.JobContext
PlanMeta = state_mod.PlanMeta
GoalInput = state_mod.GoalInput
Interaction = state_mod.Interaction
CommunicationOutput = state_mod.CommunicationOutput

comm_node_mod = importlib.import_module("interview-grader-agent.nodes.communication")
run_communication = comm_node_mod.run_communication

schemas_mod = importlib.import_module("interview-grader-agent.evals.schemas")
ExpectedCommunicationTruth = schemas_mod.ExpectedCommunicationTruth

det_eval_mod = importlib.import_module("interview-grader-agent.evals.communication_deterministic_eval")
evaluate_communication_deterministic = det_eval_mod.evaluate_communication_deterministic

judge_eval_mod = importlib.import_module("interview-grader-agent.evals.communication_llm_judge_eval")
evaluate_communication_llm_judge = judge_eval_mod.evaluate_communication_llm_judge


# ============================================================================
# COMMUNICATION BENCHMARK DATASET (5 TEST CASES)
# ============================================================================

COMMUNICATION_BENCHMARK_CASES: List[Dict[str, Any]] = [
    {
        "test_case_name": "Case 01: Clean Executive Presentation",
        "inputs": {
            "job": {
                "job_name": "VP of Engineering",
                "job_description": "Lead multi-team architecture and present strategic roadmaps to executive leadership."
            },
            "plan_meta": {
                "communication_weight": "high",
                "difficulty": "senior"
            },
            "goals": [
                {
                    "goal_id": "g_01",
                    "topic": "Architecture Roadmap Pitch",
                    "goal": "Evaluate ability to defend technical proposals to executive leadership.",
                    "interaction_history": [
                        {"role": "interviewer", "content": "How would you pitch this microservices budget to the board?"},
                        {"role": "candidate", "content": "I'd organize our proposal into three key pillars: ROI, risk mitigation, and SLA improvements. First, on ROI..."},
                        {"role": "interviewer", "content": "The CFO says this is an expensive vanity project. How do you respond?"},
                        {"role": "candidate", "content": "I understand the CFO's concern about cloud spend. However, our SLA penalties currently cost $50k per outage. Decomposing our monolith directly reduces downtime..."}
                    ]
                }
            ]
        },
        "outputs": {
            "expected_truth": {
                "expected_addressed": True,
                "min_score": 8,
                "max_score": 10,
                "expected_confidence": "high"
            }
        }
    },
    {
        "test_case_name": "Case 02: Defensive & Hostile under Pushback",
        "inputs": {
            "job": {
                "job_name": "Senior Product Manager",
                "job_description": "Collaborate across design and engineering teams."
            },
            "plan_meta": {
                "communication_weight": "high",
                "difficulty": "senior"
            },
            "goals": [
                {
                    "goal_id": "g_01",
                    "topic": "Feature Prioritization",
                    "goal": "Evaluate prioritization rationale.",
                    "interaction_history": [
                        {"role": "interviewer", "content": "Could you walk me through your prioritization framework?"},
                        {"role": "candidate", "content": "I use RICE, obvious choice."},
                        {"role": "interviewer", "content": "Could you give a concrete example of how you calculated R for a past feature?"},
                        {"role": "candidate", "content": "Why are you questioning me? If you don't know what RICE is, maybe you shouldn't be interviewing."}
                    ]
                }
            ]
        },
        "outputs": {
            "expected_truth": {
                "expected_addressed": True,
                "min_score": 1,
                "max_score": 3,
                "expected_confidence": "high"
            }
        }
    },
    {
        "test_case_name": "Case 03: Rambling & Fragmented Structure",
        "inputs": {
            "job": {
                "job_name": "Customer Support Lead",
                "job_description": "Communicate clearly with customers during critical incidents."
            },
            "plan_meta": {
                "communication_weight": "medium",
                "difficulty": "mid"
            },
            "goals": [
                {
                    "goal_id": "g_01",
                    "topic": "Incident Communication",
                    "goal": "Evaluate outage customer communication.",
                    "interaction_history": [
                        {"role": "interviewer", "content": "How do you notify customers of a service outage?"},
                        {"role": "candidate", "content": "Well, outages happen, right? Like last Tuesday my internet went out at home and my dog was barking... anyway, for customers we send emails, but sometimes emails bounce, so we might tweet, or maybe update statuspage, but statuspage was down once so we tried Slack..."}
                    ]
                }
            ]
        },
        "outputs": {
            "expected_truth": {
                "expected_addressed": True,
                "min_score": 3,
                "max_score": 5,
                "expected_confidence": "high"
            }
        }
    },
    {
        "test_case_name": "Case 04: Extreme Hedging & Evasiveness",
        "inputs": {
            "job": {
                "job_name": "Lead Security Auditor",
                "job_description": "Audit compliance and give decisive security recommendations."
            },
            "plan_meta": {
                "communication_weight": "high",
                "difficulty": "senior"
            },
            "goals": [
                {
                    "goal_id": "g_01",
                    "topic": "Compliance Audit Decision",
                    "goal": "Evaluate decisive decision-making.",
                    "interaction_history": [
                        {"role": "interviewer", "content": "Should we issue a public vulnerability advisory for this leak?"},
                        {"role": "candidate", "content": "I guess maybe? I mean, I'm not really sure, it depends on what others think, I don't want to make the wrong call..."}
                    ]
                }
            ]
        },
        "outputs": {
            "expected_truth": {
                "expected_addressed": True,
                "min_score": 3,
                "max_score": 5,
                "expected_confidence": "high"
            }
        }
    },
    {
        "test_case_name": "Case 05: ESL Phrasing With Solid Professional Structure",
        "inputs": {
            "job": {
                "job_name": "Senior DevOps Engineer",
                "job_description": "Manage CI/CD pipelines and infrastructure."
            },
            "plan_meta": {
                "communication_weight": "medium",
                "difficulty": "senior"
            },
            "goals": [
                {
                    "goal_id": "g_01",
                    "topic": "CI/CD Pipeline Breakdown",
                    "goal": "Evaluate deployment troubleshooting.",
                    "interaction_history": [
                        {"role": "interviewer", "content": "How do you handle deployment failures in production?"},
                        {"role": "candidate", "content": "First we doing automatic rollback via ArgoCD. Second we checking Grafana metric for error spike. Third we notifying team channel."}
                    ]
                }
            ]
        },
        "outputs": {
            "expected_truth": {
                "expected_addressed": True,
                "min_score": 7,
                "max_score": 9,
                "expected_confidence": "high"
            }
        }
    }
]


# --- 1. Target Function Executing Communication Node ---

def evaluate_communication_target(inputs: dict) -> dict:
    """
    Target function wrapper invoking run_communication node for LangSmith evaluation.
    """
    job_obj = JobContext(**inputs["job"])
    plan_meta_obj = PlanMeta(**inputs["plan_meta"])

    goal_objs = []
    for g in inputs["goals"]:
        interactions = [Interaction(**i) for i in g.get("interaction_history", [])]
        goal_objs.append(
            GoalInput(
                goal_id=g.get("goal_id", "g_01"),
                topic=g.get("topic", "Communication"),
                goal=g.get("goal", "Evaluate communication"),
                passing_criteria=g.get("passing_criteria", []),
                wrong_answer_signals=g.get("wrong_answer_signals", []),
                pushback_triggers=g.get("pushback_triggers", []),
                grounding_theory=g.get("grounding_theory", ""),
                weight=g.get("weight", 1.0),
                gating=g.get("gating", False),
                interaction_history=interactions,
            )
        )

    input_state = {
        "job": job_obj,
        "plan_meta": plan_meta_obj,
        "goals": goal_objs,
    }

    node_result = run_communication(input_state)
    comm_output: CommunicationOutput = node_result["communication"]

    return {
        "communication": comm_output.model_dump() if hasattr(comm_output, "model_dump") else comm_output,
        "input_state": input_state,
    }


# --- 2. LangSmith Evaluator 1: Layer 1 Deterministic Code Checks ---

def evaluate_communication_deterministic_langsmith(run, example) -> dict:
    """
    LangSmith evaluator for Layer 1 Communication deterministic code checks.
    """
    try:
        raw_output = run.outputs.get("communication")
        comm_output = CommunicationOutput(communication=raw_output)

        expected_dict = example.outputs.get("expected_truth")
        expected_truth = ExpectedCommunicationTruth(**expected_dict)

        det_result = evaluate_communication_deterministic(comm_output, expected_truth)

        results = []
        allowed_exact = (
            "communication_addressed",
            "score_range",
            "confidence_match",
            "protected_characteristic_leakage",
        )

        for item in det_result.check_items:
            clean_key = item.check_name.replace("[", "_").replace("]", "").replace("-", "_")
            if clean_key in allowed_exact:
                results.append({
                    "key": clean_key,
                    "score": 1.0 if item.passed else 0.0,
                })

        return {"results": results}
    except Exception as err:
        sys.stderr.write(f"Communication deterministic evaluator error: {err}\n")
        return {
            "results": [
                {"key": "deterministic_eval_error", "score": 1.0}
            ]
        }


# --- 3. LangSmith Evaluator 2: Layer 2 LLM-as-a-Judge ---

def evaluate_communication_llm_judge_langsmith(run, example) -> dict:
    """
    LangSmith evaluator for Layer 2 Communication LLM-as-a-Judge quality auditing.
    """
    try:
        raw_output = run.outputs.get("communication")
        comm_output = CommunicationOutput(communication=raw_output)
        input_state = run.outputs.get("input_state")

        judge_result = evaluate_communication_llm_judge(input_state, comm_output)

        return {
            "results": [
                {"key": "judge_passed", "score": 1.0 if judge_result.passed else 0.0},
                {"key": "flow_control", "score": float(judge_result.flow_control.score)},
                {"key": "active_listening", "score": float(judge_result.active_listening.score)},
                {"key": "structure", "score": float(judge_result.structure.score)},
                {"key": "assertiveness", "score": float(judge_result.assertiveness.score)},
                {"key": "objection_handling", "score": float(judge_result.objection_handling.score)},
            ]
        }
    except Exception as err:
        sys.stderr.write(f"Communication LLM Judge evaluator error: {err}\n")
        return {
            "results": [
                {"key": "judge_eval_error", "score": 1.0}
            ]
        }


# --- Main Experiment Runner ---

def main():
    print("=======================================================================")
    print("  RUNNING COMMUNICATION NODE LANGSMITH DATASET & EXPERIMENT EVALUATION ")
    print("=======================================================================")

    dataset_name = "Communication Node Grader Dataset"
    client = Client()

    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
        print(f"Dataset '{dataset_name}' found in LangSmith.")
    except Exception:
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="LangSmith benchmark dataset for Call 2 Communication Node."
        )
        print(f"Created dataset '{dataset_name}' successfully.")

    existing_examples = list(client.list_examples(dataset_id=dataset.id))
    if len(existing_examples) != len(COMMUNICATION_BENCHMARK_CASES):
        print(f"Syncing dataset examples (found {len(existing_examples)}, uploading {len(COMMUNICATION_BENCHMARK_CASES)})...")
        for eg in existing_examples:
            client.delete_example(example_id=eg.id)
        for case in COMMUNICATION_BENCHMARK_CASES:
            client.create_example(
                inputs=case["inputs"],
                outputs=case["outputs"],
                dataset_id=dataset.id
            )
        print("Dataset sync complete.")

    print("\nTriggering LangSmith Communication Experiment evaluation...")
    results = evaluate(
        evaluate_communication_target,
        data=dataset_name,
        evaluators=[
            evaluate_communication_deterministic_langsmith,
            evaluate_communication_llm_judge_langsmith,
        ],
        experiment_prefix="communication-node-eval"
    )

    print("\nLangSmith Communication Node Experiment Evaluation Completed Successfully!")
    print("=======================================================================")


if __name__ == "__main__":
    main()
