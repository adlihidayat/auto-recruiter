"""
What: Executes Call 1 (Core Analysis) of the interview grader pipeline.
Why: Required for every candidate to extract evidence, score goals against the rubric, evaluate pushback, and scan for red flags in a single pass.
Boundaries: Does not assess discourse-level communication styles or extract verbatim citations; operates only on the predefined rubric criteria.
"""
from typing import Any
from langchain_core.prompts import ChatPromptTemplate
from ..state import GraderState, CoreAnalysisOutput
from apps.agents.shared.clients import gemini_flash_lite

# Initialize structured output runnable using the shared rotating model client
structured_llm_client = gemini_flash_lite.with_structured_output(CoreAnalysisOutput)

def run_core_analysis(state: GraderState) -> dict[str, Any]:
    """
    Call 1 - Core Analysis.
    Evaluates evidence, score, confidence, pushback, consistency, and red flags.
    """
    print("Running core analysis...")
    
    # Create the prompt exactly as required by GEMINI.md constraints
    from ..prompts.core_analysis_prompt import CORE_ANALYSIS_SYSTEM_PROMPT, CORE_ANALYSIS_USER_PROMPT
    prompt = ChatPromptTemplate.from_messages([
        ("system", CORE_ANALYSIS_SYSTEM_PROMPT),
        ("user", CORE_ANALYSIS_USER_PROMPT)
    ])
    
    chain = prompt | structured_llm_client
    
    # Format inputs for the prompt safely
    job_context = f"Role: {state['job'].job_name}\nDescription: {state['job'].job_description}"
    plan_meta_str = f"Difficulty: {state['plan_meta'].difficulty}\nCommunication Weight: {state['plan_meta'].communication_weight}"
    
    goals_text = ""
    for g in state['goals']:
        goals_text += f"\n--- Goal: {g.goal_id} ({g.topic}) ---\n"
        goals_text += f"Passing Criteria: {g.passing_criteria}\n"
        goals_text += f"Wrong Answer Signals: {g.wrong_answer_signals}\n"
        goals_text += f"Pushback Triggers: {[p.model_dump_json() for p in g.pushback_triggers]}\n"
        goals_text += "Transcript:\n"
        for t in g.interaction_history:
            goals_text += f"[{t.role.upper()}]: {t.content}\n"
    
    # Invoke the chain
    result = chain.invoke({
        "job_context": job_context,
        "plan_meta": plan_meta_str,
        "goals": goals_text
    })
    
    return {
        "core_analysis": result
    }
