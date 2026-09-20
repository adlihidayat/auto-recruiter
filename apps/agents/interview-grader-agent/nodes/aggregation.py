"""
What: Computes the final candidate report and recommendation (Aggregation step).
Why: Synthesizes the results of all previous calls deterministically and generates a final reasoning summary using an LLM.
Boundaries: Applies formulaic weighting for scores and confidence, maps recommendations strictly by threshold, and uses LLM solely for the plain-language 'why' synthesis.
"""
from typing import Any, Dict
from datetime import datetime
import json
from langsmith import traceable
from ..state import GraderState, FinalReport
from ..prompts.aggregation_prompt import get_aggregation_prompt
from core_ai_lib.shared.clients import gemini_flash_lite

@traceable(name="run_aggregation")
def run_aggregation(state: GraderState) -> dict[str, Any]:
    """
    Final Aggregation (Hybrid code + LLM).
    Combines core analysis, communication, and citations into the final report.
    """
    print("Running aggregation...")
    
    # Extract inputs and meta
    plan_meta = state.get("plan_meta")
    comm_weight = plan_meta.communication_weight if plan_meta and hasattr(plan_meta, 'communication_weight') else (plan_meta.get('communication_weight', 0.5) if isinstance(plan_meta, dict) else 0.5)
    # Ensure comm_weight is parsed as float
    try:
        comm_weight = float(comm_weight)
    except:
        comm_weight = 0.5
    core_weight = 1.0 - comm_weight

    input_goals = state.get("goals", [])

    # 1. Process Core Analysis
    core_analysis = state.get("core_analysis")
    goals_assessed = 0
    goals_total = 0
    total_core_score = 0.0
    core_conf_sum = 0.0
    goal_breakdown = []
    
    conf_map = {"low": 0.3, "medium": 0.7, "high": 1.0}

    if core_analysis:
        goals = core_analysis.goals if hasattr(core_analysis, "goals") else core_analysis.get("goals", [])
        goals_total = len(goals)
        for g in goals:
            g_dict = g.model_dump() if hasattr(g, "model_dump") else g
            goal_breakdown.append(g_dict)
            
            if g_dict.get("addressed") and g_dict.get("score") is not None:
                goals_assessed += 1
                total_core_score += g_dict["score"]
                
                c = g_dict.get("confidence", "high").lower()
                core_conf_sum += conf_map.get(c, 1.0)

    core_score = (total_core_score / goals_assessed) if goals_assessed > 0 else 0.0
    core_conf_avg = (core_conf_sum / goals_assessed) if goals_assessed > 0 else 1.0

    # 2. Process Communication Analysis
    comm_analysis = state.get("communication")
    comm_score = 0.0
    comm_conf_avg = 1.0
    comm_output = None

    if comm_analysis:
        c_out = comm_analysis.communication if hasattr(comm_analysis, "communication") else comm_analysis.get("communication", {})
        comm_output = c_out.model_dump() if hasattr(c_out, "model_dump") else c_out
        traits = comm_output.get("traits", {})
        
        t_assessed = 0
        t_score_sum = 0.0
        t_conf_sum = 0.0
        
        for t_name, t_val in traits.items():
            tv = t_val if isinstance(t_val, dict) else t_val.model_dump()
            if tv.get("addressed") and tv.get("score") is not None:
                t_assessed += 1
                t_score_sum += tv["score"]
                c = tv.get("confidence", "high").lower()
                t_conf_sum += conf_map.get(c, 1.0)
                
        if t_assessed > 0:
            comm_score = t_score_sum / t_assessed
            comm_conf_avg = t_conf_sum / t_assessed

    # 3. Calculate Composites
    composite_score = round((core_weight * core_score) + (comm_weight * comm_score), 1)
    raw_conf = (core_weight * core_conf_avg) + (comm_weight * comm_conf_avg)

    if raw_conf < 0.3:
        overall_confidence = "Low"
    elif raw_conf < 0.8:
        overall_confidence = "Medium"
    else:
        overall_confidence = "High"

    # 4. Categorize Security Findings & Manual Review Items
    confirmed_security_findings = []
    manual_review_items = []
    
    injection_check = state.get("injection_check")
    if injection_check:
        findings = injection_check.injection_findings if hasattr(injection_check, 'injection_findings') else injection_check.get("injection_findings", [])
        for finding in findings:
            finding_dict = finding.model_dump() if hasattr(finding, 'model_dump') else finding
            conf = finding_dict.get("confidence", "high")
            item = {
                "description": finding_dict.get('rationale', ''),
                "quote": finding_dict.get("quote", ""),
                "confidence": conf
            }
            if conf in ["high", "medium"]:
                confirmed_security_findings.append(item)
            else:
                manual_review_items.append(item)

    has_confirmed_security_findings = len(confirmed_security_findings) > 0

    # 5. Recommendation Mapping & Deterministic Scoring Rationale
    total_expected_goals = max(len(input_goals), goals_total)
    has_unaddressed_goals = (goals_assessed < total_expected_goals) or any(
        not g.get("addressed") or g.get("score") is None for g in goal_breakdown
    )

    if composite_score >= 8.0:
        if has_confirmed_security_findings:
            recommendation = "Advance with follow-up"
            recommendation_rationale = f"Advance with follow-up (composite score {composite_score} >= 8.0 threshold, but capped due to detected prompt injection)"
        elif has_unaddressed_goals:
            recommendation = "Advance with follow-up"
            recommendation_rationale = f"Advance with follow-up (composite score {composite_score} >= 8.0 threshold, but capped due to unaddressed goals)"
        else:
            recommendation = "Advance"
            recommendation_rationale = f"Advance (composite score {composite_score} >= 8.0 threshold)"
    elif composite_score >= 3.0:
        recommendation = "Advance with follow-up"
        reasons = [f"composite score {composite_score} is between 3.0 and 7.9 threshold"]
        if has_unaddressed_goals:
            reasons.append("unaddressed goals present")
        if has_confirmed_security_findings:
            reasons.append("prompt injection detected")
        recommendation_rationale = f"Advance with follow-up ({', '.join(reasons)})"
    else:
        recommendation = "Hold"
        reasons = [f"composite score {composite_score} < 3.0 threshold"]
        if has_confirmed_security_findings:
            reasons.append("prompt injection detected")
        recommendation_rationale = f"Hold ({', '.join(reasons)})"

    # 6. LLM Reasoning Generation
    prompt = get_aggregation_prompt()
    
    core_sum = json.dumps([{"goal": g.get("goal_id"), "score": g.get("score"), "rationale": g.get("rationale")} for g in goal_breakdown], indent=2)
    if comm_output:
        overall_data = comm_output.get("overall", {})
        traits_data = comm_output.get("traits", {})
        simplified_comm = {
            "overall": {
                "is_passed": overall_data.get("is_passed") if isinstance(overall_data, dict) else getattr(overall_data, "is_passed", None),
                "rationale": overall_data.get("rationale") if isinstance(overall_data, dict) else getattr(overall_data, "rationale", None)
            },
            "traits": {
                t_name: {
                    "is_passed": t_val.get("is_passed") if isinstance(t_val, dict) else getattr(t_val, "is_passed", None),
                    "rationale": t_val.get("rationale") if isinstance(t_val, dict) else getattr(t_val, "rationale", None)
                }
                for t_name, t_val in traits_data.items()
            }
        }
        comm_sum = json.dumps(simplified_comm, indent=2)
    else:
        comm_sum = "None"
        
    confirmed_sum = json.dumps(confirmed_security_findings, indent=2) if confirmed_security_findings else "None"
    manual_sum = json.dumps(manual_review_items, indent=2) if manual_review_items else "None"
    
    messages = prompt.format_messages(
        recommendation=recommendation,
        recommendation_rationale=recommendation_rationale,
        composite_score=composite_score,
        overall_confidence=overall_confidence,
        core_summary=core_sum,
        communication_summary=comm_sum,
        confirmed_security_findings=confirmed_sum,
        manual_review_items=manual_sum
    )
    result = gemini_flash_lite.invoke(messages)
    
    if isinstance(result.content, str):
        reasoning = result.content.strip()
    elif isinstance(result.content, list):
        reasoning = "".join([c if isinstance(c, str) else c.get("text", "") for c in result.content]).strip()
    else:
        reasoning = str(result.content).strip()

    # 8. Build Final Report
    report = FinalReport(
        overall_confidence=overall_confidence,
        recommendation=recommendation,
        reasoning=reasoning,
        composite_score=composite_score,
        grader_version="v2.0",
        graded_at=datetime.utcnow().isoformat() + "Z"
    )

    return {
        "final_report": report
    }
