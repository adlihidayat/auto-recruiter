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
        references=theory.references if theory else []
    )
    
    return {"generated_questions": [generatedQuestionItem]}
