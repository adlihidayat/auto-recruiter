"""
What: Executes Call 3 (Borderline Evidence Citation) of the interview grader pipeline.
Why: Provides HR with direct, verifiable transcript quotes for goals that scored in the borderline range (4-6) or had low confidence.
Boundaries: Conditionally executed; does not change the score or confidence, only extracts supporting evidence for existing judgments.
"""
from typing import Any
from ..state import GraderState, CitationsOutput

def run_citations(state: GraderState) -> dict[str, Any]:
    """
    Call 3 - Borderline Evidence Citation.
    Runs only for goals where Call 1's score landed in 4-6 or confidence is low/medium.
    """
    # Placeholder for LLM invocation
    print("Running citations extraction...")
    return {
        "citations": None # Should return a CitationsOutput instance
    }
