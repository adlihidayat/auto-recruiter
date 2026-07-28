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
    return {
        "final_report": None # Should return a FinalReport instance
    }
