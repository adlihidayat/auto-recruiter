"""
What: Executes Call 2 (Communication & Interpersonal) of the interview grader pipeline.
Why: Evaluates flow control, active listening, structure, assertiveness, and objection handling when plan_meta.communication_weight != 'low'.
Boundaries: Conditionally executed; does not score technical correctness or goal domain criteria.
"""
from typing import Any
from langchain_core.prompts import ChatPromptTemplate
from ..state import GraderState, CommunicationOutput
from apps.agents.shared.clients import gemini_flash_lite

# Initialize structured output runnable using the shared rotating model client
structured_llm_client = gemini_flash_lite.with_structured_output(CommunicationOutput)

def run_communication(state: GraderState) -> dict[str, Any]:
    """
    Call 2 - Communication & Interpersonal.
    Evaluates communication style across full interaction history.
    """
    print("Running communication analysis...")

    from ..prompts.communication_prompt import (
        COMMUNICATION_SYSTEM_PROMPT,
        COMMUNICATION_USER_PROMPT,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", COMMUNICATION_SYSTEM_PROMPT),
        ("user", COMMUNICATION_USER_PROMPT),
    ])

    chain = prompt | structured_llm_client

    job_obj = state.get("job")
    job_name = job_obj.job_name if hasattr(job_obj, "job_name") else job_obj.get("job_name", "") if isinstance(job_obj, dict) else ""
    job_desc = job_obj.job_description if hasattr(job_obj, "job_description") else job_obj.get("job_description", "") if isinstance(job_obj, dict) else ""

    plan_meta_obj = state.get("plan_meta")
    difficulty = plan_meta_obj.difficulty if hasattr(plan_meta_obj, "difficulty") else plan_meta_obj.get("difficulty", "") if isinstance(plan_meta_obj, dict) else ""
    comm_weight = plan_meta_obj.communication_weight if hasattr(plan_meta_obj, "communication_weight") else plan_meta_obj.get("communication_weight", "") if isinstance(plan_meta_obj, dict) else ""

    job_context = f"Role: {job_name}\nDescription: {job_desc}"
    plan_meta_str = f"Difficulty: {difficulty}\nCommunication Weight: {comm_weight}"

    transcript_history = ""
    goals = state.get("goals", [])
    for g in goals:
        goal_id = g.goal_id if hasattr(g, "goal_id") else g.get("goal_id", "")
        topic = g.topic if hasattr(g, "topic") else g.get("topic", "")
        history = g.interaction_history if hasattr(g, "interaction_history") else g.get("interaction_history", [])

        transcript_history += f"\n--- Goal: {goal_id} ({topic}) ---\n"
        for t in history:
            role = t.role if hasattr(t, "role") else t.get("role", "")
            content = t.content if hasattr(t, "content") else t.get("content", "")
            transcript_history += f"[{role.upper()}]: {content}\n"

    result: CommunicationOutput = chain.invoke({
        "job_context": job_context,
        "plan_meta": plan_meta_str,
        "transcript_history": transcript_history,
    })

    return {
        "communication": result.communication
    }
