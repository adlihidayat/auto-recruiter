"""
What: Defines Pydantic data schemas for GoldFacts (test assertions) and JudgeReportOutput (LLM judge evaluation).
Why: Ensures strict, typed contracts between test cases, deterministic validation, and LLM judge scoring.
Boundaries: Schemas only; does not contain validation logic or LLM calls.
"""

from typing import Dict, List, Optional, Tuple, Literal, Any
from pydantic import BaseModel, Field


# ============================================================================
# 1. GOLD FACTS (Lightweight Test Assertions per Test Case)
# ============================================================================

class GoldGoalAssertion(BaseModel):
    """Assertions for a single goal in a test case."""
    expected_score_range: Optional[Tuple[int, int]] = Field(
        default=None, description="[min, max] score range (1-10)"
    )
    expected_pushback_triggered: Optional[bool] = Field(
        default=None, description="Whether pushback was expected to be triggered"
    )
    expected_response_type: Optional[str] = Field(
        default=None, description="Expected pushback response_type (e.g. conceded_and_corrected)"
    )
    expected_addressed: Optional[bool] = Field(
        default=True, description="Whether the goal should be marked as addressed"
    )


class GoldFacts(BaseModel):
    """Complete assertions for a mock test case."""
    case_id: str = Field(description="Unique identifier for the test case")
    description: str = Field(description="Description of what this case tests")
    per_goal: Dict[str, GoldGoalAssertion] = Field(
        description="Goal ID to assertion mapping"
    )
    expected_consistency_issues: List[str] = Field(
        default_factory=list, description="Descriptions of consistency contradictions expected to be caught"
    )
    expected_red_flags: List[str] = Field(
        default_factory=list, description="Descriptions of red flags (e.g. injection attempts) expected to be caught"
    )
    protected_characteristic_terms: List[str] = Field(
        default_factory=list, description="Keywords/phrases (e.g. 'pregnant', 'religion') that MUST NOT leak into output"
    )
    expected_problem_solving_addressed: Optional[bool] = Field(
        default=None, description="Whether problem solving under ambiguity should be addressed"
    )


# ============================================================================
# 2. DETERMINISTIC CHECK RESULTS (Per Goal & Overall)
# ============================================================================

class GoalDeterministicCheck(BaseModel):
    """Code-computed objective verification for a single goal."""
    addressed_match: bool = Field(description="True if expected_addressed matches actual_addressed")
    score_in_range: bool = Field(description="True if actual_score is within expected_score_range or both None")
    pushback_triggered_match: bool = Field(description="True if expected_pushback_triggered matches actual_triggered")
    pushback_response_type_match: bool = Field(description="True if expected_response_type matches actual_response_type or both None")


class DeterministicCheckResult(BaseModel):
    """Code-based deterministic check results across the entire case."""
    schema_valid: bool = Field(description="Whether the output matched Pydantic CoreAnalysisOutput schema")
    per_goal: Dict[str, GoalDeterministicCheck] = Field(description="Per-goal deterministic validation breakdown")
    protected_characteristic_leaked: bool = Field(description="Whether any forbidden term was found in text fields")
    leaked_terms_found: List[str] = Field(default_factory=list, description="List of leaked terms detected")
    deterministic_passed: bool = Field(description="Overall pass/fail for code-level checks")
    errors: List[str] = Field(default_factory=list, description="Specific error details")


# ============================================================================
# 3. LLM JUDGE SCORECARD SCHEMAS (Strict Literal Types)
# ============================================================================

VerdictLiteral = Literal["pass", "fail", "not_applicable", "ambiguous_gold_fact"]


class AddressedMatch(BaseModel):
    expected: bool
    actual: bool
    verdict: VerdictLiteral


class ScoreReasonableness(BaseModel):
    expected_range: Optional[List[int]] = None
    actual: Optional[int] = None
    verdict: VerdictLiteral


class PushbackClassification(BaseModel):
    expected_triggered: bool
    actual_triggered: bool
    expected_response_type: Optional[str] = None
    actual_response_type: Optional[str] = None
    verdict: VerdictLiteral


class GroundingVerdict(BaseModel):
    verdict: Literal["pass", "fail", "not_applicable"]
    notes: str


class JudgeGoalEvaluation(BaseModel):
    addressed_match: AddressedMatch
    score_reasonableness: ScoreReasonableness
    pushback_classification: PushbackClassification
    rationale_groundedness: GroundingVerdict


class DetectionVerdict(BaseModel):
    expected_count: int
    caught_count: int
    false_positives: List[str] = Field(default_factory=list)
    verdict: Literal["pass", "fail"]


class GuardrailVerdict(BaseModel):
    protected_characteristic_leaked: bool
    injection_influenced_output: bool
    notes: str


class ProblemSolvingAssessment(BaseModel):
    expected_addressed: bool
    actual_addressed: bool
    score_reasonable: bool
    verdict: VerdictLiteral


class LLMJudgeSubjectiveOutput(BaseModel):
    """Subjective outputs produced by the LLM Judge call."""
    rationale_groundedness: Dict[str, GroundingVerdict]
    pushback_ambiguity: Dict[str, Any] = Field(default_factory=dict)
    consistency_issues: List[Any] = Field(default_factory=list)
    red_flags: List[Any] = Field(default_factory=list)
    false_positives: List[Any] = Field(default_factory=list)
    guardrail_protected_characteristic_influenced: bool = False
    guardrail_injection_influenced: bool = False
    guardrail_notes: str = ""
    problem_solving_groundedness_verdict: str = "pass"


class JudgeReportOutput(BaseModel):
    """Complete qualitative evaluation scorecard returned by LLM Judge."""
    case_id: str
    per_goal: Dict[str, JudgeGoalEvaluation] = Field(description="Per-goal evaluation breakdown")
    consistency_detection: DetectionVerdict = Field(description="Consistency issue evaluation")
    red_flag_detection: DetectionVerdict = Field(description="Red flag evaluation")
    guardrail_compliance: GuardrailVerdict = Field(description="Guardrail compliance evaluation")
    problem_solving_assessment: ProblemSolvingAssessment = Field(description="Problem solving assessment evaluation")
    schema_valid: bool = Field(default=True, description="Inherited schema validity flag")
    overall_case_score: int = Field(description="Overall evaluation score (1-10)")
    failure_modes: List[str] = Field(default_factory=list, description="List of failure mode notes if any")
