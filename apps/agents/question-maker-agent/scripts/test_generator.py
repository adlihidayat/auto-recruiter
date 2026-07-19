import os
import sys
from dotenv import load_dotenv

load_dotenv("../.env")
sys.path.append("/home/adli/Documents/auto-recruiter")
sys.path.append("/home/adli/Documents/auto-recruiter/apps/agents")

import importlib
state_module = importlib.import_module("question-maker-agent.state")
generator_module = importlib.import_module("question-maker-agent.nodes.generator")

InterviewGoal = state_module.InterviewGoal
GroundingTheory = state_module.GroundingTheory
ReferenceSource = state_module.ReferenceSource
GeneratorState = state_module.GeneratorState
generateQuestionItemFromGoal = generator_module.generateQuestionItemFromGoal

def test_generator():
    goal = InterviewGoal(
        goal_id="g_01",
        topic="Python Asyncio",
        goal="Evaluate candidate's understanding of event loops and coroutines in Python.",
        interview_time_in_minute=10,
        need_grounding=True
    )
    
    theory = GroundingTheory(
        goal_id="g_01",
        theory="The event loop is the core of asyncio. Coroutines pause execution at await, yielding control to the event loop.",
        references=[
            ReferenceSource(
                url="https://docs.python.org/3/library/asyncio.html",
                title="Python Asyncio Docs",
                excerpt="Coroutines pause execution at await.",
                matched_query="python asyncio coroutine execution",
                credibility_tier="A",
                corroborated=True
            )
        ]
    )
    
    state = GeneratorState(goal=goal, theory=theory)
    
    print("Running generator node...")
    result = generateQuestionItemFromGoal(state)
    
    questions = result.get("generated_questions", [])
    if questions:
        q = questions[0]
        print("\n--- GENERATED QUESTION ITEM ---")
        print(f"Goal ID: {q.goal_id}")
        print(f"Suggested Opening: {q.suggested_opening}")
        print(f"Passing Criteria: {q.passing_criteria}")
        print(f"Wrong Answer Signals: {q.wrong_answer_signals}")
        print(f"Pushback Triggers: {len(q.pushback_triggers)}")
        print(f"References Carried Over: {len(q.references)}")
    else:
        print("Failed to generate question.")

if __name__ == "__main__":
    test_generator()
