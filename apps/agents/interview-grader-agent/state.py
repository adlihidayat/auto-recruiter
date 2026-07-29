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
    role: str
    content: str

class GoalInput(BaseModel):
    goal_id: str
    topic: str
    goal: str
    passing_criteria: List[str]
    wrong_answer_signals: List[str]
    pushback_triggers: List[Union[PushbackTrigger, str, Dict[str, Any]]] = Field(default_factory=list)
    grounding_theory: str
    weight: float = 1.0
    gating: bool = False
    interaction_history: List[Interaction]

# --- Output Schemas (Call 1) ---

class Evidence(BaseModel):
    claims: List[str]
    demonstrated_reasoning: List[str]
    specificity: str

class PushbackEval(BaseModel):
    triggered: bool
    response_type: Optional[str] = None

class CriteriaMatch(BaseModel):
    passing_met: List[str]
    failed_triggered: List[str]

class GoalEval(BaseModel):
    goal_id: str
    addressed: bool
    evidence: Optional[Evidence] = None
    pushback: Optional[PushbackEval] = None
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

class CommSignals(BaseModel):
    flow_control: str
    active_listening: str
    structure: str
    assertiveness: str
    objection_handling: str

class CommunicationEval(BaseModel):
    addressed: bool
    score: Optional[int] = None
    confidence: Optional[str] = None
    signals: Optional[CommSignals] = None
    rationale: Optional[str] = None

class CommunicationOutput(BaseModel):
    communication: CommunicationEval

# --- Output Schemas (Call 3) ---

class Citation(BaseModel):
    goal_id: str
    quote: str

class CitationsOutput(BaseModel):
    # Dict mapping goal_id to a dict containing a list of citations
    # e.g. {"g_02": {"citations": [{"goal_id": "g_02", "quote": "..."}]}}
    citations_by_goal: Dict[str, Dict[str, List[Citation]]]

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
    communication: Optional[CommunicationEval] = None
    consistency_issues: List[ConsistencyIssue]
    red_flags: List[RedFlag]
    standout_quote: Optional[str] = None
    grader_version: str
    graded_at: str

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
    citations: Optional[CitationsOutput]
    
    # Final
    final_report: Optional[FinalReport]
