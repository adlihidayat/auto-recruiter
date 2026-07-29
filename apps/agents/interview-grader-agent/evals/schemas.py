"""
What: Pydantic models for ground truth test cases, deterministic metric results, LLM-as-a-Judge evaluations, and Meta-Judge calibration.
Why: Provides typed contracts for evaluating Call 1 (Core Analysis) outputs and benchmarking the LLM Judge against human ground truth.
Boundaries: Contains only static data validation schemas and models; contains no runtime execution logic.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from ..state import CoreAnalysisOutput, GraderState

# --- Ground Truth Test Case Schemas ---

class ExpectedGoalTruth(BaseModel):
    """Ground truth expected values for a specific goal evaluation."""
    goal_id: str
    min_score: Optional[int] = Field(default=None, description="Minimum acceptable score (inclusive)")
    max_score: Optional[int] = Field(default=None, description="Maximum acceptable score (inclusive)")
    expected_addressed: bool = True
    expected_pushback_triggered: Optional[bool] = None
    expected_pushback_response_type: Optional[str] = None


class ExpectedCoreAnalysisTruth(BaseModel):
    """Ground truth expected values for an entire Core Analysis execution."""
    goals: Dict[str, ExpectedGoalTruth] = Field(
        description="Mapping of goal_id to its expected goal evaluation truth"
    )
    expected_red_flag_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords or key phrases that must appear in red_flags descriptions if caught"
    )
    expected_consistency_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords or key phrases that must appear in consistency_issues descriptions"
    )
    should_have_red_flags: bool = False
    should_have_consistency_issues: bool = False


class CoreAnalysisTestCase(BaseModel):
    """Container holding input state and expected ground truth for a test case."""
    test_case_id: str
    description: str
    input_state: Dict[str, Any]
    ground_truth: ExpectedCoreAnalysisTruth


# --- Layer 1 & Layer 2 Evaluation Result Schemas ---

class DeterministicCheckItem(BaseModel):
    """Result of an individual deterministic code check."""
    check_name: str
    passed: bool
    details: str


class ProtectedCharacteristicViolation(BaseModel):
    """Recorded instance of protected-characteristic text leakage."""
    field_name: str
    leaked_snippet: str
    detected_keyword: str


class DeterministicEvalResult(BaseModel):
    """Summary of Layer 1 deterministic evaluation results."""
    is_schema_valid: bool
    passed: bool
    pass_rate: float
    total_checks: int
    passed_checks: int
    check_items: List[DeterministicCheckItem]
    protected_characteristic_violations: List[ProtectedCharacteristicViolation]


class LLMJudgeScore(BaseModel):
    """LLM Judge score and rationale for a specific quality dimension."""
    dimension_name: str
    score: int = Field(ge=0, le=10, description="Quality rating from 0 to 10")
    passed: bool = Field(description="True if score >= 7")
    rationale: str = Field(description="Detailed justification from LLM Judge")


class LLMJudgeEvalResult(BaseModel):
    """Summary of Layer 2 LLM-as-a-Judge evaluation results."""
    passed: bool
    overall_judge_score: float
    rationale_groundedness: LLMJudgeScore
    evidence_faithfulness: LLMJudgeScore
    reasoning_coherence: LLMJudgeScore
    flag_justification_quality: LLMJudgeScore
    judge_raw_feedback: Optional[str] = None


class TestCaseEvalReport(BaseModel):
    """Combined report for a single test case containing both evaluation layers."""
    test_case_id: str
    test_case_description: str
    overall_passed: bool
    deterministic_eval: DeterministicEvalResult
    llm_judge_eval: Optional[LLMJudgeEvalResult] = None


# --- Meta-Judge Calibration & Benchmark Schemas ---

class HumanJudgeDimensionLabel(BaseModel):
    """Human ground-truth expectations for a single LLM Judge dimension."""
    dimension_name: str
    min_score: int = Field(ge=0, le=10, description="Minimum acceptable judge score")
    max_score: int = Field(ge=0, le=10, description="Maximum acceptable judge score")
    expected_passed: bool = Field(description="Expected pass/fail verdict from human auditor")
    human_rationale: str = Field(description="Human expert explanation for expected grade")


class ExpectedJudgeTruth(BaseModel):
    """Human ground-truth expectations for evaluating an LLM Judge run."""
    rationale_groundedness: HumanJudgeDimensionLabel
    evidence_faithfulness: HumanJudgeDimensionLabel
    reasoning_coherence: HumanJudgeDimensionLabel
    flag_justification_quality: HumanJudgeDimensionLabel
    should_pass_overall: bool


class JudgeBenchmarkTestCase(BaseModel):
    """Test case for benchmarking the LLM Judge against human calibration labels."""
    test_case_id: str
    description: str
    input_state: Dict[str, Any]
    core_analysis_payload: CoreAnalysisOutput
    expected_judge_truth: ExpectedJudgeTruth


class DimensionAlignmentResult(BaseModel):
    """Result of comparing LLM Judge rating vs Human expected range for 1 dimension."""
    dimension_name: str
    llm_judge_score: int
    llm_judge_passed: bool
    human_min_score: int
    human_max_score: int
    human_expected_passed: bool
    score_in_range: bool
    verdict_matched: bool
    aligned: bool
    details: str
    llm_rationale: Optional[str] = None
    human_rationale: Optional[str] = None


class JudgeBenchmarkReport(BaseModel):
    """Overall report comparing LLM Judge against Human Calibration for a benchmark case."""
    test_case_id: str
    test_case_description: str
    overall_aligned: bool
    score_alignment_rate: float
    verdict_matched: bool
    dimension_alignments: Dict[str, DimensionAlignmentResult]


# --- Communication Evaluation Schemas ---

class ExpectedCommunicationTruth(BaseModel):
    """Ground truth expected values for Layer 1 Communication node evaluation."""
    expected_addressed: bool = True
    min_score: Optional[int] = Field(default=None, ge=1, le=10)
    max_score: Optional[int] = Field(default=None, ge=1, le=10)
    expected_confidence: Optional[str] = None


class DeterministicCommunicationEvalResult(BaseModel):
    """Summary of Layer 1 Communication deterministic evaluation results."""
    is_schema_valid: bool
    passed: bool
    pass_rate: float
    total_checks: int
    passed_checks: int
    check_items: List[DeterministicCheckItem]
    protected_characteristic_violations: List[ProtectedCharacteristicViolation]


class CommunicationJudgeScore(BaseModel):
    """LLM Judge score and rationale for 1 of the 5 communication dimensions."""
    signal_name: str
    score: int = Field(ge=0, le=10, description="Quality rating from 0 to 10")
    passed: bool = Field(description="True if score >= 7")
    rationale: str = Field(description="Detailed justification from LLM Judge")


class CommunicationJudgeEvalResult(BaseModel):
    """Summary of Layer 2 Communication LLM-as-a-Judge evaluation results."""
    passed: bool
    overall_judge_score: float
    flow_control: CommunicationJudgeScore
    active_listening: CommunicationJudgeScore
    structure: CommunicationJudgeScore
    assertiveness: CommunicationJudgeScore
    objection_handling: CommunicationJudgeScore
    judge_raw_feedback: Optional[str] = None


class HumanJudgeSignalLabel(BaseModel):
    """Simplified min and max score expected range for a signal."""
    min_score: int = Field(ge=0, le=10)
    max_score: int = Field(ge=0, le=10)


class ExpectedCommunicationJudgeTruth(BaseModel):
    """Human ground-truth expectations for evaluating a Communication LLM Judge run."""
    flow_control: HumanJudgeSignalLabel
    active_listening: HumanJudgeSignalLabel
    structure: HumanJudgeSignalLabel
    assertiveness: HumanJudgeSignalLabel
    objection_handling: HumanJudgeSignalLabel


class CommunicationJudgeBenchmarkTestCase(BaseModel):
    """Test case for benchmarking the Communication LLM Judge against human labels."""
    test_case_id: str
    description: str
    input_state: Dict[str, Any]
    communication_payload: Dict[str, Any]
    expected_judge_truth: ExpectedCommunicationJudgeTruth

