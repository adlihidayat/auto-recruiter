"""
What: CLI runner for benchmarking and calibrating the Communication LLM-as-a-Judge against human ground truth across 5 test cases.
Why: Computes score deltas and 5-signal alignment rates to verify Communication Judge reliability.
Boundaries: Benchmark script only; does not alter judge prompts or dataset test cases.
"""
import sys
import os
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

# Dynamic imports
benchmark_mod = importlib.import_module("interview-grader-agent.evals.communication_judge_benchmark")
evaluate_communication_meta_judge = benchmark_mod.evaluate_communication_meta_judge

cases_mod = importlib.import_module("interview-grader-agent.evals.datasets.communication_judge_cases")
if hasattr(cases_mod, "ALL_COMMUNICATION_JUDGE_META_BENCHMARK_TEST_CASES"):
    ALL_COMMUNICATION_JUDGE_BENCHMARK_TEST_CASES = cases_mod.ALL_COMMUNICATION_JUDGE_META_BENCHMARK_TEST_CASES
else:
    ALL_COMMUNICATION_JUDGE_BENCHMARK_TEST_CASES = cases_mod.ALL_COMMUNICATION_JUDGE_BENCHMARK_TEST_CASES

schemas_mod = importlib.import_module("interview-grader-agent.evals.schemas")
CommunicationJudgeBenchmarkTestCase = schemas_mod.CommunicationJudgeBenchmarkTestCase


def run_communication_judge_calibration() -> bool:
    """
    Executes Communication Meta-Judge calibration benchmark suite across all 5 test cases.
    """
    print("=" * 90)
    print("      INTERVIEW GRADER AGENT: COMMUNICATION META-JUDGE CALIBRATION SUITE (5 CASES)      ")
    print("=" * 90)

    total_cases = len(ALL_COMMUNICATION_JUDGE_BENCHMARK_TEST_CASES)
    aligned_cases = 0
    verdict_matched_cases = 0

    for index, raw_case in enumerate(ALL_COMMUNICATION_JUDGE_BENCHMARK_TEST_CASES, start=1):
        test_case = CommunicationJudgeBenchmarkTestCase(**raw_case)
        print(f"\n------------------------------------------------------------------------------------------")
        print(f"[{index:02d}/{total_cases:02d}] CASE: {test_case.test_case_id}")
        print(f"Description: {test_case.description}")
        print(f"------------------------------------------------------------------------------------------")

        report = evaluate_communication_meta_judge(test_case)

        if report.overall_aligned:
            aligned_cases += 1
            print(f"  Overall Status: ✓ ALIGNED | Verdict Match: {report.verdict_matched}\n")
        else:
            print(f"  Overall Status: ✗ MISALIGNED | Verdict Match: {report.verdict_matched}\n")

        if report.verdict_matched:
            verdict_matched_cases += 1

        print("  DETAILED COMPARISON BY DISCOURSE SIGNAL:")
        for dim_key, dim_res in report.dimension_alignments.items():
            status_icon = "✓" if dim_res.aligned else "✗"
            print(f"    [{status_icon}] {dim_key.upper()}:")
            print(f"        • LLM Judge Score:   {dim_res.llm_judge_score}/10 (Pass: {dim_res.llm_judge_passed})")
            print(f"        • Human Expected:    {dim_res.human_min_score}-{dim_res.human_max_score}/10 (Pass: {dim_res.human_expected_passed})")
            print(f"        • LLM Rationale:     {dim_res.llm_rationale}")
            print(f"        • Human Rationale:   {dim_res.human_rationale}\n")

    alignment_rate = (aligned_cases / total_cases) * 100
    verdict_rate = (verdict_matched_cases / total_cases) * 100

    print("=" * 90)
    print("                                   SUMMARY CALIBRATION REPORT                             ")
    print("=" * 90)
    print(f" Total Test Cases Evaluated:       {total_cases}/{total_cases}")
    print(f" Benchmark Alignment Rate:         {aligned_cases}/{total_cases} ({alignment_rate:.1f}%)")
    print(f" Overall Pass/Fail Verdict Match:  {verdict_matched_cases}/{total_cases} ({verdict_rate:.1f}%)")
    print("=" * 90)

    return aligned_cases == total_cases


if __name__ == "__main__":
    run_communication_judge_calibration()
