import json
import re
from typing import Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langsmith import traceable

from ..state import (
    GraderState, 
    CoreAnalysisOutput, 
    GoalExtraction,
    GoalEval,
)
from core_ai_lib.shared.clients import gemini_flash_lite

# Initialize structured output runnable using the shared rotating model client
structured_llm_client = gemini_flash_lite.with_structured_output(GoalExtraction)


@traceable(name="Short Circuit Check", run_type="chain")
def check_transcript_addressed(history: list) -> bool:
    """Checks if the interaction history contains transcript turns."""
    return bool(history)


@traceable(name="LLM Extraction & Quote Verification", run_type="chain")
def extract_and_verify_goal_evidence(
    prompt: ChatPromptTemplate,
    prompt_kwargs: dict,
    history_map: dict,
    gid: str,
    max_retries: int = 3
) -> Optional[GoalExtraction]:
    """
    Invokes LLM for evidence extraction and executes regex quote verification loop.
    """
    current_messages = prompt.format_messages(**prompt_kwargs)
    extracted_goal = None

    for attempt in range(max_retries):
        try:
            extracted_goal = structured_llm_client.invoke(current_messages)
            extracted_goal.goal_id = gid
            
            # Verify quotes
            errors = []
            # Elements
            for cr in extracted_goal.criteria_results:
                for el in cr.elements:
                    if el.status in ["met", "partial"] and el.turn_id and el.quote:
                        if el.turn_id not in history_map:
                            errors.append(f"Turn ID {el.turn_id} not found in transcript.")
                        else:
                            if not re.search(re.escape(el.quote), history_map[el.turn_id], re.IGNORECASE):
                                if not re.search(r'\s+'.join(map(re.escape, el.quote.split())), history_map[el.turn_id], re.IGNORECASE):
                                    errors.append(f"Quote '{el.quote}' not found in turn {el.turn_id}.")
            # Signals
            for sr in extracted_goal.signal_results:
                if sr.triggered and sr.turn_id and sr.quote:
                    if sr.turn_id not in history_map:
                        errors.append(f"Signal Turn ID {sr.turn_id} not found in transcript.")
                    else:
                        if not re.search(re.escape(sr.quote), history_map[sr.turn_id], re.IGNORECASE):
                            if not re.search(r'\s+'.join(map(re.escape, sr.quote.split())), history_map[sr.turn_id], re.IGNORECASE):
                                errors.append(f"Signal Quote '{sr.quote}' not found in turn {sr.turn_id}.")
            
            if not errors:
                break  # Success
                
            error_msg = "Verification failed for the following quotes:\n" + "\n".join(errors) + "\nPlease correct the turn_ids and quotes to match the exact transcript text."
            current_messages.append(AIMessage(content=extracted_goal.model_dump_json()))
            current_messages.append(HumanMessage(content=error_msg))
            
        except Exception as e:
            print(f"Goal {gid} attempt {attempt+1} failed: {e}")

    return extracted_goal


@traceable(name="Deterministic Goal Scoring", run_type="chain")
def calculate_deterministic_score(extracted_goal: GoalExtraction, gid: str) -> GoalEval:
    """
    Computes base element score, applies signal penalties, and returns GoalEval.
    """
    points = 0.0
    assessed_elements = 0
    
    for cr in extracted_goal.criteria_results:
        for el in cr.elements:
            if el.status == "met":
                points += 1.0
                assessed_elements += 1
            elif el.status == "partial":
                points += 0.5
                assessed_elements += 1
            elif el.status == "not_met":
                assessed_elements += 1
                
    total_triggered_signals = 0
    for sr in extracted_goal.signal_results:
        if sr.triggered:
            total_triggered_signals += 1
            
    if assessed_elements == 0:
        return GoalEval(
            goal_id=gid,
            addressed=False,
            score=None,
            criteria_results=extracted_goal.criteria_results,
            signal_results=extracted_goal.signal_results,
            flagged_errors=extracted_goal.flagged_errors,
            injection_attempts=extracted_goal.injection_attempts,
            rationale="Goal was marked not_assessed (no elements evaluated)."
        )
        
    base_score = points / assessed_elements
    penalty = 0.2 * total_triggered_signals
    final_score = max(0.0, base_score - penalty) * 10.0
    
    return GoalEval(
        goal_id=gid,
        addressed=True,
        score=round(final_score, 1),
        criteria_results=extracted_goal.criteria_results,
        signal_results=extracted_goal.signal_results,
        flagged_errors=extracted_goal.flagged_errors,
        injection_attempts=extracted_goal.injection_attempts,
        rationale=extracted_goal.rationale
    )


@traceable(name="Evaluate Goal", run_type="chain")
def evaluate_single_goal(
    g: Any,
    job_name: str,
    job_desc: str,
    diff: str,
    prompt: ChatPromptTemplate
) -> GoalEval:
    """Evaluates a single goal end-to-end (Short circuit check, Extraction, and Scoring)."""
    gid = g.goal_id if hasattr(g, 'goal_id') else g.get('goal_id', '')
    history = g.interaction_history if hasattr(g, 'interaction_history') else g.get('interaction_history', [])
    
    # 1. Short-Circuit for Empty Transcripts
    is_addressed = check_transcript_addressed(history)
    if not is_addressed:
        print(f"Skipping goal {gid} (no interaction history)")
        return GoalEval(
            goal_id=gid,
            addressed=False,
            score=None,
            rationale="Goal was not addressed (empty transcript)."
        )

    history_map = {}
    history_text = ""
    for t in history:
        tid = t.turn_id if hasattr(t, 'turn_id') else t.get('turn_id', '')
        role = t.role if hasattr(t, 'role') else t.get('role', '')
        content = t.content if hasattr(t, 'content') else t.get('content', '')
        history_text += f"[{tid}] {role.upper()}: {content}\n"
        history_map[tid] = content

    topic = g.topic if hasattr(g, 'topic') else g.get('topic', '')
    goal_obj = g.goal if hasattr(g, 'goal') else g.get('goal', '')
    grounding = g.grounding_theory if hasattr(g, 'grounding_theory') else g.get('grounding_theory', '')
    
    passing_criteria = g.passing_criteria if hasattr(g, 'passing_criteria') else g.get('passing_criteria', [])
    criteria_text = ""
    for pc in passing_criteria:
        pid = pc.id if hasattr(pc, 'id') else pc.get('id', '')
        pcrit = pc.criteria if hasattr(pc, 'criteria') else pc.get('criteria', '')
        criteria_text += f"  - [{pid}]: {pcrit}\n"
        
    wrong_signals = g.wrong_answer_signals if hasattr(g, 'wrong_answer_signals') else g.get('wrong_answer_signals', [])
    signals_text = ""
    for ws in wrong_signals:
        wid = ws.id if hasattr(ws, 'id') else ws.get('id', '')
        wsig = ws.signal if hasattr(ws, 'signal') else ws.get('signal', '')
        signals_text += f"  - [{wid}]: {wsig}\n"

    prompt_kwargs = {
        "job_name": job_name,
        "job_description": job_desc,
        "difficulty": diff,
        "goal_id": gid,
        "topic": topic,
        "goal": goal_obj,
        "grounding_theory": grounding,
        "criteria": criteria_text,
        "signals": signals_text,
        "interaction_history": history_text
    }

    # 2. LLM Extraction & Verification
    extracted_goal = extract_and_verify_goal_evidence(prompt, prompt_kwargs, history_map, gid)
    if not extracted_goal:
        return GoalEval(
            goal_id=gid,
            addressed=False,
            score=None,
            rationale="Extraction failed."
        )

    # 3. Deterministic Scoring
    return calculate_deterministic_score(extracted_goal, gid)


@traceable(name="Aggregate Core Analysis Output", run_type="chain")
def aggregate_core_analysis_output(final_goals: List[GoalEval]) -> CoreAnalysisOutput:
    """Aggregates evaluated goals into the final CoreAnalysisOutput."""
    valid_scores = [g.score for g in final_goals if g.score is not None]
    overall_score = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else None
    return CoreAnalysisOutput(overall_score=overall_score, goals=final_goals)


@traceable(name="Core Analysis Node", run_type="chain")
def run_core_analysis(state: GraderState) -> dict[str, Any]:
    """
    Call 1 - Core Analysis (Per-Goal Fan-Out).
    """
    print("Running core analysis extraction per goal...")
    
    from ..prompts.core_analysis_prompt import CORE_ANALYSIS_GOAL_SYSTEM_PROMPT, CORE_ANALYSIS_GOAL_USER_PROMPT
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=CORE_ANALYSIS_GOAL_SYSTEM_PROMPT),
        ("user", CORE_ANALYSIS_GOAL_USER_PROMPT)
    ])
    
    job = state['job']
    job_name = job.job_name if hasattr(job, 'job_name') else job.get('job_name', '')
    job_desc = job.job_description if hasattr(job, 'job_description') else job.get('job_description', '')
    
    plan_meta = state['plan_meta']
    diff = plan_meta.difficulty if hasattr(plan_meta, 'difficulty') else plan_meta.get('difficulty', '')
    
    final_goals = []
    for g in state['goals']:
        goal_eval = evaluate_single_goal(g, job_name, job_desc, diff, prompt)
        final_goals.append(goal_eval)
        
    final_output = aggregate_core_analysis_output(final_goals)
    return {"core_analysis": final_output}
