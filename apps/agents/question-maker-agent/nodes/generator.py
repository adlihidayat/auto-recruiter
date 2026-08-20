"""
What: Implements the Generator Node to create a full plan/question for a specific interview goal.
Why: Synthesizes the InterviewGoal and GroundingTheory (if any) into a structured QuestionItem.
Boundaries: Generates raw question items only. Does not handle cross-question deduplication or validation.
"""

from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from apps.agents.shared.clients import gemini_flash_lite
from ..state import GeneratorState, QuestionItem, GeneratedQuestionContent
from ..prompts.generator_prompt import GENERATOR_SYSTEM_INSTRUCTION

def generateQuestionItemFromGoal(state: GeneratorState) -> Dict[str, Any]:
    """
    Generates a structured QuestionItem grounded in retrieved theory (if provided).
    
    Args:
        state: The GeneratorState containing the goal and optional theory.
        
    Returns:
        A dictionary containing the generated QuestionItem under 'generated_questions'.
    """
    goal = state["goal"]
    theory = state.get("theory")
    
    systemInstructionPrompt = SystemMessage(content=GENERATOR_SYSTEM_INSTRUCTION)
    
    # Construct the input payload
    formattedGoalAndTheoryContext = f"Goal ID: {goal.goal_id}\n"
    formattedGoalAndTheoryContext += f"Topic: {goal.topic}\n"
    formattedGoalAndTheoryContext += f"Goal: {goal.goal}\n"
    formattedGoalAndTheoryContext += f"Time Budget: {goal.interview_time_in_minute} minutes\n"
    
    if theory:
        formattedGoalAndTheoryContext += "\n--- Grounding Theory ---\n"
        formattedGoalAndTheoryContext += theory.theory + "\n"
        
        if theory.references:
            formattedGoalAndTheoryContext += "\n--- References to Map ---\n"
            for i, ref in enumerate(theory.references):
                formattedGoalAndTheoryContext += f"[{i+1}] Title: {ref.title} | URL: {ref.url} | Credibility: {ref.credibility_tier} | Corroborated: {ref.corroborated}\n"
                formattedGoalAndTheoryContext += f"    Excerpt: {ref.excerpt}\n"
                formattedGoalAndTheoryContext += f"    Matched Query: {ref.matched_query}\n"
    else:
        formattedGoalAndTheoryContext += "\n--- Grounding Theory ---\nNone provided. Rely on general best practices.\n"

    critic_feedback = state.get("critic_feedback")
    previous_generation = state.get("previous_generation")
    
    if critic_feedback or previous_generation:
        formattedGoalAndTheoryContext += "\n\n========================================\n"
        formattedGoalAndTheoryContext += "CRITIC FEEDBACK FROM PREVIOUS ATTEMPT\n"
        formattedGoalAndTheoryContext += "========================================\n"
        formattedGoalAndTheoryContext += "Your previous generation failed validation. You MUST fix the issues listed below.\n\n"
        
        if critic_feedback:
            formattedGoalAndTheoryContext += "--- FEEDBACK ---\n"
            import json
            # critic_feedback might be a dict or a string depending on the error
            if isinstance(critic_feedback, dict):
                formattedGoalAndTheoryContext += json.dumps(critic_feedback, indent=2) + "\n"
            else:
                formattedGoalAndTheoryContext += str(critic_feedback) + "\n"
                
        if previous_generation:
            formattedGoalAndTheoryContext += "\n--- YOUR PREVIOUS (FAILED) GENERATION ---\n"
            formattedGoalAndTheoryContext += previous_generation.model_dump_json(indent=2) + "\n"

    humanContextPrompt = HumanMessage(content=formattedGoalAndTheoryContext)
    
    structuredGeneratorModel = gemini_flash_lite.with_structured_output(GeneratedQuestionContent)
    generatedContent: GeneratedQuestionContent = structuredGeneratorModel.invoke([systemInstructionPrompt, humanContextPrompt])
    
    generatedQuestionItem = QuestionItem(
        goal_id=goal.goal_id,
        topic=goal.topic,
        goal=goal.goal,
        interview_time_in_minute=goal.interview_time_in_minute,
        suggested_opening=generatedContent.suggested_opening,
        passing_criteria=generatedContent.passing_criteria,
        pushback_triggers=generatedContent.pushback_triggers,
        wrong_answer_signals=generatedContent.wrong_answer_signals,
        grounding_theory=theory.theory if theory else None
    )
    
    return {"generated_questions": [generatedQuestionItem]}
