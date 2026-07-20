"""
What: Implements the Assemble Node for the question-maker-agent.
Why: Structures the final JSON output into the official QuestionSuite schema and deduplicates questions by goal_id.
Boundaries: Formatting only (no model calls). Does not generate or validate questions.
"""

from typing import Dict, Any
from ..state import QuestionMakerState, QuestionSuite

def assemble_node(state: QuestionMakerState) -> Dict[str, Any]:
    generated = state.get("generated_questions", [])
    
    # Deduplicate keeping the latest generated item for each goal_id
    latest_questions = {}
    for q in generated:
        latest_questions[q.goal_id] = q
        
    # Sort them back by original goal order
    goals = state.get("goals", [])
    ordered_questions = []
    
    for goal in goals:
        if goal.goal_id in latest_questions:
            ordered_questions.append(latest_questions[goal.goal_id])
            
    # If there are any questions not in the goals list (unlikely), append them
    for goal_id, q in latest_questions.items():
        if q not in ordered_questions:
            ordered_questions.append(q)
            
    final_suite = QuestionSuite(questions=ordered_questions)
    
    return {"final_suite": final_suite}
