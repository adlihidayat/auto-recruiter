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
from apps.agents.shared.clients import gemini_flash_lite

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
    gating_map = {}
    for ig in input_goals:
        ig_dict = ig.model_dump() if hasattr(ig, "model_dump") else ig
        gating_map[ig_dict["goal_id"]] = ig_dict.get("gating", False)

    # 1. Process Core Analysis
    core_analysis = state.get("core_analysis")
    goals_assessed = 0
    goals_total = 0
    total_core_score = 0.0
    core_conf_sum = 0.0
    gating_failed = False
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
                
                # Check gating
                if gating_map.get(g_dict["goal_id"], False):
                    if g_dict["score"] < 6.0:
                        gating_failed = True

    core_score = (total_core_score / goals_assessed) if goals_assessed > 0 else 0.0
    core_conf_avg = (core_conf_sum / goals_assessed) if goals_assessed > 0 else 1.0

    # 2. Process Communication Analysis
    comm_analysis = state.get("communication_analysis")
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

    # 4. Recommendation Mapping
    if composite_score >= 8.0:
        recommendation = "Advance"
    elif composite_score >= 3.0:
        recommendation = "Advance with follow-up"
    else:
        recommendation = "Hold"
        
    if gating_failed:
        recommendation = "Hold"

    # 5. Merge Red Flags
    red_flags = []
    injection_check = state.get("injection_check")
    if injection_check:
        findings = injection_check.injection_findings if hasattr(injection_check, 'injection_findings') else injection_check.get("injection_findings", [])
        for finding in findings:
            finding_dict = finding.model_dump() if hasattr(finding, 'model_dump') else finding
            red_flags.append({
                "description": f"Prompt Injection Detected ({finding_dict.get('layer_detected', 'unknown')}): {finding_dict.get('rationale', '')}",
                "goal_id": finding_dict.get("goal_id"),
                "severity": "critical"
            })

    # 6. Merge Citations
    citations_output = state.get("citations")
    if citations_output:
        cit_dict = citations_output.to_citations_by_goal() if hasattr(citations_output, "to_citations_by_goal") else {}
        for gb in goal_breakdown:
            g_id = gb.get("goal_id")
            if g_id in cit_dict:
                gb["citations"] = cit_dict[g_id].get("citations", [])

    # 7. LLM Reasoning Generation
    prompt = get_aggregation_prompt()
    
    core_sum = json.dumps([{"goal": g.get("goal_id"), "score": g.get("score"), "rationale": g.get("rationale")} for g in goal_breakdown], indent=2)
    comm_sum = json.dumps(comm_output, indent=2) if comm_output else "None"
    rf_sum = json.dumps(red_flags, indent=2)
    
    messages = prompt.format_messages(
        recommendation=recommendation,
        composite_score=composite_score,
        overall_confidence=overall_confidence,
        core_summary=core_sum,
        communication_summary=comm_sum,
        red_flags_summary=rf_sum
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
