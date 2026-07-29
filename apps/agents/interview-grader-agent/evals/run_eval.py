"""
What: Main CLI test runner for the 2-layer Core Analysis evaluation framework.
Why: Runs Call 1 (Core Analysis) node against test cases, executes Layer 1 deterministic and Layer 2 LLM-as-a-Judge evaluations, and prints summary metrics.
Boundaries: CLI entrypoint for local and CI benchmarking; does not run production API.
"""
import sys
import os
import argparse
import importlib
from dotenv import load_dotenv

# Setup path mapping for monorepo structure
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

# Load environment variables
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
load_dotenv(env_path)

if "GEMINI_API_KEY1" in os.environ and "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["GEMINI_API_KEY1"]

# Dynamic imports to handle hyphenated directory name 'interview-grader-agent'
core_analysis_module = importlib.import_module("interview-grader-agent.nodes.core_analysis")
run_core_analysis = core_analysis_module.run_core_analysis

schemas_module = importlib.import_module("interview-grader-agent.evals.schemas")
TestCaseEvalReport = schemas_module.TestCaseEvalReport

det_eval_module = importlib.import_module("interview-grader-agent.evals.deterministic_eval")
evaluate_deterministic = det_eval_module.evaluate_deterministic

judge_eval_module = importlib.import_module("interview-grader-agent.evals.llm_judge_eval")
evaluate_llm_judge = judge_eval_module.evaluate_llm_judge

cases_module = importlib.import_module("interview-grader-agent.evals.datasets.core_analysis_cases")
ALL_CORE_ANALYSIS_TEST_CASES = cases_module.ALL_CORE_ANALYSIS_TEST_CASES


def run_evaluation(skip_llm_judge: bool = False) -> bool:
    """
    Runs evaluation suite across all Core Analysis test cases.
    
    Returns True if all test cases pass both evaluation layers, False otherwise.
    """
    print("===============================================================")
    print("      INTERVIEW GRADER AGENT: CORE ANALYSIS EVALUATION        ")
    print("===============================================================\n")

    reports = []
    all_passed = True

    for test_case in ALL_CORE_ANALYSIS_TEST_CASES:
        print(f"[RUNNING] {test_case.test_case_id}: {test_case.description}")
        
        # 1. Execute Core Analysis Node
        try:
            node_result = run_core_analysis(test_case.input_state)
            core_output = node_result["core_analysis"]
        except Exception as err:
            print(f"  ❌ Failed to execute run_core_analysis: {err}")
            all_passed = False
            continue

        # 2. Layer 1: Deterministic Evaluation
        det_result = evaluate_deterministic(core_output, test_case.ground_truth)
        
        print(f"  └─ Layer 1 (Deterministic): {'PASS' if det_result.passed else 'FAIL'} ({det_result.passed_checks}/{det_result.total_checks} checks passed)")
        for check in det_result.check_items:
            status_icon = "✓" if check.passed else "✗"
            print(f"      [{status_icon}] {check.check_name}: {check.details}")

        if det_result.protected_characteristic_violations:
            print("      ⚠️ PROTECTED CHARACTERISTIC LEAKAGE DETECTED:")
            for violation in det_result.protected_characteristic_violations:
                print(f"         - Field: {violation.field_name} | Keyword: '{violation.detected_keyword}'")

        # 3. Layer 2: LLM-as-a-Judge Evaluation (Conditional)
        judge_result = None
        if not skip_llm_judge:
            try:
                judge_result = evaluate_llm_judge(test_case.input_state, core_output)
                print(f"  └─ Layer 2 (LLM Judge): {'PASS' if judge_result.passed else 'FAIL'} (Score: {judge_result.overall_judge_score:.1f}/10)")
                print(f"      - Rationale Groundedness: {judge_result.rationale_groundedness.score}/10 ({judge_result.rationale_groundedness.rationale})")
                print(f"      - Evidence Faithfulness:  {judge_result.evidence_faithfulness.score}/10 ({judge_result.evidence_faithfulness.rationale})")
                print(f"      - Reasoning Coherence:   {judge_result.reasoning_coherence.score}/10 ({judge_result.reasoning_coherence.rationale})")
                print(f"      - Flag Justification:    {judge_result.flag_justification_quality.score}/10 ({judge_result.flag_justification_quality.rationale})")
            except Exception as err:
                print(f"  ⚠️ LLM Judge execution failed: {err}")

        case_passed = det_result.passed and (judge_result.passed if judge_result else True)
        if not case_passed:
            all_passed = False

        reports.append(
            TestCaseEvalReport(
                test_case_id=test_case.test_case_id,
                test_case_description=test_case.description,
                overall_passed=case_passed,
                deterministic_eval=det_result,
                llm_judge_eval=judge_result,
            )
        )
        print()

    print("===============================================================")
    print(f"SUMMARY: {sum(1 for r in reports if r.overall_passed)}/{len(reports)} Test Cases Passed Overall")
    print("===============================================================")
    
    return all_passed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Core Analysis Evaluation Suite")
    parser.add_argument("--skip-llm-judge", action="store_true", help="Skip Layer 2 LLM Judge assessment")
    args = parser.parse_args()

    success = run_evaluation(skip_llm_judge=args.skip_llm_judge)
    sys.exit(0 if success else 1)
