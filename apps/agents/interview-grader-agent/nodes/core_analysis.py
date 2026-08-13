"""
What: Executes Call 1 (Core Analysis) of the interview grader pipeline.
Why: Extracts evidence from the transcript via LLM, then applies deterministic rules to score goals.
Boundaries: LLM extracts criteria/signal states and turn citations. Deterministic code calculates final scores.
"""
import json
from typing import Any
from langchain_core.prompts import ChatPromptTemplate
from ..state import (
    GraderState, 
    CoreAnalysisOutput, 
    CoreAnalysisExtraction,
    GoalEval,
    CriteriaMatch,
    CriterionMatchDetail,
    ProblemSolvingEval,
    ConsistencyIssue,
    RedFlag
)
from apps.agents.shared.clients import gemini_flash_lite

# Initialize structured output runnable using the shared rotating model client
# Layer 1: Extraction Schema
structured_llm_client = gemini_flash_lite.with_structured_output(CoreAnalysisExtraction)

def run_core_analysis(state: GraderState) -> dict[str, Any]:
    """
    Call 1 - Core Analysis.
    Step 1: LLM extracts evidence mapping to criteria/signal IDs.
    Step 2: Deterministic algorithm calculates score and confidence.
    """
    print("Running core analysis extraction...")
    
    # Create the prompt exactly as required by GEMINI.md constraints
    from ..prompts.core_analysis_prompt import CORE_ANALYSIS_SYSTEM_PROMPT, CORE_ANALYSIS_USER_PROMPT
    prompt = ChatPromptTemplate.from_messages([
        ("system", CORE_ANALYSIS_SYSTEM_PROMPT),
        ("user", CORE_ANALYSIS_USER_PROMPT)
    ])
    
    chain = prompt | structured_llm_client
    
    # Format inputs for the prompt safely
    job = state['job']
    job_name = job.job_name if hasattr(job, 'job_name') else job.get('job_name', '')
    job_desc = job.job_description if hasattr(job, 'job_description') else job.get('job_description', '')
    job_context = f"Role: {job_name}\nDescription: {job_desc}"
    
    plan_meta = state['plan_meta']
    diff = plan_meta.difficulty if hasattr(plan_meta, 'difficulty') else plan_meta.get('difficulty', '')
    comm = plan_meta.communication_weight if hasattr(plan_meta, 'communication_weight') else plan_meta.get('communication_weight', '')
    plan_meta_str = f"Difficulty: {diff}\nCommunication Weight: {comm}"
    
    goals_text = ""
    for g in state['goals']:
        gid = g.goal_id if hasattr(g, 'goal_id') else g.get('goal_id', '')
        topic = g.topic if hasattr(g, 'topic') else g.get('topic', '')
        goals_text += f"\n--- Goal: {gid} ({topic}) ---\n"
        
        # Criteria
        passing_criteria = g.passing_criteria if hasattr(g, 'passing_criteria') else g.get('passing_criteria', [])
        goals_text += "Passing Criteria:\n"
        for pc in passing_criteria:
            pid = pc.id if hasattr(pc, 'id') else pc.get('id', '')
            pcrit = pc.criteria if hasattr(pc, 'criteria') else pc.get('criteria', '')
            goals_text += f"  - [{pid}]: {pcrit}\n"
            
        # Signals
        wrong_signals = g.wrong_answer_signals if hasattr(g, 'wrong_answer_signals') else g.get('wrong_answer_signals', [])
        goals_text += "Wrong Answer Signals:\n"
        for ws in wrong_signals:
            wid = ws.id if hasattr(ws, 'id') else ws.get('id', '')
            wsig = ws.signal if hasattr(ws, 'signal') else ws.get('signal', '')
            goals_text += f"  - [{wid}]: {wsig}\n"
            
        goals_text += "Transcript:\n"
        history = g.interaction_history if hasattr(g, 'interaction_history') else g.get('interaction_history', [])
        for t in history:
            tid = t.turn_id if hasattr(t, 'turn_id') else t.get('turn_id', '')
            role = t.role if hasattr(t, 'role') else t.get('role', '')
            content = t.content if hasattr(t, 'content') else t.get('content', '')
            goals_text += f"[{tid}] {role.upper()}: {content}\n"
    
    # Step 1: Invoke LLM for pure extraction
    extraction_result: CoreAnalysisExtraction = chain.invoke({
        "job_context": job_context,
        "plan_meta": plan_meta_str,
        "goals": goals_text
    })
    
    print("Running core analysis deterministic grading...")
    # Step 2: Deterministic grading
    final_goals = []
    
    for extracted_goal in extraction_result.goals:
        gid = extracted_goal.goal_id
        
        # Find the original goal to get history for verification
        input_goal = None
        for g in state['goals']:
            curr_gid = g.goal_id if hasattr(g, 'goal_id') else g.get('goal_id', '')
            if curr_gid == gid:
                input_goal = g
                break
                
        history_map = {}
        if input_goal:
            history = input_goal.interaction_history if hasattr(input_goal, 'interaction_history') else input_goal.get('interaction_history', [])
            for t in history:
                tid = t.turn_id if hasattr(t, 'turn_id') else t.get('turn_id', '')
                content = t.content if hasattr(t, 'content') else t.get('content', '')
                history_map[tid] = content
        
        passing_met = []
        failed_triggered = []
        
        downgrades = [] # list of ('low', 'reason') or ('medium', 'reason')
        
        any_not_assessed = False
        all_criteria_met = True if extracted_goal.criteria_results else False
        any_met = False
        
        # Process criteria
        for cr in extracted_goal.criteria_results:
            if cr.status == "not_assessed":
                any_not_assessed = True
                downgrades.append(("low", "Criterion not assessed"))
                all_criteria_met = False
            elif cr.status == "met":
                any_met = True
                verified = True
                quote = cr.quote or ""
                turn_id = cr.turn_id or ""
                
                # Verification & Vague Check
                if turn_id in history_map:
                    if quote not in history_map[turn_id]:
                        verified = False
                        downgrades.append(("low", "Quote failed substring check"))
                else:
                    verified = False
                    downgrades.append(("low", "Turn ID not found"))
                    
                if len(quote) < 10 or len(quote.split()) < 2:
                    downgrades.append(("medium", "Evidence quote too short/vague"))
                
                passing_met.append(CriterionMatchDetail(
                    criterion_id=cr.criterion_id,
                    status=cr.status,
                    turn_id=cr.turn_id,
                    quote=quote,
                    verified=verified
                ))
            else:
                all_criteria_met = False
                
        # Process signals
        any_signal_triggered = False
        for sr in extracted_goal.signal_results:
            if sr.triggered:
                any_signal_triggered = True
                verified = True
                quote = sr.quote or ""
                turn_id = sr.turn_id or ""
                
                if turn_id in history_map:
                    if quote not in history_map[turn_id]:
                        verified = False
                        downgrades.append(("low", "Signal quote failed substring check"))
                else:
                    verified = False
                    downgrades.append(("low", "Signal Turn ID not found"))
                
                if len(quote) < 10 or len(quote.split()) < 2:
                    downgrades.append(("medium", "Signal quote too short/vague"))
                    
                failed_triggered.append(CriterionMatchDetail(
                    criterion_id=sr.signal_id,
                    status="triggered",
                    turn_id=sr.turn_id,
                    quote=quote,
                    verified=verified
                ))
                
        if any_met and any_signal_triggered:
            downgrades.append(("medium", "Met criterion and triggered wrong signal co-exist"))
            
        # Calculate continuous score based on assessed criteria and signal penalties
        met = sum(1 for cr in extracted_goal.criteria_results if cr.status == "met")
        assessed = sum(1 for cr in extracted_goal.criteria_results if cr.status in ["met", "unmet"])
        triggered_signals = sum(1 for sr in extracted_goal.signal_results if sr.triggered)

        # 1. Base score from assessed criteria only (not_assessed excluded, not penalized)
        base_score = round((met / assessed) * 10, 1) if assessed > 0 else None

        # 2. Signal penalty — equal severity, but scales down with count
        #    1 signal caps score at 2.0, 2 signals at 0.5, 3+ floors at 0.0
        if triggered_signals > 0:
            cap = max(0.0, 2.0 - (triggered_signals - 1) * 1.5)
            score = min(base_score, cap) if base_score is not None else cap
        else:
            score = base_score
            
            
        # Determine Confidence
        confidence = "high"
        if downgrades:
            has_low = any(d[0] == "low" for d in downgrades)
            if has_low:
                confidence = "low"
            else:
                confidence = "medium"
            
        criteria_match = CriteriaMatch(
            passing_met=passing_met,
            failed_triggered=failed_triggered
        )
        
        final_goals.append(GoalEval(
            goal_id=gid,
            addressed=(assessed > 0 or len(extracted_goal.criteria_results) > 0),
            score=score,
            confidence=confidence,
            criteria_match=criteria_match,
            rationale=extracted_goal.rationale
        ))
        
    final_output = CoreAnalysisOutput(
        goals=final_goals
    )
    
    return {
        "core_analysis": final_output
    }
