"""
What: CLI runner for benchmarking and calibrating the LLM-as-a-Judge against human ground truth across 20 benchmark test cases.
Why: Computes score deltas, verdict agreement rates, and flaw sensitivity to verify Judge reliability.
Boundaries: Benchmark script only; does not alter judge prompts or dataset test cases.
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

# Dynamic imports
benchmark_mod = importlib.import_module("interview-grader-agent.evals.judge_benchmark")
evaluate_meta_judge = benchmark_mod.evaluate_meta_judge

cases_mod = importlib.import_module("interview-grader-agent.evals.datasets.judge_benchmark_cases")
ALL_JUDGE_BENCHMARK_TEST_CASES = cases_mod.ALL_JUDGE_BENCHMARK_TEST_CASES


def run_judge_calibration() -> bool:
    """
    Executes Meta-Judge calibration benchmark suite across all 20 test cases.
    
    Returns True if LLM Judge matches human ground-truth labels across all benchmark cases.
    """
    print("==========================================================================================")
    print("           INTERVIEW GRADER AGENT: META-JUDGE CALIBRATION SUITE (20 BENCHMARK CASES)      ")
    print("==========================================================================================\n")

    reports = []
    all_aligned = True

    for idx, test_case in enumerate(ALL_JUDGE_BENCHMARK_TEST_CASES, start=1):
        print(f"------------------------------------------------------------------------------------------")
        print(f"[{idx:02d}/20] CASE: {test_case.test_case_id}")
        print(f"Description: {test_case.description}")
        print(f"------------------------------------------------------------------------------------------")
        
        try:
            report = evaluate_meta_judge(test_case)
        except Exception as err:
            print(f"  ❌ Failed to execute Meta-Judge evaluation: {err}\n")
            all_aligned = False
            continue

        status_str = "✓ ALIGNED" if report.overall_aligned else "✗ MISALIGNED"
        print(f"  Overall Status: {status_str} | Verdict Match: {report.verdict_matched}\n")
        
        print("  DETAILED COMPARISON BY DIMENSION:")
        for dim_name, alignment in report.dimension_alignments.items():
            icon = "✓" if alignment.aligned else "✗"
            print(f"    [{icon}] {dim_name.upper()}:")
            print(f"        • LLM Judge Score:   {alignment.llm_judge_score}/10 (Pass: {alignment.llm_judge_passed})")
            print(f"        • Human Expected:    {alignment.human_min_score}-{alignment.human_max_score}/10 (Pass: {alignment.human_expected_passed})")
            print(f"        • LLM Rationale:     {alignment.llm_rationale}")
            print(f"        • Human Rationale:   {alignment.human_rationale}")
            print()

        if not report.overall_aligned:
            all_aligned = False

        reports.append(report)

    aligned_count = sum(1 for r in reports if r.overall_aligned)
    verdict_match_count = sum(1 for r in reports if r.verdict_matched)

    print("==========================================================================================")
    print("                                   SUMMARY CALIBRATION REPORT                             ")
    print("==========================================================================================")
    print(f" Total Test Cases Evaluated:       {len(reports)}/20")
    print(f" Benchmark Alignment Rate:         {aligned_count}/{len(reports)} ({(aligned_count/len(reports))*100:.1f}%)")
    print(f" Overall Pass/Fail Verdict Match:  {verdict_match_count}/{len(reports)} ({(verdict_match_count/len(reports))*100:.1f}%)")
    print("==========================================================================================")

    return all_aligned


if __name__ == "__main__":
    success = run_judge_calibration()
    sys.exit(0 if success else 1)
