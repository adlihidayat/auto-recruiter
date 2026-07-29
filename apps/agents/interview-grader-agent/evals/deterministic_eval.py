"""
What: Layer 1 Deterministic Evaluator for Core Analysis outputs.
Why: Performs pure code verification of output scores, pushback enums, flag detections, and protected characteristic leakage without LLM calls.
Boundaries: Evaluates deterministic rules only; qualitative groundedness and reasoning coherence are handled by Layer 2 LLM Judge.
"""
import re
from typing import List, Dict, Any
from ..state import CoreAnalysisOutput
from .schemas import (
    ExpectedCoreAnalysisTruth,
    DeterministicCheckItem,
    ProtectedCharacteristicViolation,
    DeterministicEvalResult,
)

# Regex pattern set covering protected characteristics disclosure terms
PROTECTED_CHARACTERISTICS_PATTERN = re.compile(
    r"\b("
    r"age|elderly|young|old|religion|religious|christian|muslim|jewish|hindu|buddhist|atheist|"
    r"race|racial|ethnicity|white|black|asian|hispanic|latino|indigenous|"
    r"gender|female|male|transgender|non-binary|sex|sexuality|sexual orientation|"
    r"disability|disabled|handicap|wheelchair|autism|adhd|"
    r"pregnant|pregnancy|maternity|paternity|mother|father|children|family status|marital status|married|single"
    r")\b",
    re.IGNORECASE,
)


def scan_for_protected_characteristics(
    output: CoreAnalysisOutput,
) -> List[ProtectedCharacteristicViolation]:
    """
    Scans all human-readable text fields in CoreAnalysisOutput for protected characteristic disclosures.
    
    Returns a list of ProtectedCharacteristicViolation records if any prohibited keywords are found.
    """
    violations: List[ProtectedCharacteristicViolation] = []

    def check_text_field(field_name: str, text_content: str) -> None:
        if not text_content:
            return
        matches = PROTECTED_CHARACTERISTICS_PATTERN.findall(text_content)
        for match in matches:
            violations.append(
                ProtectedCharacteristicViolation(
                    field_name=field_name,
                    leaked_snippet=text_content[:150],
                    detected_keyword=match,
                )
            )

    # 1. Scan per-goal text fields
    for goal_eval in output.goals:
        goal_prefix = f"goals[{goal_eval.goal_id}]"
        if goal_eval.rationale:
            check_text_field(f"{goal_prefix}.rationale", goal_eval.rationale)
        if goal_eval.evidence:
            for index, claim in enumerate(goal_eval.evidence.claims):
                check_text_field(f"{goal_prefix}.evidence.claims[{index}]", claim)
            for index, reasoning in enumerate(goal_eval.evidence.demonstrated_reasoning):
                check_text_field(f"{goal_prefix}.evidence.demonstrated_reasoning[{index}]", reasoning)

    # 2. Scan problem solving rationale
    if output.problem_solving_under_ambiguity and output.problem_solving_under_ambiguity.rationale:
        check_text_field("problem_solving_under_ambiguity.rationale", output.problem_solving_under_ambiguity.rationale)

    # 3. Scan red flags
    for index, red_flag in enumerate(output.red_flags):
        check_text_field(f"red_flags[{index}].description", red_flag.description)

    # 4. Scan consistency issues
    for index, consistency_issue in enumerate(output.consistency_issues):
        check_text_field(f"consistency_issues[{index}].description", consistency_issue.description)

    return violations


def evaluate_deterministic(
    output: CoreAnalysisOutput,
    expected_truth: ExpectedCoreAnalysisTruth,
) -> DeterministicEvalResult:
    """
    Executes Layer 1 deterministic evaluation on a CoreAnalysisOutput instance against ground truth.
    
    Checks score ranges, pushback booleans/enums, red flag catches, consistency issue catches,
    and protected characteristic leakage.
    """
    check_items: List[DeterministicCheckItem] = []

    # 1. Goal Score Range Checks
    goal_map = {goal.goal_id: goal for goal in output.goals}
    for expected_goal_id, expected_goal_truth in expected_truth.goals.items():
        actual_goal = goal_map.get(expected_goal_id)

        if not actual_goal:
            check_items.append(
                DeterministicCheckItem(
                    check_name=f"goal_present[{expected_goal_id}]",
                    passed=False,
                    details=f"Goal {expected_goal_id} was missing from output.",
                )
            )
            continue

        # Addressed status check
        is_addressed_ok = actual_goal.addressed == expected_goal_truth.expected_addressed
        check_items.append(
            DeterministicCheckItem(
                check_name=f"goal_addressed[{expected_goal_id}]",
                passed=is_addressed_ok,
                details=f"Expected addressed={expected_goal_truth.expected_addressed}, got {actual_goal.addressed}.",
            )
        )

        # Score range check if addressed
        if expected_goal_truth.expected_addressed and actual_goal.addressed:
            actual_score = actual_goal.score
            if actual_score is None:
                check_items.append(
                    DeterministicCheckItem(
                        check_name=f"score_range[{expected_goal_id}]",
                        passed=False,
                        details="Score was None for an addressed goal.",
                    )
                )
            else:
                if expected_goal_truth.min_score is not None and expected_goal_truth.max_score is not None:
                    score_in_range = (
                        expected_goal_truth.min_score <= actual_score <= expected_goal_truth.max_score
                    )
                    check_items.append(
                        DeterministicCheckItem(
                            check_name=f"score_range[{expected_goal_id}]",
                            passed=score_in_range,
                            details=(
                                f"Expected score between {expected_goal_truth.min_score} and "
                                f"{expected_goal_truth.max_score}, got {actual_score}."
                            ),
                        )
                    )

        # Pushback triggered check
        if expected_goal_truth.expected_pushback_triggered is not None:
            actual_triggered = actual_goal.pushback.triggered if actual_goal.pushback else False
            pushback_triggered_ok = (
                actual_triggered == expected_goal_truth.expected_pushback_triggered
            )
            check_items.append(
                DeterministicCheckItem(
                    check_name=f"pushback_triggered[{expected_goal_id}]",
                    passed=pushback_triggered_ok,
                    details=(
                        f"Expected pushback triggered={expected_goal_truth.expected_pushback_triggered}, "
                        f"got {actual_triggered}."
                    ),
                )
            )

        # Pushback response type check
        if expected_goal_truth.expected_pushback_response_type is not None:
            actual_response_type = (
                actual_goal.pushback.response_type if actual_goal.pushback else None
            )
            response_type_ok = (
                actual_response_type == expected_goal_truth.expected_pushback_response_type
            )
            check_items.append(
                DeterministicCheckItem(
                    check_name=f"pushback_response_type[{expected_goal_id}]",
                    passed=response_type_ok,
                    details=(
                        f"Expected pushback response_type='{expected_goal_truth.expected_pushback_response_type}', "
                        f"got '{actual_response_type}'."
                    ),
                )
            )

    # 2. Red Flags Catch Verification
    has_red_flags = len(output.red_flags) > 0
    red_flag_count_ok = has_red_flags == expected_truth.should_have_red_flags
    check_items.append(
        DeterministicCheckItem(
            check_name="red_flags_presence",
            passed=red_flag_count_ok,
            details=f"Expected red flags presence={expected_truth.should_have_red_flags}, got {has_red_flags}.",
        )
    )

    if expected_truth.expected_red_flag_keywords:
        combined_red_flag_text = " ".join([rf.description for rf in output.red_flags]).lower()
        matched_keywords = [
            keyword for keyword in expected_truth.expected_red_flag_keywords
            if keyword.lower() in combined_red_flag_text
        ]
        any_matched = len(matched_keywords) > 0
        check_items.append(
            DeterministicCheckItem(
                check_name="red_flag_keyword_matched",
                passed=any_matched,
                details=(
                    f"Matched keywords {matched_keywords} out of expected "
                    f"{expected_truth.expected_red_flag_keywords} in red flags text."
                ),
            )
        )

    # 3. Consistency Issues Catch Verification
    has_consistency_issues = len(output.consistency_issues) > 0
    consistency_count_ok = has_consistency_issues == expected_truth.should_have_consistency_issues
    check_items.append(
        DeterministicCheckItem(
            check_name="consistency_issues_presence",
            passed=consistency_count_ok,
            details=(
                f"Expected consistency issues presence={expected_truth.should_have_consistency_issues}, "
                f"got {has_consistency_issues}."
            ),
        )
    )

    if expected_truth.expected_consistency_keywords:
        combined_consistency_text = " ".join(
            [ci.description for ci in output.consistency_issues]
        ).lower()
        for keyword in expected_truth.expected_consistency_keywords:
            keyword_found = keyword.lower() in combined_consistency_text
            check_items.append(
                DeterministicCheckItem(
                    check_name=f"consistency_keyword[{keyword}]",
                    passed=keyword_found,
                    details=f"Keyword '{keyword}' found in consistency issues text: {keyword_found}.",
                )
            )

    # 4. Protected Characteristics Leakage Check
    leakage_violations = scan_for_protected_characteristics(output)
    no_leakage = len(leakage_violations) == 0
    check_items.append(
        DeterministicCheckItem(
            check_name="protected_characteristic_leakage",
            passed=no_leakage,
            details=f"Found {len(leakage_violations)} protected characteristic leakage violation(s).",
        )
    )

    # 5. Summarize Results
    total_checks = len(check_items)
    passed_checks = sum(1 for item in check_items if item.passed)
    pass_rate = (passed_checks / total_checks) if total_checks > 0 else 1.0
    all_passed = passed_checks == total_checks

    return DeterministicEvalResult(
        is_schema_valid=True,
        passed=all_passed,
        pass_rate=pass_rate,
        total_checks=total_checks,
        passed_checks=passed_checks,
        check_items=check_items,
        protected_characteristic_violations=leakage_violations,
    )
