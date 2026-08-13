"""
What: Defines the Pydantic schemas and LangGraph TypedDict for the interview grader agent's state.
Why: Ensures strict type safety, data validation, and predictable schema contracts across the 3-call pipeline.
Boundaries: Does not contain runtime logic, LLM parsing code, or routing logic; strictly static definitions.
"""
from typing import TypedDict, List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

# --- Input Schemas ---

class JobContext(BaseModel):
    job_name: str
    job_description: str

class PlanMeta(BaseModel):
    communication_weight: str = "low"
    difficulty: str = "senior"

class PushbackTrigger(BaseModel):
    trigger: str
    severity: str
    pushback_type: str

class Interaction(BaseModel):
    turn_id: str
    role: str
    content: str

class PassingCriterion(BaseModel):
    id: str
    criteria: str

class WrongAnswerSignal(BaseModel):
    id: str
    signal: str

class GoalInput(BaseModel):
    goal_id: str
    topic: str
    goal: str
    passing_criteria: List[PassingCriterion]
    wrong_answer_signals: List[WrongAnswerSignal]
    pushback_triggers: List[Union[PushbackTrigger, str, Dict[str, Any]]] = Field(default_factory=list)
    grounding_theory: str
    weight: float = 1.0
    gating: bool = False
    interaction_history: List[Interaction]

# --- LLM Output Schemas (Call 1) ---

class CriterionResult(BaseModel):
    criterion_id: str
    status: str
    turn_id: Optional[str] = None
    quote: Optional[str] = None

class SignalResult(BaseModel):
    signal_id: str
    triggered: bool
    turn_id: Optional[str] = None
    quote: Optional[str] = None

class GoalExtraction(BaseModel):
    goal_id: str
    criteria_results: List[CriterionResult]
    signal_results: List[SignalResult]
    rationale: str

class CoreAnalysisExtraction(BaseModel):
    goals: List[GoalExtraction]

# --- Node Output Schemas (Call 1) ---

class CriterionMatchDetail(BaseModel):
    criterion_id: str
    status: str
    turn_id: Optional[str] = None
    quote: Optional[str] = None
    verified: bool = True

class CriteriaMatch(BaseModel):
    passing_met: List[CriterionMatchDetail]
    failed_triggered: List[CriterionMatchDetail]

class GoalEval(BaseModel):
    goal_id: str
    addressed: bool
    is_passed: Optional[bool] = None
    needs_review: bool = False
    score: Optional[int] = None
    confidence: Optional[str] = None
    criteria_match: Optional[CriteriaMatch] = None
    rationale: Optional[str] = None

class ProblemSolvingEval(BaseModel):
    addressed: bool
    score: Optional[int] = None
    confidence: Optional[str] = None
    rationale: Optional[str] = None

class ConsistencyIssue(BaseModel):
    description: str
    goal_ids_involved: List[str]

class RedFlag(BaseModel):
    description: str
    goal_id: Optional[str] = None
    severity: str

class CoreAnalysisOutput(BaseModel):
    goals: List[GoalEval]
    problem_solving_under_ambiguity: ProblemSolvingEval
    consistency_issues: List[ConsistencyIssue]
    red_flags: List[RedFlag]

# --- Output Schemas (Call 2) ---

# --- LLM Extraction Schemas (Call 2) ---

class CommSignalMatch(BaseModel):
    signal_id: str
    turn_id: str
    quote: str
    rationale: str

class CommTraitExtraction(BaseModel):
    positive: List[CommSignalMatch]
    negative: List[CommSignalMatch]

class CommunicationExtraction(BaseModel):
    active_listening: CommTraitExtraction
    structure: CommTraitExtraction
    assertiveness: CommTraitExtraction
    clarity: CommTraitExtraction

# --- Node Output Schemas (Call 2) ---

class CommEvidence(BaseModel):
    signal_id: str
    turn_id: str
    quote: str
    polarity: str

class CommTraitEval(BaseModel):
    addressed: bool
    is_passed: Optional[bool] = None
    score: Optional[int] = None
    confidence: str
    evidence: List[CommEvidence]
    rationale: str

class CommOverallEval(BaseModel):
    is_passed: Optional[bool] = None
    confidence: str
    traits_passed: int
    traits_failed: int
    traits_not_addressed: int
    rule_applied: str
    rationale: str

class CommunicationOutputData(BaseModel):
    overall: CommOverallEval
    traits: Dict[str, CommTraitEval]

class CommunicationOutput(BaseModel):
    communication: CommunicationOutputData

# --- Output Schemas (Call 3) ---

class Citation(BaseModel):
    goal_id: str
    quote: str
    turn_reference: Optional[str] = None

class GoalCitations(BaseModel):
    goal_id: str
    citations: List[Citation] = Field(default_factory=list)

class CitationsOutput(BaseModel):
    goal_citations: List[GoalCitations] = Field(default_factory=list)

    def to_citations_by_goal(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        Helper method converting to dictionary mapping format:
        e.g. {"g_02": {"citations": [{"goal_id": "g_02", "quote": "...", "turn_reference": "..."}]}}
        """
        res: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        for gc in self.goal_citations:
            res[gc.goal_id] = {
                "citations": [c.model_dump() for c in gc.citations]
            }
        return res

# --- Output Schemas (Aggregation) ---

class FinalReport(BaseModel):
    summary: str
    recommendation: str
    flags: List[str]
    composite_score: float
    overall_confidence: str
    goals_assessed: int
    goals_total: int
    gating_failed: bool
    goal_breakdown: List[Any]  # Can be GoalEval merged with Citations
    problem_solving_under_ambiguity: ProblemSolvingEval
    communication: Optional[CommunicationOutputData] = None
    consistency_issues: List[ConsistencyIssue]
    red_flags: List[RedFlag]
    standout_quote: Optional[str] = None
    grader_version: str
    graded_at: str

# --- Output Schemas (Injection Check) ---

class InjectionFinding(BaseModel):
    goal_id: str
    turn_id: str
    layer_detected: str
    layer_2_score: Optional[float] = None
    confidence: str
    quote: str
    rationale: str

class InjectionCheckOutput(BaseModel):
    injection_findings: List[InjectionFinding] = Field(default_factory=list)

# --- Graph State ---

class GraderState(TypedDict):
    """
    LangGraph state for the interview grader agent.
    """
    # Input
    job: JobContext
    plan_meta: PlanMeta
    goals: List[GoalInput]
    
    # Intermediate / Outputs
    core_analysis: Optional[CoreAnalysisOutput]
    communication_analysis: Optional[CommunicationOutput]
    injection_check: Optional[InjectionCheckOutput]
    citations: Optional[CitationsOutput]
    
    # Final
    final_report: Optional[FinalReport]
