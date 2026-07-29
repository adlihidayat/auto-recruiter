"""
What: Layer 2 LLM-as-a-Judge Evaluator for Call 2 Communication output quality.
Why: Audits the 5 discourse signals (flow_control, active_listening, structure, assertiveness, objection_handling) against transcript evidence.
Boundaries: Focuses on qualitative auditing using structured LLM output; deterministic checks are handled in communication_deterministic_eval.py.
"""
import importlib
import json
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

try:
    from ..state import CommunicationOutput
    from .schemas import CommunicationJudgeScore, CommunicationJudgeEvalResult
    from .prompts.communication_judge_prompts import (
        COMMUNICATION_JUDGE_SYSTEM_PROMPT,
        COMMUNICATION_JUDGE_USER_PROMPT,
    )
except (ImportError, ValueError):
    state_mod = importlib.import_module("interview-grader-agent.state")
    CommunicationOutput = state_mod.CommunicationOutput

    schemas_mod = importlib.import_module("interview-grader-agent.evals.schemas")
    CommunicationJudgeScore = schemas_mod.CommunicationJudgeScore
    CommunicationJudgeEvalResult = schemas_mod.CommunicationJudgeEvalResult

    prompts_mod = importlib.import_module("interview-grader-agent.evals.prompts.communication_judge_prompts")
    COMMUNICATION_JUDGE_SYSTEM_PROMPT = prompts_mod.COMMUNICATION_JUDGE_SYSTEM_PROMPT
    COMMUNICATION_JUDGE_USER_PROMPT = prompts_mod.COMMUNICATION_JUDGE_USER_PROMPT

from apps.agents.shared.clients import gemini_flash_lite


class CommunicationJudgeResponse(BaseModel):
    flow_control_score: int = Field(ge=0, le=10)
    flow_control_rationale: str

    active_listening_score: int = Field(ge=0, le=10)
    active_listening_rationale: str

    structure_score: int = Field(ge=0, le=10)
    structure_rationale: str

    assertiveness_score: int = Field(ge=0, le=10)
    assertiveness_rationale: str

    objection_handling_score: int = Field(ge=0, le=10)
    objection_handling_rationale: str


def evaluate_communication_llm_judge(
    input_state: Dict[str, Any],
    output: CommunicationOutput,
) -> CommunicationJudgeEvalResult:
    """
    Executes Layer 2 LLM-as-a-Judge evaluation on a CommunicationOutput instance.
    Audits all 5 discourse signals on a 0-10 scale.
    """
    structured_judge = gemini_flash_lite.with_structured_output(CommunicationJudgeResponse)

    prompt = ChatPromptTemplate.from_messages([
        ("system", COMMUNICATION_JUDGE_SYSTEM_PROMPT),
        ("user", COMMUNICATION_JUDGE_USER_PROMPT),
    ])

    chain = prompt | structured_judge

    job_val = input_state.get("job", {})
    job_name = job_val.job_name if hasattr(job_val, "job_name") else job_val.get("job_name", "") if isinstance(job_val, dict) else ""
    job_desc = job_val.job_description if hasattr(job_val, "job_description") else job_val.get("job_description", "") if isinstance(job_val, dict) else ""
    job_context = f"Role: {job_name}\nDescription: {job_desc}"

    transcript_history = ""
    goals = input_state.get("goals", [])
    for g in goals:
        goal_id = g.goal_id if hasattr(g, "goal_id") else g.get("goal_id", "") if isinstance(g, dict) else ""
        topic = g.topic if hasattr(g, "topic") else g.get("topic", "") if isinstance(g, dict) else ""
        history = g.interaction_history if hasattr(g, "interaction_history") else g.get("interaction_history", []) if isinstance(g, dict) else []

        transcript_history += f"\n--- Goal: {goal_id} ({topic}) ---\n"
        for t in history:
            role = t.role if hasattr(t, "role") else t.get("role", "") if isinstance(t, dict) else ""
            content = t.content if hasattr(t, "content") else t.get("content", "") if isinstance(t, dict) else ""
            transcript_history += f"[{role.upper()}]: {content}\n"

    comm_dict = output.model_dump() if hasattr(output, "model_dump") else output
    comm_json = json.dumps(comm_dict, indent=2)

    raw_judge_response: CommunicationJudgeResponse = chain.invoke({
        "job_context": job_context,
        "transcript_history": transcript_history,
        "communication_json": comm_json,
    })

    flow_control_score = CommunicationJudgeScore(
        signal_name="flow_control",
        score=raw_judge_response.flow_control_score,
        passed=raw_judge_response.flow_control_score >= 7,
        rationale=raw_judge_response.flow_control_rationale,
    )

    active_listening_score = CommunicationJudgeScore(
        signal_name="active_listening",
        score=raw_judge_response.active_listening_score,
        passed=raw_judge_response.active_listening_score >= 7,
        rationale=raw_judge_response.active_listening_rationale,
    )

    structure_score = CommunicationJudgeScore(
        signal_name="structure",
        score=raw_judge_response.structure_score,
        passed=raw_judge_response.structure_score >= 7,
        rationale=raw_judge_response.structure_rationale,
    )

    assertiveness_score = CommunicationJudgeScore(
        signal_name="assertiveness",
        score=raw_judge_response.assertiveness_score,
        passed=raw_judge_response.assertiveness_score >= 7,
        rationale=raw_judge_response.assertiveness_rationale,
    )

    objection_handling_score = CommunicationJudgeScore(
        signal_name="objection_handling",
        score=raw_judge_response.objection_handling_score,
        passed=raw_judge_response.objection_handling_score >= 7,
        rationale=raw_judge_response.objection_handling_rationale,
    )

    scores = [
        raw_judge_response.flow_control_score,
        raw_judge_response.active_listening_score,
        raw_judge_response.structure_score,
        raw_judge_response.assertiveness_score,
        raw_judge_response.objection_handling_score,
    ]
    avg_score = sum(scores) / len(scores)
    all_passed = all(s >= 7 for s in scores)

    return CommunicationJudgeEvalResult(
        passed=all_passed,
        overall_judge_score=avg_score,
        flow_control=flow_control_score,
        active_listening=active_listening_score,
        structure=structure_score,
        assertiveness=assertiveness_score,
        objection_handling=objection_handling_score,
    )
