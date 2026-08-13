"""
What: Computes the final candidate report and recommendation (Aggregation step).
Why: Synthesizes the results of all previous calls deterministically without incurring additional LLM costs.
Boundaries: Pure Python code; does not make LLM calls or alter the upstream scores/flags (only rolls them up).
"""
from typing import Any
from ..state import GraderState, FinalReport

def run_aggregation(state: GraderState) -> dict[str, Any]:
    """
    Final Aggregation (Pure code, no LLM call).
    Combines core analysis, communication, and citations into the final report.
    """
    print("Running aggregation...")
    
    # Extract existing red flags from core_analysis if present
    core_analysis = state.get("core_analysis")
    red_flags = []
    
    if core_analysis:
        # Handle if core_analysis is Pydantic or dict
        if hasattr(core_analysis, 'red_flags'):
            red_flags.extend(core_analysis.red_flags)
        else:
            red_flags.extend(core_analysis.get("red_flags", []))
            
    # Merge injection findings as red flags
    injection_check = state.get("injection_check")
    if injection_check:
        # Handle if injection_check is Pydantic or dict
        findings = injection_check.injection_findings if hasattr(injection_check, 'injection_findings') else injection_check.get("injection_findings", [])
        
        for finding in findings:
            # Convert finding to RedFlag format
            finding_dict = finding.model_dump() if hasattr(finding, 'model_dump') else finding
            
            # Map injection finding to RedFlag schema
            red_flags.append({
                "description": f"Prompt Injection Detected ({finding_dict.get('layer_detected', 'unknown')}): {finding_dict.get('rationale', '')}",
                "goal_id": finding_dict.get("goal_id"),
                "severity": "critical"
            })
            
    # TODO: Build actual FinalReport
    # For now, return the dummy final_report
    return {
        "final_report": None # Should return a FinalReport instance
    }
