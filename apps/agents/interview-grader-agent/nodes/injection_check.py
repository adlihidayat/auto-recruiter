"""
What: Placeholder node for detecting prompt injection in candidate transcripts.
Why: Part of Phase 1 parallel execution. Runs over every candidate turn.
Boundaries: Currently a stub. Does not modify core analysis or communication logic.
"""
from typing import Dict, Any
from ..state import GraderState

def run_injection_check(state: GraderState) -> Dict[str, Any]:
    """
    Stub for the injection check node.
    Currently returns an empty injection_findings list.
    """
    return {
        "injection_check": {
            "injection_findings": []
        }
    }
