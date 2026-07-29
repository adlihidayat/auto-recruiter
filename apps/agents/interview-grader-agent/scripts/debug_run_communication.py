"""
What: Debug runner for testing Call 2 (Communication & Interpersonal) node execution on a sample test case.
Why: Demonstrates Call 2 execution when plan_meta.communication_weight == 'high'.
Boundaries: Local debugging script only; does not run production server.
"""
import os
import sys
import json
import importlib
from dotenv import load_dotenv

# Setup path mapping for monorepo imports
agent_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
agents_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))

for path in [agent_root, agents_parent, workspace_root]:
    if path not in sys.path:
        sys.path.insert(0, path)

load_dotenv(os.path.join(agents_parent, ".env"))

if "GEMINI_API_KEY1" in os.environ and "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["GEMINI_API_KEY1"]

# Dynamic imports
state_mod = importlib.import_module("interview-grader-agent.state")
JobContext = state_mod.JobContext
PlanMeta = state_mod.PlanMeta
GoalInput = state_mod.GoalInput
Interaction = state_mod.Interaction

comm_node_mod = importlib.import_module("interview-grader-agent.nodes.communication")
run_communication = comm_node_mod.run_communication


def run_communication_test_case():
    print("=======================================================================")
    print("  TESTING CALL 2 (COMMUNICATION & INTERPERSONAL) NODE EXECUTION        ")
    print("=======================================================================")

    input_state = {
        "job": JobContext(
            job_name="Engineering Manager / Lead Architect",
            job_description="Lead technical direction, mentor team members, and present architecture proposals to executives."
        ),
        "plan_meta": PlanMeta(
            communication_weight="high",  # Triggers Call 2
            difficulty="senior"
        ),
        "goals": [
            GoalInput(
                goal_id="g_01",
                topic="Architecture Proposal & Stakeholder Pushback",
                goal="Evaluate ability to defend technical proposals to non-technical executive leadership.",
                passing_criteria=["Structure proposal clearly with trade-offs"],
                wrong_answer_signals=[],
                pushback_triggers=[],
                grounding_theory="",
                weight=1.0,
                gating=False,
                interaction_history=[
                    Interaction(
                        role="interviewer",
                        content="We are considering migrating from monolith to microservices. How would you pitch this budget to executives?"
                    ),
                    Interaction(
                        role="candidate",
                        content="That's a great question. Let me structure this into three core points: business value, migration risk, and expected ROI. First, on business value..."
                    ),
                    Interaction(
                        role="interviewer",
                        content="The CFO says microservices sound like an expensive engineering vanity project that will double cloud costs. How do you respond?"
                    ),
                    Interaction(
                        role="candidate",
                        content="I completely understand the CFO's concern — cloud infrastructure cost inflation is a very real risk if unmanaged. However, our current monolith downtime costs us $50k per outage in SLA penalties. By decomposing into independent domain services..."
                    )
                ]
            )
        ]
    }

    print("\nInvoking Call 2 run_communication node...")
    result = run_communication(input_state)
    comm_output = result.get("communication")

    print("\n=======================================================================")
    print("  COMMUNICATION ANALYSIS RESULT OUTPUT                                ")
    print("=======================================================================")
    print(f"Addressed:   {comm_output.addressed}")
    print(f"Score:       {comm_output.score} / 10")
    print(f"Confidence:  {comm_output.confidence}")
    print("\nDiscourse Signal Breakdown:")
    print(f"  • Flow Control:        {comm_output.signals.flow_control}")
    print(f"  • Active Listening:    {comm_output.signals.active_listening}")
    print(f"  • Structure & Clarity: {comm_output.signals.structure}")
    print(f"  • Assertiveness:       {comm_output.signals.assertiveness}")
    print(f"  • Objection Handling:  {comm_output.signals.objection_handling}")
    print("\nOverall Rationale:")
    print(f"  {comm_output.rationale}")
    print("=======================================================================")


if __name__ == "__main__":
    run_communication_test_case()
