"""
What: Implements the Validate Node to perform quality control on the generated question suite.
Why: Acts as a gatekeeper using both deterministic schema checks and qualitative LLM judgment to prevent poor outputs.
Boundaries: Does not generate questions. Only evaluates them and sets critic_feedback.
"""

import logging
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage

from apps.agents.shared.clients import gemini_flash_lite
from ..state import QuestionMakerState, CriticFeedback
from ..prompts.validator_prompt import JUDGE_SYSTEM_INSTRUCTION

logger = logging.getLogger(__name__)

def validateQuestionSuite(state: QuestionMakerState) -> Dict[str, Any]:
    """
    [4] Validator/Critic: 
    Layer 1: Schema validation (checks for empty critical fields).
    Layer 2: LLM evaluation (grades alignment with goal/theory).
    Uses: gemini-3.1-flash-lite.
    """
    generated_questions = state.get("generated_questions", [])
    goals = {g.goal_id: g for g in state.get("goals", [])}
    theories = {t.goal_id: t for t in state.get("grounding_theories", [])}
    
    critic_feedback = {
        "is_valid": True,
        "failed_goal_ids": [],
        "feedback_per_question": {}
    }
    
    structured_judge = gemini_flash_lite.with_structured_output(CriticFeedback)
    sys_msg = SystemMessage(content=JUDGE_SYSTEM_INSTRUCTION)
    
    for question in generated_questions:
        goal_id = question.goal_id
        
        # ---------------------------------------------------------
        # Layer 1: Deterministic Schema Checks
        # ---------------------------------------------------------
        missing_fields = []
        if not question.suggested_opening:
            missing_fields.append("suggested_opening")
        if not question.passing_criteria:
            missing_fields.append("passing_criteria")
        if not question.wrong_answer_signals:
            missing_fields.append("wrong_answer_signals")
            
        if missing_fields:
            critic_feedback["is_valid"] = False
            if goal_id not in critic_feedback["failed_goal_ids"]:
                critic_feedback["failed_goal_ids"].append(goal_id)
            critic_feedback["feedback_per_question"][goal_id] = f"Layer 1 Failure: Missing or empty fields: {', '.join(missing_fields)}"
            continue  # Skip Layer 2 for this question since it's already fundamentally broken
            
        # ---------------------------------------------------------
        # Layer 2: LLM Quality Judge
        # ---------------------------------------------------------
        goal_obj = goals.get(goal_id)
        theory_obj = theories.get(goal_id)
        
        human_content = f"Goal ID: {goal_id}\n"
        if goal_obj:
            human_content += f"Goal: {goal_obj.goal}\n"
        
        if theory_obj:
            human_content += f"\n--- Grounding Theory ---\n{theory_obj.theory}\n"
            
        human_content += "\n--- Generated Question ---\n"
        human_content += f"Suggested Opening: {question.suggested_opening}\n"
        human_content += f"Passing Criteria: {question.passing_criteria}\n"
        human_content += f"Wrong Answer Signals: {question.wrong_answer_signals}\n"
        
        human_msg = HumanMessage(content=human_content)
        
        # Call the LLM Judge
        try:
            feedback_result: CriticFeedback = structured_judge.invoke([sys_msg, human_msg])
            
            checks = feedback_result.checks
            passed_all = (feedback_result.verdict == "pass")
            
            if not passed_all:
                critic_feedback["is_valid"] = False
                if goal_id not in critic_feedback["failed_goal_ids"]:
                    critic_feedback["failed_goal_ids"].append(goal_id)
                # Store the entire checks object to pass feedback back to the generator
                critic_feedback["feedback_per_question"][goal_id] = checks.model_dump()
        except Exception as e:
            # Fallback if the LLM judge fails to parse
            critic_feedback["is_valid"] = False
            if goal_id not in critic_feedback["failed_goal_ids"]:
                critic_feedback["failed_goal_ids"].append(goal_id)
            critic_feedback["feedback_per_question"][goal_id] = f"Layer 2 Failure: Judge crashed. Error: {str(e)}"
            
    # Update retry counts for failed goals
    retry_counts = state.get("retry_counts", {})
    for gid in critic_feedback["failed_goal_ids"]:
        retry_counts[gid] = retry_counts.get(gid, 0) + 1
        
    return {
        "critic_feedback": critic_feedback,
        "retry_counts": retry_counts
    }
