"""
What: Terminal runner for testing Call 3 (Borderline Evidence Citation Node) in isolation.
Why: Validates that run_citations processes all goals needing citations in 1 single LLM call and returns structured quotes.
Boundaries: CLI runner for dev/testing only; does not run in production FastAPI endpoints.
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
CoreAnalysisOutput = state_mod.CoreAnalysisOutput
GoalEval = state_mod.GoalEval
Evidence = state_mod.Evidence
CriteriaMatch = state_mod.CriteriaMatch
ProblemSolvingEval = state_mod.ProblemSolvingEval
CitationsOutput = state_mod.CitationsOutput

citations_node_mod = importlib.import_module("interview-grader-agent.nodes.citations")
run_citations = citations_node_mod.run_citations


def run_citations_test():
    print("=======================================================================")
    print("      TESTING CALL 3 (BORDERLINE EVIDENCE CITATION NODE) IN ISOLATION   ")
    print("=======================================================================")

    job = JobContext(
        job_name="Senior Distributed Systems Engineer",
        job_description="Design and optimize high-throughput microservices using Go and gRPC."
    )

    plan_meta = PlanMeta(communication_weight="low", difficulty="senior")

    # 3 Goals in candidate interaction history
    goals = [
        # g_01: Strong performance (Score 8, High confidence) -> Should NOT get citations
        GoalInput(
            goal_id="g_01",
            topic="gRPC Load Balancing",
            goal="Evaluate gRPC L4 vs L7 balancing knowledge",
            passing_criteria=["Identifies HTTP/2 connection pinning issue with L4"],
            wrong_answer_signals=[],
            pushback_triggers=[],
            grounding_theory="gRPC multiplexes streams over long-lived HTTP/2 TCP connections...",
            weight=1.0,
            gating=False,
            interaction_history=[
                Interaction(role="interviewer", content="Why does L4 load balancing fail for gRPC in Kubernetes?"),
                Interaction(role="candidate", content="Because gRPC uses HTTP/2 single long-lived TCP connections, so L4 just pins all streams to the first pod."),
            ]
        ),
        # g_02: Borderline performance (Score 5, Medium confidence) -> SHOULD get citations
        GoalInput(
            goal_id="g_02",
            topic="Schema Migration Strategy",
            goal="Evaluate zero-downtime database schema migration strategy",
            passing_criteria=["Uses expand-contract pattern for non-null column additions"],
            wrong_answer_signals=["Adds NOT NULL column directly without default on large table"],
            pushback_triggers=[],
            grounding_theory="Large table alterations require adding nullable column first, backfilling, then adding constraint...",
            weight=1.0,
            gating=False,
            interaction_history=[
                Interaction(role="interviewer", content="How do you safely add a NOT NULL column to a 100M row Postgres table?"),
                Interaction(role="candidate", content="I'd probably just run ALTER TABLE ADD COLUMN NOT NULL DEFAULT 'active' during off-peak hours."),
                Interaction(role="interviewer", content="That locks the table for a full rewrite. Is there a zero-downtime way?"),
                Interaction(role="candidate", content="Oh, right. I guess I'd add it as nullable first, backfill rows in batches, and then set NOT NULL later."),
            ]
        ),
        # g_03: Low confidence performance (Score 7, Low confidence) -> SHOULD get citations
        GoalInput(
            goal_id="g_03",
            topic="Idempotency in Payment Processing",
            goal="Evaluate idempotency key mechanics in distributed payment retries",
            passing_criteria=["Uses atomic DB transaction with request hash"],
            wrong_answer_signals=[],
            pushback_triggers=[],
            grounding_theory="Idempotency keys prevent double charge on retries...",
            weight=1.0,
            gating=False,
            interaction_history=[
                Interaction(role="interviewer", content="How do you handle retries in payments without double charging?"),
                Interaction(role="candidate", content="We use idempotency keys. I think we store them in Redis or Postgres for a few hours."),
                Interaction(role="interviewer", content="What happens if the Redis write succeeds but the charge fails?"),
                Interaction(role="candidate", content="Yeah, that would be tricky. I'm not totally sure how our payment gateway handles that edge case."),
            ]
        ),
    ]

    # Call 1 Core Analysis Output simulation
    core_analysis = CoreAnalysisOutput(
        goals=[
            GoalEval(
                goal_id="g_01",
                addressed=True,
                score=8,
                confidence="high",
                evidence=Evidence(claims=["L4 pins connections"], demonstrated_reasoning=["Understands HTTP/2 connection multiplexing"], specificity="high"),
                criteria_match=CriteriaMatch(passing_met=["Identifies HTTP/2 connection pinning issue"], failed_triggered=[]),
                rationale="Clear and accurate explanation of gRPC L4 balancing limitations."
            ),
            GoalEval(
                goal_id="g_02",
                addressed=True,
                score=5,
                confidence="medium",
                evidence=Evidence(claims=["ALTER TABLE directly", "expand-contract after prompt"], demonstrated_reasoning=["Initial answer locked table, corrected after interviewer hint"], specificity="medium"),
                criteria_match=CriteriaMatch(passing_met=["Mentions expand-contract after hint"], failed_triggered=["Direct ALTER TABLE initially"]),
                rationale="Borderline response: initially proposed table-locking migration, but recovered expand-contract pattern after interviewer pushback."
            ),
            GoalEval(
                goal_id="g_03",
                addressed=True,
                score=7,
                confidence="low",
                evidence=Evidence(claims=["Uses idempotency keys"], demonstrated_reasoning=["Understands basic key concept, uncertain on failure modes"], specificity="low"),
                criteria_match=CriteriaMatch(passing_met=["Mentions idempotency keys"], failed_triggered=[]),
                rationale="Low confidence assessment: candidate understands high-level idempotency key concept but admitted uncertainty on distributed transaction edge cases."
            ),
        ],
        problem_solving_under_ambiguity=ProblemSolvingEval(addressed=True, score=7, confidence="high", rationale="Good problem solving."),
        consistency_issues=[],
        red_flags=[]
    )

    state = {
        "job": job,
        "plan_meta": plan_meta,
        "goals": goals,
        "core_analysis": core_analysis,
    }

    print("\nState prepared with 3 goals:")
    print("  - g_01: Score 8, Confidence high  -> Excluded from Call 3")
    print("  - g_02: Score 5, Confidence medium -> Target for Call 3 (Score in 4-6)")
    print("  - g_03: Score 7, Confidence low    -> Target for Call 3 (Low confidence)")

    print("\nInvoking run_citations(state) in 1 single LLM pass...")
    res = run_citations(state)

    citations_obj: CitationsOutput = res["citations"]
    print("\n=======================================================================")
    print("                     CALL 3 CITATIONS OUTPUT RESULT                    ")
    print("=======================================================================")
    print(f"Goal Citations Count: {len(citations_obj.goal_citations)}")
    for gc in citations_obj.goal_citations:
        print(f"\n[Goal ID: {gc.goal_id}] ({len(gc.citations)} quote(s)):")
        for c in gc.citations:
            print(f"  - Turn Ref: {c.turn_reference}")
            print(f"    Quote   : \"{c.quote}\"")

    print("\nMapping format via to_citations_by_goal():")
    print(json.dumps(citations_obj.to_citations_by_goal(), indent=2))
    print("\nCall 3 Citation Node test completed successfully!")


if __name__ == "__main__":
    run_citations_test()
