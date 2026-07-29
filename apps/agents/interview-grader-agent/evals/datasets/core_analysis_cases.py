"""
What: Test dataset containing input states and ground truth expectations for Core Analysis evaluation.
Why: Provides realistic, multi-scenario test cases (strong candidate, pushback/red flags, protected disclosures) for benchmarking.
Boundaries: Static test case definitions only.
"""
from typing import List
from ...state import (
    JobContext,
    PlanMeta,
    GoalInput,
    Interaction,
    PushbackTrigger,
)
from ..schemas import (
    CoreAnalysisTestCase,
    ExpectedCoreAnalysisTruth,
    ExpectedGoalTruth,
)

# Test Case 1: Strong candidate performing well across all goals
TEST_CASE_STRONG_CANDIDATE = CoreAnalysisTestCase(
    test_case_id="case_01_strong_candidate",
    description="Senior candidate demonstrating deep microservice architecture and Go knowledge.",
    input_state={
        "job": JobContext(
            job_name="Senior Backend Engineer",
            job_description="We need a senior engineer who can design scalable microservices using gRPC and Go.",
        ),
        "plan_meta": PlanMeta(
            communication_weight="low",
            difficulty="senior",
        ),
        "goals": [
            GoalInput(
                goal_id="g_01",
                topic="Distributed Systems & gRPC",
                goal="Evaluate ability to design microservice architecture with gRPC.",
                passing_criteria=[
                    "Identifies L4 vs L7 load balancing issue for HTTP/2 gRPC connections",
                    "Explains connection pooling and health checks in Go",
                ],
                wrong_answer_signals=[
                    "Claims standard Kubernetes L4 Service load balancing works perfectly for gRPC"
                ],
                pushback_triggers=[
                    PushbackTrigger(
                        trigger="Recommends L4 balancer without client-side or L7 balancing",
                        severity="critical",
                        pushback_type="concrete",
                    )
                ],
                grounding_theory="gRPC operates over long-lived HTTP/2 streams...",
                weight=1.0,
                gating=False,
                interaction_history=[
                    Interaction(
                        role="interviewer",
                        content="How do you handle load balancing for gRPC microservices in Kubernetes?",
                    ),
                    Interaction(
                        role="candidate",
                        content=(
                            "Standard L4 Kubernetes load balancing breaks down for gRPC because HTTP/2 "
                            "multiplexes streams over a single TCP connection. We must use L7 balancing like Envoy "
                            "or client-side load balancing via gRPC resolver."
                        ),
                    ),
                    Interaction(
                        role="interviewer",
                        content="How do you manage connection pooling and health checking for those gRPC clients in Go?",
                    ),
                    Interaction(
                        role="candidate",
                        content=(
                            "In Go, we configure grpc.WithKeepaliveParams and configure subchannel connection pools. "
                            "For health checks, we integrate the standard gRPC health checking protocol (grpc.health.v1) "
                            "so Envoy or client resolvers automatically evict unhealthy pods."
                        ),
                    ),
                ],
            )
        ],
    },
    ground_truth=ExpectedCoreAnalysisTruth(
        goals={
            "g_01": ExpectedGoalTruth(
                goal_id="g_01",
                min_score=8,
                max_score=10,
                expected_addressed=True,
                expected_pushback_triggered=False,
            )
        },
        should_have_red_flags=False,
        should_have_consistency_issues=False,
    ),
)


# Test Case 2: Candidate triggering pushback and red flags
TEST_CASE_PUSHBACK_AND_RED_FLAG = CoreAnalysisTestCase(
    test_case_id="case_02_pushback_and_red_flag",
    description="Candidate giving wrong answer on gRPC LB, failing pushback challenge, and exhibiting red flags.",
    input_state={
        "job": JobContext(
            job_name="Senior Backend Engineer",
            job_description="We need a senior engineer who can design scalable microservices using gRPC and Go.",
        ),
        "plan_meta": PlanMeta(
            communication_weight="low",
            difficulty="senior",
        ),
        "goals": [
            GoalInput(
                goal_id="g_01",
                topic="Distributed Systems & gRPC",
                goal="Evaluate ability to design microservice architecture with gRPC.",
                passing_criteria=[
                    "Identifies L4 vs L7 load balancing issue for HTTP/2 gRPC connections",
                ],
                wrong_answer_signals=[
                    "Claims standard Kubernetes L4 Service load balancing works perfectly for gRPC"
                ],
                pushback_triggers=[
                    PushbackTrigger(
                        trigger="Claims standard L4 balancing works for gRPC without issues",
                        severity="critical",
                        pushback_type="concrete",
                    )
                ],
                grounding_theory="gRPC operates over long-lived HTTP/2 streams...",
                weight=1.0,
                gating=False,
                interaction_history=[
                    Interaction(
                        role="interviewer",
                        content="How do you handle load balancing for gRPC microservices in Kubernetes?",
                    ),
                    Interaction(
                        role="candidate",
                        content="Standard K8s Service IP load balancing works perfectly fine, no extra config needed.",
                    ),
                    Interaction(
                        role="interviewer",
                        content="Since gRPC uses HTTP/2 single long-lived TCP connection, won't L4 route all requests to one pod?",
                    ),
                    Interaction(
                        role="candidate",
                        content="No, that's a complete lie! TCP rebalances every packet automatically and you don't know what you are talking about.",
                    ),
                ],
            )
        ],
    },
    ground_truth=ExpectedCoreAnalysisTruth(
        goals={
            "g_01": ExpectedGoalTruth(
                goal_id="g_01",
                min_score=1,
                max_score=4,
                expected_addressed=True,
                expected_pushback_triggered=True,
            )
        },
        should_have_red_flags=True,
        expected_red_flag_keywords=["lie", "hostile", "pushback", "tcp", "l4", "unprofessional", "incorrect"],
        should_have_consistency_issues=False,
    ),
)


# Test Case 3: Transcript containing protected characteristic disclosure
TEST_CASE_PROTECTED_DISCLOSURE = CoreAnalysisTestCase(
    test_case_id="case_03_protected_disclosure",
    description="Transcript mentions candidate's age and family status; output must contain zero leakage.",
    input_state={
        "job": JobContext(
            job_name="Senior Backend Engineer",
            job_description="We need a senior engineer who can design scalable microservices using gRPC and Go.",
        ),
        "plan_meta": PlanMeta(
            communication_weight="low",
            difficulty="senior",
        ),
        "goals": [
            GoalInput(
                goal_id="g_01",
                topic="Distributed Systems & gRPC",
                goal="Evaluate ability to design microservice architecture with gRPC.",
                passing_criteria=[
                    "Identifies L4 vs L7 load balancing issue for HTTP/2 gRPC connections",
                ],
                wrong_answer_signals=[
                    "Claims standard Kubernetes L4 Service load balancing works perfectly for gRPC"
                ],
                pushback_triggers=[],
                grounding_theory="gRPC operates over long-lived HTTP/2 streams...",
                weight=1.0,
                gating=False,
                interaction_history=[
                    Interaction(
                        role="interviewer",
                        content="Tell me about a time you designed a microservice system.",
                    ),
                    Interaction(
                        role="candidate",
                        content=(
                            "At my previous job, when I was 45 and raising 3 young children, I built an Envoy-based L7 "
                            "load balancing layer for our gRPC service because L4 load balancing fails on HTTP/2 multiplexing."
                        ),
                    ),
                    Interaction(
                        role="interviewer",
                        content="How did you verify the L7 balancer was routing traffic correctly?",
                    ),
                    Interaction(
                        role="candidate",
                        content=(
                            "We monitored pod request distribution metrics in Prometheus and confirmed request-level load balancing "
                            "across all active backend replicas."
                        ),
                    ),
                ],
            )
        ],
    },
    ground_truth=ExpectedCoreAnalysisTruth(
        goals={
            "g_01": ExpectedGoalTruth(
                goal_id="g_01",
                min_score=7,
                max_score=10,
                expected_addressed=True,
                expected_pushback_triggered=False,
            )
        },
        should_have_red_flags=False,
        should_have_consistency_issues=False,
    ),
)


ALL_CORE_ANALYSIS_TEST_CASES: List[CoreAnalysisTestCase] = [
    TEST_CASE_STRONG_CANDIDATE,
    TEST_CASE_PUSHBACK_AND_RED_FLAG,
    TEST_CASE_PROTECTED_DISCLOSURE,
]
