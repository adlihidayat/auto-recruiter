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

@traceable(name="run_citations")
def run_citations(state: GraderState) -> Dict[str, Any]:
    """
    Call 3 - Borderline Evidence Citation.
    Runs in 1 single LLM call for all goals where Call 1's score landed in 4-6 or confidence is low/medium.
    """
    print("Running citations extraction...")

    core_analysis = state.get("core_analysis")
    if not core_analysis:
        print("No core_analysis found in state. Skipping citations.")
        return {"citations": CitationsOutput(goal_citations=[])}

    # Extract goal evaluations from core_analysis (supporting Pydantic vs dict)
    eval_goals: List[Any] = (
        core_analysis.goals
        if hasattr(core_analysis, "goals")
        else core_analysis.get("goals", [])
    )

    # Map input goals by goal_id for fast lookup of interaction_history
    input_goals_map: Dict[str, Any] = {}
    for g in state.get("goals", []):
        gid = g.goal_id if hasattr(g, "goal_id") else g.get("goal_id", "")
        if gid:
            input_goals_map[gid] = g

    # Filter goals needing citations: score in 4-6 OR confidence in low/medium
    target_eval_goals: List[Any] = []
    for eg in eval_goals:
        addressed = eg.addressed if hasattr(eg, "addressed") else eg.get("addressed", True)
        if not addressed:
            continue

        score = eg.score if hasattr(eg, "score") else eg.get("score")
        confidence = eg.confidence if hasattr(eg, "confidence") else eg.get("confidence")

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
    job_name = job_obj.job_name if hasattr(job_obj, "job_name") else job_obj.get("job_name", "") if isinstance(job_obj, dict) else ""
    job_desc = job_obj.job_description if hasattr(job_obj, "job_description") else job_obj.get("job_description", "") if isinstance(job_obj, dict) else ""
    job_context = f"Role: {job_name}\nDescription: {job_desc}"

    # Format all target goals into a single consolidated prompt string
    target_goals_blocks: List[str] = []
    for eg in target_eval_goals:
        gid = eg.goal_id if hasattr(eg, "goal_id") else eg.get("goal_id", "")
        score = eg.score if hasattr(eg, "score") else eg.get("score")
        confidence = eg.confidence if hasattr(eg, "confidence") else eg.get("confidence")
        rationale = eg.rationale if hasattr(eg, "rationale") else eg.get("rationale", "")

        evidence_obj = eg.evidence if hasattr(eg, "evidence") else eg.get("evidence", {})
        claims = evidence_obj.claims if hasattr(evidence_obj, "claims") else evidence_obj.get("claims", []) if isinstance(evidence_obj, dict) else []
        reasoning = evidence_obj.demonstrated_reasoning if hasattr(evidence_obj, "demonstrated_reasoning") else evidence_obj.get("demonstrated_reasoning", []) if isinstance(evidence_obj, dict) else []

        input_goal = input_goals_map.get(gid)
        topic = input_goal.topic if hasattr(input_goal, "topic") else input_goal.get("topic", "") if isinstance(input_goal, dict) else ""
        goal_text = input_goal.goal if hasattr(input_goal, "goal") else input_goal.get("goal", "") if isinstance(input_goal, dict) else ""
        history = input_goal.interaction_history if hasattr(input_goal, "interaction_history") else input_goal.get("interaction_history", []) if isinstance(input_goal, dict) else []

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
            role = turn.role if hasattr(turn, "role") else turn.get("role", "")
            content = turn.content if hasattr(turn, "content") else turn.get("content", "")
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
