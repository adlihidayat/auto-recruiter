"""
What: Layer 1 Deterministic Evaluator for Call 2 Communication node outputs.
Why: Performs pure code verification of Communication node schema, score range, confidence match, and protected characteristic leakage without LLM calls.
Boundaries: Evaluates deterministic rules only; qualitative auditing of the 5 discourse signals is handled by Layer 2 Communication LLM Judge.
"""
import re
from typing import List
from ..state import CommunicationOutput
from .schemas import (
    ExpectedCommunicationTruth,
    DeterministicCheckItem,
    ProtectedCharacteristicViolation,
    DeterministicCommunicationEvalResult,
)
from .deterministic_eval import PROTECTED_CHARACTERISTICS_PATTERN


def scan_communication_for_protected_characteristics(
    output: CommunicationOutput,
) -> List[ProtectedCharacteristicViolation]:
    """
    Scans rationale and 5 signals text fields for protected characteristic disclosures.
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

    comm = output.communication
    if comm:
        if comm.rationale:
            check_text_field("communication.rationale", comm.rationale)

        if comm.signals:
            check_text_field("communication.signals.flow_control", comm.signals.flow_control)
            check_text_field("communication.signals.active_listening", comm.signals.active_listening)
            check_text_field("communication.signals.structure", comm.signals.structure)
            check_text_field("communication.signals.assertiveness", comm.signals.assertiveness)
            check_text_field("communication.signals.objection_handling", comm.signals.objection_handling)

    return violations


def evaluate_communication_deterministic(
    output: CommunicationOutput,
    expected_truth: ExpectedCommunicationTruth,
) -> DeterministicCommunicationEvalResult:
    """
    Executes Layer 1 deterministic evaluation on a CommunicationOutput instance against ground truth.
    """
    check_items: List[DeterministicCheckItem] = []
    comm = output.communication

    if not comm:
        return DeterministicCommunicationEvalResult(
            is_schema_valid=False,
            passed=False,
            pass_rate=0.0,
            total_checks=1,
            passed_checks=0,
            check_items=[
                DeterministicCheckItem(
                    check_name="communication_present",
                    passed=False,
                    details="Communication object was missing from output.",
                )
            ],
            protected_characteristic_violations=[],
        )

    # 1. Addressed Check
    is_addressed_ok = comm.addressed == expected_truth.expected_addressed
    check_items.append(
        DeterministicCheckItem(
            check_name="communication_addressed",
            passed=is_addressed_ok,
            details=f"Expected addressed={expected_truth.expected_addressed}, got {comm.addressed}.",
        )
    )

    # 2. Score Range Check (if addressed)
    if expected_truth.expected_addressed and comm.addressed:
        if comm.score is None:
            check_items.append(
                DeterministicCheckItem(
                    check_name="score_range",
                    passed=False,
                    details="Communication score was None for an addressed assessment.",
                )
            )
        elif expected_truth.min_score is not None and expected_truth.max_score is not None:
            score_in_range = (
                expected_truth.min_score <= comm.score <= expected_truth.max_score
            )
            check_items.append(
                DeterministicCheckItem(
                    check_name="score_range",
                    passed=score_in_range,
                    details=(
                        f"Expected communication score between {expected_truth.min_score} and "
                        f"{expected_truth.max_score}, got {comm.score}."
                    ),
                )
            )

    # 3. Confidence Match Check
    if expected_truth.expected_confidence is not None:
        confidence_ok = comm.confidence == expected_truth.expected_confidence
        check_items.append(
            DeterministicCheckItem(
                check_name="confidence_match",
                passed=confidence_ok,
                details=f"Expected confidence='{expected_truth.expected_confidence}', got '{comm.confidence}'.",
            )
        )

    # 4. Protected Characteristics Leakage Check
    leakage_violations = scan_communication_for_protected_characteristics(output)
    no_leakage = len(leakage_violations) == 0
    check_items.append(
        DeterministicCheckItem(
            check_name="protected_characteristic_leakage",
            passed=no_leakage,
            details=f"Found {len(leakage_violations)} protected characteristic leakage violation(s).",
        )
    )

    total_checks = len(check_items)
    passed_checks = sum(1 for item in check_items if item.passed)
    pass_rate = (passed_checks / total_checks) if total_checks > 0 else 1.0
    all_passed = passed_checks == total_checks

    return DeterministicCommunicationEvalResult(
        is_schema_valid=True,
        passed=all_passed,
        pass_rate=pass_rate,
        total_checks=total_checks,
        passed_checks=passed_checks,
        check_items=check_items,
        protected_characteristic_violations=leakage_violations,
    )
