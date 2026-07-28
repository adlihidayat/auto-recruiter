"""
What: CLI runner for the Grader Evaluation Framework across all 20 core analysis test cases (02-21).
Why: Dynamically executes Core Analysis on all cases, runs per-goal deterministic checks, invokes LLM Judge, and prints a comprehensive scorecard report.
Boundaries: CLI entrypoint for local eval suite execution.
"""

import sys
import os
import json
import importlib
from dotenv import load_dotenv

# Setup path imports for monorepo
evals_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(evals_dir)
sys.path.append(os.path.abspath(os.path.join(evals_dir, "..")))
sys.path.append(os.path.abspath(os.path.join(evals_dir, "../..")))
sys.path.append(os.path.abspath(os.path.join(evals_dir, "../../../..")))

# Load environment
env_path = os.path.abspath(os.path.join(evals_dir, "../../.env"))
load_dotenv(env_path)

if "GEMINI_API_KEY1" in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["GEMINI_API_KEY1"]
if "LANGSMITH_API_KEY" in os.environ:
    os.environ["LANGCHAIN_API_KEY"] = os.environ["LANGSMITH_API_KEY"]

# Dynamic imports
nodes_module = importlib.import_module("interview-grader-agent.nodes.core_analysis")
run_core_analysis = nodes_module.run_core_analysis

import deterministic
import judge
from cases.core_analysis_cases import ALL_MOCK_STATES, ALL_GOLD_FACTS


def run_evaluation_for_case(state: dict, gold_facts) -> dict:
    """Executes core analysis, runs deterministic checks, and calls LLM judge."""
    print(f"\n=======================================================")
    print(f"RUNNING EVALUATION FOR: {gold_facts.case_id}")
    print(f"Description: {gold_facts.description}")
    print(f"=======================================================")

    # 1. Execute Core Analysis Node
    print("[Step 1/3] Executing Core Analysis Node...")
    step_output = run_core_analysis(state)
    core_analysis_result = step_output.get("core_analysis")

    # 2. Run Deterministic Checks
    print("[Step 2/3] Running Deterministic Code Checks...")
    det_result = deterministic.run_deterministic_checks(core_analysis_result, gold_facts)
    print(f"  - Schema Valid: {det_result.schema_valid}")
    print(f"  - Protected Characteristic Leaked: {det_result.protected_characteristic_leaked}")
    print(f"  - Deterministic Check Overall Passed: {det_result.deterministic_passed}")

    # 3. Run LLM-as-a-Judge Evaluation
    print("[Step 3/3] Invoking LLM Judge (gemini_flash_lite)...")
    judge_report = judge.evaluate_with_llm_judge(core_analysis_result, gold_facts, state["goals"])
    judge_report.schema_valid = det_result.schema_valid

    return {
        "case_id": gold_facts.case_id,
        "gold_facts": gold_facts,
        "actual_output": core_analysis_result,
        "deterministic": det_result,
        "judge_report": judge_report
    }


def main():
    test_cases = []
    for key in sorted(ALL_MOCK_STATES.keys()):
        test_cases.append((ALL_MOCK_STATES[key], ALL_GOLD_FACTS[key]))
            
    print(f"Discovered {len(test_cases)} test cases in core_analysis_cases.py. Starting evaluation suite...")
    
    reports = []
    for state, gold in test_cases:
        try:
            report = run_evaluation_for_case(state, gold)
            reports.append(report)
        except Exception as err:
            print(f"❌ Error running evaluation for case {gold.case_id}: {err}")
            import traceback
            traceback.print_exc()

    # Print Detailed Field-by-Field Scorecard Table
    print("\n" + "=" * 120)
    print(f"DETAILED FIELD-BY-FIELD EVALUATION SCORECARD TABLE ({len(reports)} CASES)")
    print("=" * 120)
    
    header = (
        f"{'CASE ID':<35} | {'GOAL':<6} | {'SCORE (EXP vs ACT)':<20} | "
        f"{'PUSHBACK (EXP vs ACT)':<25} | {'RED FLAGS / CONSISTENCY / GUARDRAILS':<25}"
    )
    print(header)
    print("-" * 120)
    
    total_judge_score = 0
    passed_cases = 0
    
    for r in reports:
        case_id = r["case_id"]
        gold = r["gold_facts"]
        actual = r["actual_output"]
        det = r["deterministic"]
        j = r["judge_report"]
        
        total_judge_score += j.overall_case_score
        if j.overall_case_score >= 8 and det.deterministic_passed:
            passed_cases += 1
            
        # Goal details
        for goal_id, g_eval in j.per_goal.items():
            gold_g = gold.per_goal.get(goal_id)
            exp_range = f"{list(gold_g.expected_score_range)}" if gold_g and gold_g.expected_score_range else "N/A"
            act_score = str(g_eval.score_reasonableness.actual) if g_eval.score_reasonableness.actual is not None else "None"
            score_str = f"{exp_range} vs {act_score} ({g_eval.score_reasonableness.verdict})"
            
            exp_pb = f"{gold_g.expected_pushback_triggered} ({gold_g.expected_response_type})" if gold_g and gold_g.expected_pushback_triggered else "False"
            act_pb = f"{g_eval.pushback_classification.actual_triggered} ({g_eval.pushback_classification.actual_response_type})"
            pb_str = f"{exp_pb} vs {act_pb}"
            
            # Diagnostic summary
            diag = []
            if j.red_flag_detection.verdict == "fail":
                diag.append("RedFlag Missed")
            if j.consistency_detection.verdict == "fail":
                diag.append("Consistency Missed")
            if det.protected_characteristic_leaked:
                diag.append("Leaked Char")
            if not diag:
                diag_str = "All Guardrails OK"
            else:
                diag_str = ", ".join(diag)
                
            print(f"{case_id:<35} | {goal_id:<6} | {score_str:<20} | {pb_str:<25} | {diag_str:<25}")
        print("-" * 120)

    avg_score = total_judge_score / len(reports) if reports else 0
    print(f"Average LLM Judge Score across {len(reports)} cases: {avg_score:.2f}/10")
    print(f"Overall Suite Success Rate (Score >= 8 & Det Pass): {passed_cases}/{len(reports)}")
    print("=" * 120)

    # Print Detailed Failure Diagnostics for Prompt Tuning
    print("\n" + "=" * 120)
    print("PROMPT TUNING DIAGNOSTIC FAILURE NOTES")
    print("=" * 120)
    for r in reports:
        j = r["judge_report"]
        print(f"\n📌 [Case: {j.case_id}] (Score: {j.overall_case_score}/10)")
        if j.failure_modes:
            for fm in j.failure_modes:
                print(f"   ❌ {fm}")
        else:
            print("   ✅ No failure modes detected. Perfect execution!")


if __name__ == "__main__":
    main()
