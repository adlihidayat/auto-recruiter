import os
import sys
from dotenv import load_dotenv

load_dotenv("../.env")
sys.path.append("/home/adli/Documents/auto-recruiter")
sys.path.append("/home/adli/Documents/auto-recruiter/apps/agents")

import importlib
state_module = importlib.import_module("question-maker-agent.state")
validate_module = importlib.import_module("question-maker-agent.nodes.validate")

QuestionMakerState = state_module.QuestionMakerState
QuestionItem = state_module.QuestionItem
InterviewGoal = state_module.InterviewGoal
GroundingTheory = state_module.GroundingTheory
validateQuestionSuite = validate_module.validateQuestionSuite

def test_validator():
    goal = InterviewGoal(
        goal_id="g_01",
        topic="Python Asyncio",
        goal="Evaluate candidate's understanding of event loops.",
        interview_time_in_minute=10,
        need_grounding=True
    )
    
    # Passing Question
    q_pass = QuestionItem(
        goal_id="g_01",
        topic="Python Asyncio",
        goal="Evaluate candidate's understanding of event loops.",
        interview_time_in_minute=10,
        suggested_opening="How does the asyncio event loop work?",
        passing_criteria=["Mentions single-threaded scheduling"],
        wrong_answer_signals=["Says it uses OS threads automatically"],
        pushback_triggers=[],
        references=[]
    )
    
    # Layer 1 Failing Question (Missing fields)
    q_fail_layer1 = QuestionItem(
        goal_id="g_02",
        topic="Databases",
        goal="Evaluate SQL",
        interview_time_in_minute=10,
        suggested_opening="",  # Missing!
        passing_criteria=[],   # Missing!
        wrong_answer_signals=[],
        pushback_triggers=[],
        references=[]
    )
    
    state = QuestionMakerState(
        job_name="Test",
        job_description="Test",
        difficulty="mid",
        num_goals=2,
        total_duration_minutes=45,
        goals=[goal],
        meta=None,
        research_brief=[],
        grounding_theories=[],
        generated_questions=[q_pass, q_fail_layer1],
        consolidated_questions=[],
        critic_feedback=None,
        retry_counts={},
        final_suite=None
    )
    
    print("Running validate node...")
    result = validateQuestionSuite(state)
    
    feedback = result.get("critic_feedback")
    print(f"\nOverall Valid: {feedback.get('is_valid')}")
    print(f"Failed Goal IDs: {feedback.get('failed_goal_ids')}")
    for k, v in feedback.get("feedback_per_question", {}).items():
        print(f"Feedback for {k}: {v}")

if __name__ == "__main__":
    test_validator()
