"""
What: Layer 2 LLM-as-a-Judge Evaluator for Core Analysis output quality.
Why: Evaluates qualitative aspects such as rationale groundedness, evidence faithfulness, reasoning coherence, and flag justification quality.
Boundaries: Focuses on qualitative auditing using structured LLM output; deterministic checks are handled in deterministic_eval.py.
"""
import importlib
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

try:
    from ..state import GraderState, CoreAnalysisOutput
    from .schemas import LLMJudgeScore, LLMJudgeEvalResult
    from .prompts.judge_prompts import (
        CORE_ANALYSIS_JUDGE_SYSTEM_PROMPT,
        CORE_ANALYSIS_JUDGE_USER_PROMPT,
    )
except (ImportError, ValueError):
    state_mod = importlib.import_module("interview-grader-agent.state")
    GraderState = state_mod.GraderState
    CoreAnalysisOutput = state_mod.CoreAnalysisOutput

    schemas_mod = importlib.import_module("interview-grader-agent.evals.schemas")
    LLMJudgeScore = schemas_mod.LLMJudgeScore
    LLMJudgeEvalResult = schemas_mod.LLMJudgeEvalResult

    prompts_mod = importlib.import_module("interview-grader-agent.evals.prompts.judge_prompts")
    CORE_ANALYSIS_JUDGE_SYSTEM_PROMPT = prompts_mod.CORE_ANALYSIS_JUDGE_SYSTEM_PROMPT
    CORE_ANALYSIS_JUDGE_USER_PROMPT = prompts_mod.CORE_ANALYSIS_JUDGE_USER_PROMPT

from apps.agents.shared.clients import gemini_flash_lite

# Pydantic schema passed to with_structured_output for the LLM judge
class CoreAnalysisJudgeResponse(BaseModel):
    rationale_groundedness_score: int = Field(ge=0, le=10)
    rationale_groundedness_rationale: str
    
    evidence_faithfulness_score: int = Field(ge=0, le=10)
    evidence_faithfulness_rationale: str
    
    reasoning_coherence_score: int = Field(ge=0, le=10)
    reasoning_coherence_rationale: str
    
    flag_justification_quality_score: int = Field(ge=0, le=10)
    flag_justification_quality_rationale: str
    
    overall_summary: str


structured_judge_client = gemini_flash_lite.with_structured_output(CoreAnalysisJudgeResponse)


def evaluate_llm_judge(
    input_state: GraderState,
    output: CoreAnalysisOutput,
) -> LLMJudgeEvalResult:
    """
    Executes Layer 2 LLM-as-a-Judge evaluation on a CoreAnalysisOutput against the input transcript.
    
    Assesses groundedness, faithfulness, coherence, and flag justification quality.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", CORE_ANALYSIS_JUDGE_SYSTEM_PROMPT),
        ("user", CORE_ANALYSIS_JUDGE_USER_PROMPT),
    ])

    chain = prompt | structured_judge_client

    # Format job context
    job_context = f"Job Name: {input_state['job'].job_name}\nDescription: {input_state['job'].job_description}"
    plan_meta = f"Difficulty: {input_state['plan_meta'].difficulty}\nCommunication Weight: {input_state['plan_meta'].communication_weight}"

    # Format goals and interactions
    goals_and_transcript_text = ""
    for goal in input_state["goals"]:
        goals_and_transcript_text += f"\n--- Goal: {goal.goal_id} ({goal.topic}) ---\n"
        goals_and_transcript_text += f"Passing Criteria: {goal.passing_criteria}\n"
        goals_and_transcript_text += f"Wrong Answer Signals: {goal.wrong_answer_signals}\n"
        goals_and_transcript_text += "Transcript:\n"
        for interaction in goal.interaction_history:
            goals_and_transcript_text += f"[{interaction.role.upper()}]: {interaction.content}\n"

    # Format CoreAnalysisOutput JSON
    core_analysis_json = output.model_dump_json(indent=2)

    # Invoke Judge
    judge_response: CoreAnalysisJudgeResponse = chain.invoke({
        "job_context": job_context,
        "plan_meta": plan_meta,
        "goals_and_transcript": goals_and_transcript_text,
        "core_analysis_json": core_analysis_json,
    })

    # Build LLMJudgeScore components
    groundedness = LLMJudgeScore(
        dimension_name="rationale_groundedness",
        score=judge_response.rationale_groundedness_score,
        passed=judge_response.rationale_groundedness_score >= 7,
        rationale=judge_response.rationale_groundedness_rationale,
    )

    faithfulness = LLMJudgeScore(
        dimension_name="evidence_faithfulness",
        score=judge_response.evidence_faithfulness_score,
        passed=judge_response.evidence_faithfulness_score >= 7,
        rationale=judge_response.evidence_faithfulness_rationale,
    )

    coherence = LLMJudgeScore(
        dimension_name="reasoning_coherence",
        score=judge_response.reasoning_coherence_score,
        passed=judge_response.reasoning_coherence_score >= 7,
        rationale=judge_response.reasoning_coherence_rationale,
    )

    flag_quality = LLMJudgeScore(
        dimension_name="flag_justification_quality",
        score=judge_response.flag_justification_quality_score,
        passed=judge_response.flag_justification_quality_score >= 7,
        rationale=judge_response.flag_justification_quality_rationale,
    )

    overall_score = (
        groundedness.score + faithfulness.score + coherence.score + flag_quality.score
    ) / 4.0

    all_passed = (
        groundedness.passed and faithfulness.passed and coherence.passed and flag_quality.passed
    )

    return LLMJudgeEvalResult(
        passed=all_passed,
        overall_judge_score=overall_score,
        rationale_groundedness=groundedness,
        evidence_faithfulness=faithfulness,
        reasoning_coherence=coherence,
        flag_justification_quality=flag_quality,
        judge_raw_feedback=judge_response.overall_summary,
    )
