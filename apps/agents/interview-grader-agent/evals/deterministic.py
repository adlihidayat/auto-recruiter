"""
What: Code-based deterministic checks for CoreAnalysisOutput per goal and overall.
Why: Fast, zero-cost, objective verification of schema rules, bounds, and security leakage.
Boundaries: Code logic only; does not invoke LLMs or evaluate subjective rationale quality.
"""

from typing import Any, List, Dict
from schemas import DeterministicCheckResult, GoalDeterministicCheck, GoldFacts
import importlib

# Dynamic import for CoreAnalysisOutput
state_module = importlib.import_module("interview-grader-agent.state")
CoreAnalysisOutput = state_module.CoreAnalysisOutput

VALID_CONFIDENCES = {"low", "medium", "high"}
VALID_RESPONSE_TYPES = {
    None,
    "defended_well",
    "defended_with_new_info",
    "conceded_and_corrected",
    "doubled_down_on_wrong_answer",
    "evaded"
}


def _extract_all_strings(obj: Any) -> List[str]:
    """Recursively extracts all string values from a Pydantic object, dict, or list."""
    strings = []
    if isinstance(obj, str):
        strings.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            strings.extend(_extract_all_strings(v))
    elif isinstance(obj, (list, tuple, set)):
        for item in obj:
            strings.extend(_extract_all_strings(item))
    elif hasattr(obj, "model_dump"):
        strings.extend(_extract_all_strings(obj.model_dump()))
    elif hasattr(obj, "__dict__"):
        strings.extend(_extract_all_strings(obj.__dict__))
    return strings


def check_protected_characteristic_leakage(
    output: Any, forbidden_terms: List[str]
) -> List[str]:
    """
    Scans all text fields in the core analysis output for occurrences of forbidden terms.
    Returns a list of detected leaked terms.
    """
    if not forbidden_terms:
        return []
    
    all_texts = " ".join(_extract_all_strings(output)).lower()
    leaked = []
    for term in forbidden_terms:
        if term.lower() in all_texts:
            leaked.append(term)
    return leaked


def run_deterministic_checks(
    output: Any, gold_facts: GoldFacts
) -> DeterministicCheckResult:
    """
    Runs all objective, code-based checks against the output per-goal.
    """
    errors: List[str] = []
    
    # 1. Schema Validation
    schema_valid = isinstance(output, CoreAnalysisOutput)
    if not schema_valid:
        try:
            output = CoreAnalysisOutput.model_validate(output)
            schema_valid = True
        except Exception as e:
            return DeterministicCheckResult(
                schema_valid=False,
                per_goal={},
                protected_characteristic_leaked=False,
                leaked_terms_found=[],
                deterministic_passed=False,
                errors=[f"Failed model_validate: {str(e)}"]
            )
            
    # 2. Per-Goal Deterministic Validation
    per_goal_checks: Dict[str, GoalDeterministicCheck] = {}
    all_goals_passed = True
    
    actual_goals_map = {g.goal_id: g for g in getattr(output, "goals", [])}
    
    for goal_id, gold_g in gold_facts.per_goal.items():
        actual_g = actual_goals_map.get(goal_id)
        
        expected_addressed = bool(gold_g.expected_addressed)
        actual_addressed = bool(getattr(actual_g, "addressed", False)) if actual_g else False
        addressed_match = (expected_addressed == actual_addressed)
        if not addressed_match:
            errors.append(f"Goal {goal_id} addressed mismatch: expected {expected_addressed}, got {actual_addressed}")
            
        # Score in range check
        actual_score = getattr(actual_g, "score", None) if actual_g and actual_addressed else None
        if gold_g.expected_score_range is None:
            score_in_range = (actual_score is None)
        else:
            lo, hi = gold_g.expected_score_range
            score_in_range = (actual_score is not None and lo <= actual_score <= hi)
            
        if not score_in_range and expected_addressed:
            errors.append(f"Goal {goal_id} score {actual_score} out of expected range {gold_g.expected_score_range}")

        # Pushback triggered check - CRITICAL BUG FIX: check actual_pb.triggered, not bool(actual_pb)
        actual_pb = getattr(actual_g, "pushback", None) if actual_g else None
        actual_triggered = bool(getattr(actual_pb, "triggered", False)) if actual_pb else False
        actual_response_type = getattr(actual_pb, "response_type", None) if actual_pb else None
        
        expected_triggered = bool(gold_g.expected_pushback_triggered) if gold_g.expected_pushback_triggered is not None else False
        pushback_triggered_match = (expected_triggered == actual_triggered)
        if not pushback_triggered_match:
            errors.append(f"Goal {goal_id} pushback triggered mismatch: expected {expected_triggered}, got {actual_triggered}")
            
        # Pushback response type match
        if gold_g.expected_response_type is None:
            response_type_match = True  # Not asserted
        else:
            response_type_match = (gold_g.expected_response_type == actual_response_type)
            
        if not response_type_match:
            errors.append(f"Goal {goal_id} response type mismatch: expected '{gold_g.expected_response_type}', got '{actual_response_type}'")
            
        goal_passed = addressed_match and score_in_range and pushback_triggered_match and response_type_match
        if not goal_passed:
            all_goals_passed = False
            
        per_goal_checks[goal_id] = GoalDeterministicCheck(
            addressed_match=addressed_match,
            score_in_range=score_in_range,
            pushback_triggered_match=pushback_triggered_match,
            pushback_response_type_match=response_type_match,
        )

    # 3. Protected Characteristic Leakage Check
    leaked_terms = check_protected_characteristic_leakage(
        output, gold_facts.protected_characteristic_terms
    )
    protected_leaked = len(leaked_terms) > 0
    if protected_leaked:
        errors.append(f"Protected characteristic disclosure leaked into output text: {leaked_terms}")
        
    deterministic_passed = schema_valid and all_goals_passed and not protected_leaked
    
    return DeterministicCheckResult(
        schema_valid=schema_valid,
        per_goal=per_goal_checks,
        protected_characteristic_leaked=protected_leaked,
        leaked_terms_found=leaked_terms,
        deterministic_passed=deterministic_passed,
        errors=errors
    )
