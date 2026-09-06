"""
What: Executes Call 3 (Borderline Evidence Citation) of the interview grader pipeline.
Why: Provides HR with direct, verifiable transcript quotes for goals that scored in the borderline range (4-6) or had low/medium confidence.
Boundaries: Conditionally executed in 1 single LLM call for all target goals; does not alter scores or confidence.
"""
from typing import Any, Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

from ..state import GraderState, CitationsOutput, GoalInput, GoalEval
from ..prompts.citations_prompt import (
    CITATIONS_SYSTEM_PROMPT,
    CITATIONS_USER_PROMPT,
)
from apps.agents.shared.clients import gemini_flash_lite

# Initialize structured output runnable for Citations Output
structured_citations_client = gemini_flash_lite.with_structured_output(CitationsOutput)

def _get_val(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

@traceable(name="run_citations")
def run_citations(state: GraderState) -> Dict[str, Any]:
    """
    Extracts verbatim transcripts quotes supporting Call 1 score/confidence.
    """
    print("Running citations extraction...")

    core_analysis = state.get("core_analysis")
    if not core_analysis:
        print("No core_analysis found in state. Skipping citations.")
        return {"citations": CitationsOutput(goal_citations=[])}

    # Extract goal evaluations from core_analysis (supporting Pydantic vs dict)
    eval_goals: List[Any] = _get_val(core_analysis, "goals", [])

    # Map input goals by goal_id for fast lookup of interaction_history
    input_goals_map: Dict[str, Any] = {}
    for g in state.get("goals", []):
        gid = _get_val(g, "goal_id", "")
        if gid:
            input_goals_map[gid] = g

    # Filter goals needing citations: score in 4-6 OR confidence in low/medium
    target_eval_goals: List[Any] = []
    for eg in eval_goals:
        addressed = _get_val(eg, "addressed", True)
        if not addressed:
            continue

        score = _get_val(eg, "score")
        confidence = _get_val(eg, "confidence")

        needs_citation = False
        if score is not None and 4 <= score <= 6:
            needs_citation = True
        if confidence in ["low", "medium"]:
            needs_citation = True

        if needs_citation:
            target_eval_goals.append(eg)

    if not target_eval_goals:
        print("No goals meet citation criteria (score 4-6 or low/medium confidence). Bypassing LLM call.")
        return {"citations": CitationsOutput(goal_citations=[])}

    # Job Context
    job_obj = state.get("job")
    job_name = _get_val(job_obj, "job_name", "")
    job_desc = _get_val(job_obj, "job_description", "")
    job_context = f"Role: {job_name}\nDescription: {job_desc}"

    # Format all target goals into a single consolidated prompt string
    target_goals_blocks: List[str] = []
    for eg in target_eval_goals:
        gid = _get_val(eg, "goal_id", "")
        score = _get_val(eg, "score")
        confidence = _get_val(eg, "confidence")
        rationale = _get_val(eg, "rationale", "")

        evidence_obj = _get_val(eg, "evidence", {})
        claims = _get_val(evidence_obj, "claims", [])
        reasoning = _get_val(evidence_obj, "demonstrated_reasoning", [])

        input_goal = input_goals_map.get(gid)
        topic = _get_val(input_goal, "topic", "")
        goal_text = _get_val(input_goal, "goal", "")
        history = _get_val(input_goal, "interaction_history", [])

        block = f"--- Target Goal: {gid} ({topic}) ---\n"
        block += f"Goal Description: {goal_text}\n"
        block += f"Call 1 Score: {score}/10 | Confidence: {confidence}\n"
        block += f"Call 1 Rationale: {rationale}\n"
        if claims:
            block += f"Claims Identified: {', '.join(claims)}\n"
        if reasoning:
            block += f"Demonstrated Reasoning: {', '.join(reasoning)}\n"

        block += "\nInteraction History for this Goal:\n"
        for t_idx, turn in enumerate(history, start=1):
            role = _get_val(turn, "role", "")
            content = _get_val(turn, "content", "")
            block += f"  [Turn {t_idx} - {role.upper()}]: {content}\n"

        target_goals_blocks.append(block)

    target_goals_text = "\n".join(target_goals_blocks)

    prompt = ChatPromptTemplate.from_messages([
        ("system", CITATIONS_SYSTEM_PROMPT),
        ("user", CITATIONS_USER_PROMPT),
    ])

    chain = prompt | structured_citations_client

    print(f"Extracting citations in 1 LLM pass for {len(target_eval_goals)} target goal(s)...")
    result: CitationsOutput = chain.invoke({
        "job_context": job_context,
        "target_goals_text": target_goals_text,
    })

    return {
        "citations": result
    }
