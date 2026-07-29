"""
What: Communication Meta-Judge evaluator comparing LLM Judge outputs against Human Ground Truth calibration labels.
Why: Validates whether the Communication LLM Judge correctly scores the 5 discourse signals across benchmark test cases.
Boundaries: Meta-evaluation module only; evaluates judge quality against human expected labels.
"""
import importlib
from typing import Dict, Any

try:
    from .schemas import (
        CommunicationJudgeBenchmarkTestCase,
        DimensionAlignmentResult,
        JudgeBenchmarkReport,
        CommunicationJudgeEvalResult,
    )
    from .communication_llm_judge_eval import evaluate_communication_llm_judge
except (ImportError, ValueError):
    schemas_mod = importlib.import_module("interview-grader-agent.evals.schemas")
    CommunicationJudgeBenchmarkTestCase = schemas_mod.CommunicationJudgeBenchmarkTestCase
    DimensionAlignmentResult = schemas_mod.DimensionAlignmentResult
    JudgeBenchmarkReport = schemas_mod.JudgeBenchmarkReport
    CommunicationJudgeEvalResult = schemas_mod.CommunicationJudgeEvalResult

    judge_mod = importlib.import_module("interview-grader-agent.evals.communication_llm_judge_eval")
    evaluate_communication_llm_judge = judge_mod.evaluate_communication_llm_judge


def evaluate_communication_meta_judge(
    test_case: CommunicationJudgeBenchmarkTestCase,
) -> JudgeBenchmarkReport:
    """
    Executes the Communication LLM Judge on a benchmark case and compares judgment against human ground truth labels.
    """
    # 1. Run Communication LLM Judge
    llm_judge_result: CommunicationJudgeEvalResult = evaluate_communication_llm_judge(
        input_state=test_case.input_state,
        output=test_case.communication_payload,
    )

    expected = test_case.expected_judge_truth
    dimension_map = {
        "flow_control": (llm_judge_result.flow_control, expected.flow_control),
        "active_listening": (llm_judge_result.active_listening, expected.active_listening),
        "structure": (llm_judge_result.structure, expected.structure),
        "assertiveness": (llm_judge_result.assertiveness, expected.assertiveness),
        "objection_handling": (llm_judge_result.objection_handling, expected.objection_handling),
    }

    dimension_alignments: Dict[str, DimensionAlignmentResult] = {}
    aligned_count = 0

    for dim_name, (actual_score_obj, expected_label) in dimension_map.items():
        actual_score = actual_score_obj.score
        actual_passed = actual_score_obj.passed

        expected_passed = expected_label.min_score >= 7
        score_in_range = (
            expected_label.min_score <= actual_score <= expected_label.max_score
        )
        verdict_matched = actual_passed == expected_passed
        is_dim_aligned = score_in_range and verdict_matched

        if is_dim_aligned:
            aligned_count += 1

        details_str = (
            f"LLM score {actual_score} (Pass: {actual_passed}) vs "
            f"Human range [{expected_label.min_score}-{expected_label.max_score}]."
        )

        dimension_alignments[dim_name] = DimensionAlignmentResult(
            dimension_name=dim_name,
            llm_judge_score=actual_score,
            llm_judge_passed=actual_passed,
            human_min_score=expected_label.min_score,
            human_max_score=expected_label.max_score,
            human_expected_passed=expected_passed,
            score_in_range=score_in_range,
            verdict_matched=verdict_matched,
            aligned=is_dim_aligned,
            details=details_str,
            llm_rationale=actual_score_obj.rationale,
            human_rationale=f"Expected range [{expected_label.min_score}-{expected_label.max_score}]",
        )

    alignment_rate = aligned_count / len(dimension_map)
    overall_aligned = alignment_rate == 1.0
    overall_verdict_matched = llm_judge_result.passed == overall_aligned

    return JudgeBenchmarkReport(
        test_case_id=test_case.test_case_id,
        test_case_description=test_case.description,
        overall_aligned=overall_aligned,
        score_alignment_rate=alignment_rate,
        verdict_matched=overall_verdict_matched,
        dimension_alignments=dimension_alignments,
    )
