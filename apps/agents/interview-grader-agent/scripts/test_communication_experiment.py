"""
What: Evaluates Call 2 (Communication & Interpersonal) node using LangSmith Datasets and Experiments across 20 test cases.
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

cases_mod = importlib.import_module("interview-grader-agent.evals.datasets.communication_judge_cases")
if hasattr(cases_mod, "ALL_COMMUNICATION_JUDGE_META_BENCHMARK_TEST_CASES"):
    BENCHMARK_CASES = cases_mod.ALL_COMMUNICATION_JUDGE_META_BENCHMARK_TEST_CASES
else:
    BENCHMARK_CASES = cases_mod.ALL_COMMUNICATION_JUDGE_BENCHMARK_TEST_CASES

judge_eval_mod = importlib.import_module("interview-grader-agent.evals.communication_llm_judge_eval")
evaluate_communication_llm_judge = judge_eval_mod.evaluate_communication_llm_judge


# ============================================================================
# DATASET CONSTRUCTION (20 TEST CASES)
# ============================================================================

def build_langsmith_dataset_cases() -> List[Dict[str, Any]]:
    """
    Extracts inputs and target expected truth from the 20 benchmark test cases
    with explicit sequential index prefixes [01/20] through [20/20].
    """
    dataset_cases = []

    for idx, case in enumerate(BENCHMARK_CASES, start=1):
        raw_case_id = case.get("test_case_id", "unknown_case")
        case_id = f"[{idx:02d}/20] {raw_case_id}"
        input_state = case.get("input_state", {})
        comm_payload = case.get("communication_payload", {}).get("communication", {})

        target_score = comm_payload.get("score")
        target_addressed = comm_payload.get("addressed", True)
        target_confidence = comm_payload.get("confidence", "high")

        plan_meta = input_state.get("plan_meta", {
            "communication_weight": "high",
            "difficulty": "senior"
        })

        dataset_cases.append({
            "test_case_name": case_id,
            "inputs": {
                "case_index": idx,
                "test_case_id": case_id,
                "job": input_state.get("job", {}),
                "plan_meta": plan_meta,
                "goals": input_state.get("goals", [])
            },
            "outputs": {
                "expected_truth": {
                    "expected_addressed": target_addressed,
                    "target_score": target_score,
                    "min_score": (target_score - 1) if target_score is not None else None,
                    "max_score": (target_score + 1) if target_score is not None else None,
                    "expected_confidence": target_confidence
                }
            }
        })

    return dataset_cases


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


# --- 2. LangSmith Evaluator 1: Layer 1 Deterministic Code Checks (2 Metrics) ---

def evaluate_communication_deterministic_langsmith(run, example) -> dict:
    """
    LangSmith evaluator for Layer 1 Communication deterministic checks (2 metrics):
    1. score_match: 10 - abs(actual_score - target_score) (scale 0-10)
    2. confidence_match: ordinal distance score based on low (0) < medium (1) < high (2):
       - difference 0 -> 1.0 (exact match)
       - difference 1 -> 0.5 (1 level off)
       - difference 2 -> 0.0 (2 levels off)
    """
    try:
        raw_output = run.outputs.get("communication")
        expected_truth = example.outputs.get("expected_truth", {})

        comm_output = None
        if raw_output and isinstance(raw_output, dict):
            try:
                comm_output = CommunicationOutput(communication=raw_output)
            except Exception:
                comm_output = None

        actual_comm = comm_output.communication if (comm_output and comm_output.communication) else None
        actual_score = actual_comm.score if actual_comm else None
        target_score = expected_truth.get("target_score")

        # 1. Score Metric (10 - abs(actual - target))
        if actual_score is not None and target_score is not None:
            score_diff = abs(int(actual_score) - int(target_score))
            score_match_val = float(max(0, 10 - score_diff))
        elif actual_score is None and target_score is None:
            score_match_val = 10.0
        else:
            score_match_val = 0.0

        # 2. Confidence Metric (Ordinal Distance: diff 0 -> 1.0, diff 1 -> 0.5, diff 2 -> 0.0)
        actual_conf = str(actual_comm.confidence).lower() if (actual_comm and actual_comm.confidence) else None
        expected_conf = str(expected_truth.get("expected_confidence")).lower() if expected_truth.get("expected_confidence") else None

        conf_map = {"low": 0, "medium": 1, "high": 2}

        if actual_conf is None and expected_conf is None:
            conf_match_val = 1.0
        elif actual_conf in conf_map and expected_conf in conf_map:
            conf_diff = abs(conf_map[actual_conf] - conf_map[expected_conf])
            if conf_diff == 0:
                conf_match_val = 1.0
            elif conf_diff == 1:
                conf_match_val = 0.5
            else:
                conf_match_val = 0.0
        else:
            conf_match_val = 0.0

        return {
            "results": [
                {"key": "score_match", "score": score_match_val},
                {"key": "confidence_match", "score": conf_match_val},
            ]
        }
    except Exception as err:
        sys.stderr.write(f"Communication deterministic evaluator error: {err}\n")
        return {
            "results": [
                {"key": "score_match", "score": 0.0},
                {"key": "confidence_match", "score": 0.0},
            ]
        }


# --- 3. LangSmith Evaluator 2: Layer 2 LLM-as-a-Judge (5 Metrics) ---

def evaluate_communication_llm_judge_langsmith(run, example) -> dict:
    """
    LangSmith evaluator for Layer 2 Communication LLM-as-a-Judge (5 metrics):
    1. flow_control (0-10 score)
    2. active_listening (0-10 score)
    3. structure (0-10 score)
    4. assertiveness (0-10 score)
    5. objection_handling (0-10 score)
    """
    try:
        raw_output = run.outputs.get("communication")
        comm_output = CommunicationOutput(communication=raw_output)
        input_state = run.outputs.get("input_state")

        judge_result = evaluate_communication_llm_judge(input_state, comm_output)

        return {
            "results": [
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
                {"key": "flow_control", "score": 0.0},
                {"key": "active_listening", "score": 0.0},
                {"key": "structure", "score": 0.0},
                {"key": "assertiveness", "score": 0.0},
                {"key": "objection_handling", "score": 0.0},
            ]
        }


# --- Main Experiment Runner ---

def main():
    import uuid
    import datetime

    print("=======================================================================")
    print("  RUNNING COMMUNICATION NODE LANGSMITH DATASET & EXPERIMENT EVALUATION ")
    print("=======================================================================")

    dataset_cases = build_langsmith_dataset_cases()
    print(f"Loaded {len(dataset_cases)} benchmark test cases from communication_judge_cases.py.")

    dataset_name = "Communication Node Grader Dataset"
    client = Client()

    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
        print(f"Dataset '{dataset_name}' found in LangSmith.")
    except Exception:
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="LangSmith benchmark dataset for Call 2 Communication Node (20 cases)."
        )
        print(f"Created dataset '{dataset_name}' successfully.")

    existing_examples = list(client.list_examples(dataset_id=dataset.id))
    if len(existing_examples) < len(dataset_cases):
        print(f"Creating dataset examples ({len(dataset_cases)} ordered examples)...")
        base_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=30)
        for case in dataset_cases:
            idx = case["inputs"]["case_index"]
            created_timestamp = base_time + datetime.timedelta(seconds=idx)
            client.create_example(
                inputs=case["inputs"],
                outputs=case["outputs"],
                dataset_id=dataset.id,
                created_at=created_timestamp,
            )
        print("Dataset creation complete.")
    else:
        print(f"Reusing existing {len(existing_examples)} dataset examples from dataset '{dataset_name}'.")

    # Fetch examples and sort strictly by case_index 1..20
    dataset_examples = list(client.list_examples(dataset_id=dataset.id))
    sorted_examples = sorted(dataset_examples, key=lambda x: x.inputs.get("case_index", 0))

    print(f"\nTriggering LangSmith Communication Experiment evaluation sequentially across {len(sorted_examples)} sorted examples (max_concurrency=1)...")
    results = evaluate(
        evaluate_communication_target,
        data=sorted_examples,
        evaluators=[
            evaluate_communication_deterministic_langsmith,
            evaluate_communication_llm_judge_langsmith,
        ],
        max_concurrency=1,
        experiment_prefix="communication-node-eval-ordered"
    )

    print("\nLangSmith Communication Node Experiment Evaluation Completed Successfully!")
    print("=======================================================================")


if __name__ == "__main__":
    main()

