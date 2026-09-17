"""
What: Interactive CLI testing script for the Generator Node and generator_prompt.py.
Why: Allows developers to run custom or template inputs through the Generator node and visually evaluate output quality.
Boundaries: Isolated test script for prompt iteration and quality evaluation; does not run full graph.
"""

import os
import sys
import json
import argparse
from dotenv import load_dotenv

# 1. Setup workspace paths dynamically
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MONOREPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../.."))
AGENTS_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))

if MONOREPO_ROOT not in sys.path:
    sys.path.append(MONOREPO_ROOT)
if AGENTS_ROOT not in sys.path:
    sys.path.append(AGENTS_ROOT)

load_dotenv(os.path.join(MONOREPO_ROOT, ".env"))

import importlib
state_module = importlib.import_module("question-maker-agent.state")
generator_module = importlib.import_module("question-maker-agent.nodes.generator")

InterviewGoal = state_module.InterviewGoal
GroundingTheory = state_module.GroundingTheory
ReferenceSource = state_module.ReferenceSource
GeneratorState = state_module.GeneratorState
PushbackTrigger = state_module.PushbackTrigger
QuestionItem = state_module.QuestionItem
generateQuestionItemFromGoal = generator_module.generateQuestionItemFromGoal


# Pre-configured test scenarios
TEST_SCENARIOS = {
    # "1": {
    #     "name": "Ideal Baseline (Grounded, Mid Time Budget)",
    #     "goal": InterviewGoal(
    #         goal_id="g_01",
    #         topic="REST API Rate Limiting",
    #         goal="Evaluate candidate's understanding of exponential backoff with jitter when handling 429 responses from a third-party API.",
    #         interview_time_in_minute=10,
    #         need_grounding=True
    #     ),
    #     "theory": GroundingTheory(
    #         goal_id="g_01",
    #         theory=(
    #             "When a client receives a 429 Too Many Requests response, it should not retry "
    #             "immediately. Exponential backoff doubles the wait time after each successive "
    #             "failure (e.g., 1s, 2s, 4s, 8s), up to a capped maximum. Adding random jitter to "
    #             "the delay prevents many clients from retrying in synchronized bursts (the "
    #             "'thundering herd' problem). A Retry-After header, when present, should override "
    #             "the client's own computed backoff and be honored directly."
    #         ),
    #         references=[
    #             ReferenceSource(
    #                 url="https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429",
    #                 title="429 Too Many Requests - HTTP",
    #                 excerpt="Servers may include a Retry-After header to indicate how long to wait before retrying.",
    #                 matched_query="429 retry after exponential backoff jitter",
    #                 credibility_tier="A",
    #                 corroborated=True
    #             )
    #         ]
    #     ),
    #     "critic_feedback": None,
    #     "previous_generation": None
    # },
 
    # "2": {
    #     "name": "No Grounding Theory + Very Short Time Budget (fabrication temptation)",
    #     "goal": InterviewGoal(
    #         goal_id="g_02",
    #         topic="Data Structures",
    #         goal="Evaluate candidate's understanding of amortized time complexity for dynamic array (list) append operations.",
    #         interview_time_in_minute=2,
    #         need_grounding=False
    #     ),
    #     "theory": None,
    #     "critic_feedback": None,
    #     "previous_generation": None
    # },
 
    "1": {
        "name": "Visual-Temptation Goal (stack trace, no grounding)",
        "goal": InterviewGoal(
            goal_id="g_03",
            topic="Debugging with Stack Traces",
            goal="Evaluate candidate's ability to read a Python traceback and identify the actual root cause of the exception, as opposed to the line where it surfaced.",
            interview_time_in_minute=6,
            need_grounding=False
        ),
        "theory": None,
        "critic_feedback": None,
        "previous_generation": None
    },
 
    # "4": {
    #     "name": "Narrow Procedural Fact, No Natural Partial-Wrong Version",
    #     "goal": InterviewGoal(
    #         goal_id="g_04",
    #         topic="Data Breach Compliance",
    #         goal="Evaluate whether the candidate knows the mandatory notification timeframe for reporting a confirmed personal data breach to the relevant supervisory authority under GDPR.",
    #         interview_time_in_minute=3,
    #         need_grounding=True
    #     ),
    #     "theory": GroundingTheory(
    #         goal_id="g_04",
    #         theory=(
    #             "Under GDPR Article 33, a data controller who becomes aware of a personal data "
    #             "breach must notify the competent supervisory authority without undue delay and, "
    #             "where feasible, not later than 72 hours after having become aware of it. If "
    #             "notification is not made within 72 hours, it must be accompanied by reasons for "
    #             "the delay."
    #         ),
    #         references=[
    #             ReferenceSource(
    #                 url="https://gdpr-info.eu/art-33-gdpr/",
    #                 title="Art. 33 GDPR - Notification of a personal data breach",
    #                 excerpt="Notification shall be made not later than 72 hours after having become aware of it.",
    #                 matched_query="GDPR breach notification 72 hours",
    #                 credibility_tier="A",
    #                 corroborated=True
    #             )
    #         ]
    #     ),
    #     "critic_feedback": None,
    #     "previous_generation": None
    # },
 
    # "5": {
    #     "name": "Compound Adversarial Retry (empty-array pressure + stale schema in context)",
    #     "goal": InterviewGoal(
    #         goal_id="g_05",
    #         topic="Distributed Locking & Concurrency",
    #         goal="Evaluate whether the candidate knows that the Redlock algorithm requires acquiring the lock across a majority of independent Redis nodes, not just a single node.",
    #         interview_time_in_minute=5,
    #         need_grounding=True
    #     ),
    #     "theory": GroundingTheory(
    #         goal_id="g_05",
    #         theory=(
    #             "The Redlock algorithm acquires a lock by attempting to set the same key with the "
    #             "same random value across N independent Redis nodes, each with a short TTL. The "
    #             "lock is considered acquired only if it was successfully set on a majority "
    #             "(N/2 + 1) of the nodes within a bounded time window. Relying on a single Redis "
    #             "node for locking does not provide this guarantee, since that node is a single "
    #             "point of failure."
    #         ),
    #         references=[
    #             ReferenceSource(
    #                 url="https://redis.io/docs/latest/develop/use/patterns/distributed-locks/",
    #                 title="Distributed Locks with Redis",
    #                 excerpt="The lock is considered acquired when the majority of nodes have set it successfully.",
    #                 matched_query="redis redlock majority quorum nodes",
    #                 credibility_tier="A",
    #                 corroborated=True
    #             )
    #         ]
    #     ),
    #     # Second round: a prior attempt already (correctly) returned an empty
    #     # pushback_triggers array for this narrow, binary-knowledge goal, and the critic
    #     # is pushing back on the emptiness itself rather than on any content problem.
    #     "critic_feedback": {
    #         "pushback_actionability": {
    #             "pass": False,
    #             "issues": [
    #                 "pushback_triggers is empty. Every goal must include at least one "
    #                 "pushback_triggers entry to be considered complete."
    #             ]
    #         }
    #     },
    #     # NOTE: previous_generation intentionally uses the OLD pushback_triggers shape
    #     # (trigger/severity/pushback_type) to simulate a pre-migration record re-entering
    #     # a retry loop. wrong_answer_signals is already in the current plain-string shape.
    #     "previous_generation": QuestionItem(
    #         goal_id="g_05",
    #         topic="Distributed Locking & Concurrency",
    #         goal="Evaluate whether the candidate knows that the Redlock algorithm requires acquiring the lock across a majority of independent Redis nodes, not just a single node.",
    #         interview_time_in_minute=5,
    #         suggested_opening=(
    #             "Say you're implementing a distributed lock using Redis so only one worker "
    #             "processes a given job at a time. Walk me through how you'd make sure the lock "
    #             "is actually safe across multiple Redis nodes, not just reliable on paper."
    #         ),
    #         passing_criteria=[
    #             "States that the lock must be acquired across a majority of independent Redis "
    #             "nodes (not just one), AND explains why a single-node lock is unsafe -- that "
    #             "node becomes a single point of failure"
    #         ],
    #         wrong_answer_signals=[
    #             "Claims acquiring the lock on a single Redis node is sufficient for safety"
    #         ],
    #         pushback_triggers=[],
    #         references=[]
    #     )
    # },
    # "6": {
    #     "name": "Graphic Design - Visual Hierarchy (visual-temptation domain)",
    #     "goal": InterviewGoal(
    #         goal_id="g_06",
    #         topic="Visual Hierarchy in Layout Design",
    #         goal="Evaluate candidate's understanding of how to use size, contrast, and placement to guide a viewer's eye through a poster in a specific intended order.",
    #         interview_time_in_minute=6,
    #         need_grounding=True
    #     ),
    #     "theory": GroundingTheory(
    #         goal_id="g_06",
    #         theory=(
    #             "Visual hierarchy is the deliberate arrangement of elements to guide the order in "
    #             "which a viewer's eye perceives them. The eye is naturally drawn first to the "
    #             "largest element, then to areas of highest contrast (color or value difference "
    #             "against the background), then to elements positioned along common scan paths "
    #             "(e.g., an F-pattern for text-heavy layouts, or a Z-pattern for image-led "
    #             "layouts). Designers create a single dominant focal point, then a secondary "
    #             "element, then supporting details, rather than giving multiple elements equal "
    #             "visual weight -- equal weight forces the viewer to guess where to look first, "
    #             "which increases the time it takes to understand the piece."
    #         ),
    #         references=[
    #             ReferenceSource(
    #                 url="https://www.interaction-design.org/literature/topics/visual-hierarchy",
    #                 title="Visual Hierarchy - Interaction Design Foundation",
    #                 excerpt="Visual hierarchy refers to the arrangement of elements to show their order of importance.",
    #                 matched_query="visual hierarchy size contrast scan pattern",
    #                 credibility_tier="A",
    #                 corroborated=True
    #             )
    #         ]
    #     ),
    #     "critic_feedback": None,
    #     "previous_generation": None
    # },
 
    # "7": {
    #     "name": "Nursing - Five Rights of Medication Administration (rich checklist domain)",
    #     "goal": InterviewGoal(
    #         goal_id="g_07",
    #         topic="Medication Administration Safety",
    #         goal="Evaluate the candidate's understanding of the 'five rights' of medication administration and how each one independently prevents a specific category of medication error.",
    #         interview_time_in_minute=8,
    #         need_grounding=True
    #     ),
    #     "theory": GroundingTheory(
    #         goal_id="g_07",
    #         theory=(
    #             "The five rights of medication administration are a checklist used to prevent "
    #             "medication errors before a dose is given: (1) Right patient -- verified using two "
    #             "identifiers (e.g., name and date of birth), preventing a dose meant for one "
    #             "patient being given to another. (2) Right drug -- confirming the medication "
    #             "matches the order exactly, preventing look-alike/sound-alike drug mix-ups. "
    #             "(3) Right dose -- verifying the calculated amount against the ordered amount, "
    #             "preventing overdose or underdose, especially in weight-based pediatric dosing. "
    #             "(4) Right route -- confirming the method of administration (oral, IV, "
    #             "intramuscular, etc.) matches the order, since the same drug can be dangerous or "
    #             "ineffective by the wrong route. (5) Right time -- administering within the "
    #             "correct scheduled window, since some medications lose efficacy or become unsafe "
    #             "if given too early, too late, or too close to another dose."
    #         ),
    #         references=[
    #             ReferenceSource(
    #                 url="https://www.ncbi.nlm.nih.gov/books/NBK519065/",
    #                 title="Medication Errors - StatPearls",
    #                 excerpt="The five rights are patient, drug, dose, route, and time.",
    #                 matched_query="five rights medication administration nursing",
    #                 credibility_tier="A",
    #                 corroborated=True
    #             )
    #         ]
    #     ),
    #     "critic_feedback": None,
    #     "previous_generation": None
    # },
 
    # "8": {
    #     "name": "Customer Service - De-escalating an Angry Guest (pure judgment, no named facts)",
    #     "goal": InterviewGoal(
    #         goal_id="g_08",
    #         topic="Guest Conflict De-escalation",
    #         goal="Evaluate the candidate's ability to de-escalate an angry hotel guest complaining about a late, incorrect room-service order, while still holding the hotel's actual policy.",
    #         interview_time_in_minute=5,
    #         need_grounding=False
    #     ),
    #     "theory": None,
    #     "critic_feedback": None,
    #     "previous_generation": None
    # }

}


def run_test(scenario_key: str = "all"):
    if scenario_key == "all":
        keys_to_run = list(TEST_SCENARIOS.keys())
    else:
        keys_to_run = [scenario_key]

    for key in keys_to_run:
        scenario = TEST_SCENARIOS.get(key, TEST_SCENARIOS["1"])
        print("\n" + "=" * 80)
        print(f"RUNNING GENERATOR NODE TEST — Scenario {key}: {scenario['name']}")
        print("=" * 80)

        state = GeneratorState(
            goal=scenario["goal"],
            theory=scenario["theory"],
            critic_feedback=scenario["critic_feedback"],
            previous_generation=scenario["previous_generation"]
        )

        result = generateQuestionItemFromGoal(state)

        questions = result.get("generated_questions", [])
        if questions:
            q = questions[0]
            print("\n--- GENERATED QUESTION ITEM ---")
            output_dict = q.model_dump()
            print(json.dumps(output_dict, indent=2))
            print("=" * 80)
            print(f"✓ SUCCESS: Scenario {key} QuestionItem generated successfully.")
        else:
            print(f"❌ FAIL: Scenario {key} failed to generate a question item.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Generator Node Output Quality")
    parser.add_argument(
        "--scenario",
        choices=["1", "2", "3", "4", "5", "all"],
        default="all",
        help="Select scenario (1-5) or 'all' to execute all 5 scenarios sequentially (default: all)"
    )
    args = parser.parse_args()
    run_test(args.scenario)
