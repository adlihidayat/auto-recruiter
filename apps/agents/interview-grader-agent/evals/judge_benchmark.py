"""
What: Meta-Judge evaluator comparing LLM Judge outputs against Human Ground Truth calibration labels.
Why: Validates whether the LLM-as-a-Judge correctly identifies hallucinations, evidence fabrications, and score contradictions.
Boundaries: Evaluates the LLM Judge quality only; does not grade candidate transcripts directly.
"""
import importlib
from typing import Dict, Any

try:
    from .schemas import (
        JudgeBenchmarkTestCase,
        DimensionAlignmentResult,
        JudgeBenchmarkReport,
        LLMJudgeEvalResult,
    )
    from .llm_judge_eval import evaluate_llm_judge
except (ImportError, ValueError):
    schemas_mod = importlib.import_module("interview-grader-agent.evals.schemas")
    JudgeBenchmarkTestCase = schemas_mod.JudgeBenchmarkTestCase
    DimensionAlignmentResult = schemas_mod.DimensionAlignmentResult
    JudgeBenchmarkReport = schemas_mod.JudgeBenchmarkReport
    LLMJudgeEvalResult = schemas_mod.LLMJudgeEvalResult

    judge_mod = importlib.import_module("interview-grader-agent.evals.llm_judge_eval")
    evaluate_llm_judge = judge_mod.evaluate_llm_judge


def evaluate_meta_judge(
    test_case: JudgeBenchmarkTestCase,
) -> JudgeBenchmarkReport:
    """
    Executes the LLM Judge on a benchmark test case and compares its judgment against human ground truth labels.
    """
    # 1. Run LLM Judge
    llm_judge_result: LLMJudgeEvalResult = evaluate_llm_judge(
        input_state=test_case.input_state,
        output=test_case.core_analysis_payload,
    )

    expected = test_case.expected_judge_truth
    alignments: Dict[str, DimensionAlignmentResult] = {}

    dimensions = [
        ("rationale_groundedness", llm_judge_result.rationale_groundedness, expected.rationale_groundedness),
        ("evidence_faithfulness", llm_judge_result.evidence_faithfulness, expected.evidence_faithfulness),
        ("reasoning_coherence", llm_judge_result.reasoning_coherence, expected.reasoning_coherence),
        ("flag_justification_quality", llm_judge_result.flag_justification_quality, expected.flag_justification_quality),
    ]

    for dim_name, actual_score_obj, human_label in dimensions:
        score_in_range = (
            human_label.min_score <= actual_score_obj.score <= human_label.max_score
        )
        verdict_matched = actual_score_obj.passed == human_label.expected_passed
        is_aligned = score_in_range and verdict_matched

        details = (
            f"LLM score={actual_score_obj.score} (Human expected {human_label.min_score}-{human_label.max_score}) | "
            f"LLM pass={actual_score_obj.passed} (Human expected {human_label.expected_passed})"
        )

        alignments[dim_name] = DimensionAlignmentResult(
            dimension_name=dim_name,
            llm_judge_score=actual_score_obj.score,
            llm_judge_passed=actual_score_obj.passed,
            human_min_score=human_label.min_score,
            human_max_score=human_label.max_score,
            human_expected_passed=human_label.expected_passed,
            score_in_range=score_in_range,
            verdict_matched=verdict_matched,
            aligned=is_aligned,
            details=details,
            llm_rationale=actual_score_obj.rationale,
            human_rationale=human_label.human_rationale,
        )

    # Summary metrics
    aligned_count = sum(1 for dim in alignments.values() if dim.aligned)
    alignment_rate = aligned_count / len(alignments)
    verdict_matched_overall = llm_judge_result.passed == expected.should_pass_overall
    case_overall_aligned = verdict_matched_overall and (alignment_rate >= 0.75)

    return JudgeBenchmarkReport(
        test_case_id=test_case.test_case_id,
        test_case_description=test_case.description,
        overall_aligned=case_overall_aligned,
        score_alignment_rate=alignment_rate,
        verdict_matched=verdict_matched_overall,
        dimension_alignments=alignments,
    )
