"""
What: Core evaluation runner for the LLM Judge node.
Why: Orchestrates regression runs across simulated grader outputs and JudgeGoldFacts targets.
Boundaries: Orchestrates test suite execution and report printing; delegates assertions to judge.py and deterministic.py.
"""

from typing import List, Optional

from .schemas import EvalCaseReport, DeterministicCaseResult, LLMJudgeResult
from .deterministic import evaluate_deterministic
from .judge import evaluate_llm_judge
from .cases.core_analysis_cases import ALL_TEST_CASES


def run_evaluation_suite(
    filter_case_id: Optional[str] = None,
    include_judge: bool = True,
    verbose: bool = True,
) -> List[EvalCaseReport]:
    """
    Runs evaluation pipeline on test cases.

    Args:
        filter_case_id: Optional case_id substring filter to run a single test case.
        include_judge: If True, runs gemini_flash_lite qualitative judge.
        verbose: If True, prints formatted console summary table.

    Returns:
        List of EvalCaseReport objects.
    """
    reports: List[EvalCaseReport] = []

    cases_to_run = ALL_TEST_CASES
    if filter_case_id:
        cases_to_run = [
            (mock_out, gold) for mock_out, gold in ALL_TEST_CASES
            if filter_case_id.lower() in gold.case_id.lower()
        ]

    if verbose:
        print(f"\n================================================================================")
        print(f"       STARTING LLM JUDGE EVALUATION SUITE ({len(cases_to_run)} TEST CASES)")
        print(f"================================================================================\n")

    for index, (mock_output, gold_facts) in enumerate(cases_to_run, 1):
        if verbose:
            print(f"[{index}/{len(cases_to_run)}] Evaluating Judge on: {gold_facts.case_id}...")

        # 1. Run Deterministic Layer (Pure Code Schema & Guardrails)
        det_result: DeterministicCaseResult = evaluate_deterministic(mock_output, mock_output, gold_facts)

        # 2. Run LLM Judge Layer (gemini_flash_lite)
        judge_result: Optional[LLMJudgeResult] = None
        if include_judge and mock_output is not None:
            if verbose:
                print(f"    -> Running LLM Judge (gemini_flash_lite)...")
            judge_result = evaluate_llm_judge(mock_output, mock_output, gold_facts)

        report = EvalCaseReport(
            case_id=gold_facts.case_id,
            description=gold_facts.description,
            deterministic=det_result,
            judge=judge_result,
        )
        reports.append(report)

    if verbose:
        _print_summary_table(reports)

    return reports


def _print_summary_table(reports: List[EvalCaseReport]) -> None:
    """Prints a formatted summary table of evaluation results to console."""
    print(f"\n================================================================================")
    print(f"                       EVALUATION RESULTS SUMMARY")
    print(f"================================================================================\n")

    total_cases = len(reports)
    passed_cases = sum(1 for r in reports if r.deterministic.overall_pass)
    pass_rate = (passed_cases / total_cases * 100) if total_cases > 0 else 0.0

    print(f"Deterministic Pass Rate: {passed_cases}/{total_cases} ({pass_rate:.1f}%)\n")

    # Header
    header = f"{'Case ID':<42} | {'Schema':<7} | {'Guardrail':<9} | {'Judge Assertions':<18}"
    print(header)
    print("-" * len(header))

    for r in reports:
        case_name = r.case_id[:40]
        schema_str = "PASS" if r.deterministic.schema_valid else "FAIL"
        guard_str = "CLEAN" if r.deterministic.guardrail_leak_check else "LEAKED"

        if r.judge:
            judge_str = "ALL MATCH" if r.judge.all_judge_assertions_passed else "MISMATCH DETECTED"
        else:
            judge_str = "N/A"

        print(f"{case_name:<42} | {schema_str:<7} | {guard_str:<9} | {judge_str:<18}")

    print("\n--------------------------------------------------------------------------------")
    print("DETAILED QUALITATIVE LLM JUDGE VERDICTS (PER GOAL & PER FLAG):")
    print("--------------------------------------------------------------------------------")
    for r in reports:
        if r.judge:
            print(f"\n[{r.case_id}]:")
            print("  PER-GOAL EVALUATIONS:")
            for goal_id, p in r.judge.per_goal.items():
                g_m = "MATCH" if p.groundedness_match else "MISMATCH"
                f_m = "MATCH" if p.faithfulness_match else "MISMATCH"
                c_m = "MATCH" if p.coherence_match else "MISMATCH"
                print(f"    - Goal {goal_id}:")
                print(f"        Groundedness: {p.rationale_groundedness} [{g_m}]")
                print(f"        Faithfulness:  {p.evidence_faithfulness} [{f_m}]")
                print(f"        Coherence:     {p.reasoning_coherence} [{c_m}]")
                if p.qualitative_notes:
                    print(f"        Notes: {p.qualitative_notes}")

            if r.judge.flag_evaluations:
                print("  FLAG EVALUATIONS:")
                for f in r.judge.flag_evaluations:
                    q_m = "MATCH" if f.quality_match else "MISMATCH"
                    print(f"    - [{f.flag_type}] '{f.description_excerpt[:50]}...':")
                    print(f"        Reasoning Quality: {f.reasoning_quality} [{q_m}]")
                    if f.qualitative_notes:
                        print(f"        Notes: {f.qualitative_notes}")

            if r.judge.overall_qualitative_summary:
                print(f"  OVERALL SUMMARY: {r.judge.overall_qualitative_summary}")

    print(f"\n================================================================================\n")
