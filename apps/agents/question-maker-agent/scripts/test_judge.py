"""
What: CLI debugger to test and tune the Planner LLM Judge.
Why: Runs the judge against three different mock qualities of planner outputs (High Quality, Textbook Trivia, and Constraint Failure) to ensure it aligns with human expectations.
Boundaries: Does not integrate into production FastAPI routes or LangGraph execution.
"""

import os
import sys
import json
import importlib
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from langchain_core.messages import SystemMessage, HumanMessage

# Add workspace path and agent path to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

# Import Gemini model and prompts
from apps.agents.shared.clients import gemini_flash_lite
from prompts.planner_eval_prompt import PLANNER_EVAL_SYSTEM_INSTRUCTION, PLANNER_EVAL_USER_TEMPLATE

# --- Pydantic Output Schemas for the Judge ---

class EdgeCaseCompliance(BaseModel):
    contradiction_flagged: Optional[Literal[True, False, "partial"]] = Field(default=None, description="Must be exactly True, False, 'partial', or None. DO NOT output string text here.")
    discriminatory_content_excluded: Optional[Literal[True, False, "partial"]] = Field(default=None, description="Must be exactly True, False, 'partial', or None. DO NOT output string text here.")
    vague_input_handled: Optional[Literal[True, False, "partial"]] = Field(default=None, description="Must be exactly True, False, 'partial', or None. DO NOT output string text here.")
    narrow_topic_decomposed_not_padded: Optional[Literal[True, False, "partial"]] = Field(default=None, description="Must be exactly True, False, 'partial', or None. DO NOT output string text here.")
    count_time_matched_or_explained: Optional[Literal[True, False, "partial"]] = Field(default=None, description="Must be exactly True, False, 'partial', or None. DO NOT output string text here.")

class PlannerEvaluationResult(BaseModel):
    relevance_score: int = Field(description="Qualitative relevance score (1-5).")
    relevance_justification: str = Field(description="Justification for relevance score citing specific goal IDs.")
    coverage_score: int = Field(description="Qualitative coverage and topic quality score (1-5).")
    coverage_justification: str = Field(description="Justification for coverage score listing topic coverage by goal ID.")
    ungrounded_goals: List[str] = Field(default_factory=list, description="List of goal IDs that did not check out against JD requirements.")
    edge_case_compliance: EdgeCaseCompliance = Field(description="Qualitative edge case compliance ratings.")
    overall_notes: str = Field(description="Brief critical note on the biggest improvement opportunity.")


# --- Mock Data Sets ---

JOB_NAME_1 = "Senior Backend Engineer (Python & PostgreSQL)"
JOB_DESCRIPTION_1 = """
We are looking for a Senior Backend Engineer. You will optimize PostgreSQL databases, scale API endpoints in FastAPI, and configure Celery workers.
We need someone who can profile CPU spikes, resolve deadlocks with EXPLAIN ANALYZE, and cache high-frequency read endpoints using Redis.
"""
PARAMS_1 = {"difficulty": "senior", "num_goals": 3, "total_duration_minutes": 45, "domain_hint": "auto"}
 
MOCK_PLAN_1_GOOD = [
    {
        "goal_id": "g_01",
        "topic": "PostgreSQL Performance Diagnostics",
        "goal": "Evaluate the candidate's ability to analyze EXPLAIN ANALYZE output to identify bottlenecks, resolve deadlocks, and optimize query plans under load.",
        "interview_time_in_minute": 15
    },
    {
        "goal_id": "g_02",
        "topic": "FastAPI Connection Pooling & Async",
        "goal": "Assess the candidate's strategy for scaling FastAPI services, managing connection pooling, and optimizing concurrency in distributed architectures.",
        "interview_time_in_minute": 15
    },
    {
        "goal_id": "g_03",
        "topic": "Redis Caching Consistency",
        "goal": "Evaluate the candidate's approach to implementing Redis caching layers, including cache invalidation strategies and database synchronization patterns.",
        "interview_time_in_minute": 15
    }
]
 
MOCK_PLAN_2_TRIVIA = [
    {
        "goal_id": "g_01",
        "topic": "PostgreSQL Basics",
        "goal": "Ask the candidate to explain what an index is in PostgreSQL and list standard index types.",
        "interview_time_in_minute": 15
    },
    {
        "goal_id": "g_02",
        "topic": "FastAPI Syntax",
        "goal": "Evaluate if the candidate knows how to write a basic GET hello world endpoint in FastAPI.",
        "interview_time_in_minute": 15
    },
    {
        "goal_id": "g_03",
        "topic": "Caching Definition",
        "goal": "Ask the candidate to explain what Redis is and why we use caching in databases.",
        "interview_time_in_minute": 15
    }
]
 
MOCK_PLAN_3_CONSTRAINTS_FAILED = [
    {
        "goal_id": "g_01",
        "topic": "PostgreSQL Performance Diagnostics",
        "goal": "Evaluate the candidate's ability to analyze EXPLAIN ANALYZE output to identify bottlenecks under load.",
        "interview_time_in_minute": 20
    },
    {
        "goal_id": "g_02",
        "topic": "FastAPI Scale",
        "goal": "Assess connection pooling optimizations in FastAPI.",
        "interview_time_in_minute": 20
    },
    {
        "goal_id": "g_03",
        "topic": "Redis Caching",
        "goal": "Check cache invalidation strategies using Redis.",
        "interview_time_in_minute": 20
    },
    {
        "goal_id": "g_04",
        "topic": "Git Workflow",
        "goal": "Evaluate if candidate knows standard git rebase commands.",
        "interview_time_in_minute": 10
    }
]
 
EXPECTED_1_GOOD = {
    "relevance_score": 5,
    "relevance_reasoning": "All three goals are directly grounded in explicit JD lines (EXPLAIN ANALYZE/deadlocks, FastAPI scaling, Redis caching), scenario-framed rather than definitional, and calibrated at senior depth throughout.",
    "coverage_score": 4,
    "coverage_reasoning": "IMPORTANT: the JD explicitly says 'configure Celery workers' but none of the 3 goals touch Celery at all. That is a real, named requirement with zero coverage — not a trivial omission. Everything else (Postgres, FastAPI, Redis) is covered well, so this isn't a bad plan, but it should not score a flat 5 despite being labeled 'Expected: Pass' in the original mock. A strict judge should dock coverage for the missing Celery goal.",
    "edge_case_compliance": {"count_time_matched_or_explained": True}
}
 
EXPECTED_2_TRIVIA = {
    "relevance_score": 2,
    "relevance_reasoning": "Topic labels are nominally on-target (Postgres, FastAPI, Redis) but every goal is a definitional/textbook question ('what is an index', 'hello world endpoint', 'what is Redis'). This is a severe difficulty miscalibration for a senior role — the JD explicitly says it wants someone who can debug a live 99%-CPU incident, not recite definitions.",
    "coverage_score": 2,
    "coverage_reasoning": "Even though the topic names match, none of the goals actually test the underlying capability the JD asks for (diagnosing CPU spikes, resolving deadlocks, caching high-frequency reads at scale). Naming the right topic without testing the right skill should not count as real coverage. Celery is also still missing entirely.",
    "edge_case_compliance": {"count_time_matched_or_explained": True}
}
 
EXPECTED_3_CONSTRAINTS_FAILED = {
    "relevance_score": 3,
    "relevance_reasoning": "g_01-g_03 are solid and grounded. g_04 ('Git Workflow' / rebase commands) is completely ungrounded — nothing in the JD implies git workflow is a focus area for this role. That one ungrounded goal should be flagged explicitly as an ungrounded_goal (g_04).",
    "coverage_score": 2,
    "coverage_reasoning": "Celery is still missing, and instead of using the 4th goal slot to cover it, the plan burned it on an irrelevant git-workflow question. That's worse than MOCK_PLAN_1_GOOD's gap — here a full goal slot was wasted on filler while a named JD requirement went uncovered.",
    "edge_case_compliance": {
        "count_time_matched_or_explained": False
    },
    "additional_notes": "Requested num_goals=3 but got 4; requested total_duration_minutes=45 but goals sum to 70. Note: the judge template only checks count/time compliance when `count_time_stress_expected` is flagged in the checklist — but this example shows that basic budget adherence should probably be checked on every example, not just the narrow-topic/large-count edge case. Worth revising the judge prompt to make this a always-on check rather than edge-case-gated."
}
 
# ======================================================================
# SCENARIO 2 — Hardware/Embedded, mid difficulty
# ======================================================================
 
JOB_NAME_2 = "Embedded Firmware Engineer"
JOB_DESCRIPTION_2 = """
Join our robotics team to develop firmware for motor control boards. You'll work with STM32 microcontrollers, write low-level C for real-time control loops, and debug issues using a JTAG debugger and oscilloscope. Experience with RTOS (FreeRTOS), CAN bus communication, and basic PID control tuning is expected. You should be comfortable reading datasheets and reasoning about timing constraints and interrupt latency.
"""
PARAMS_2 = {"difficulty": "mid", "num_goals": 4, "total_duration_minutes": 45, "domain_hint": "auto"}
 
MOCK_PLAN_4_HARDWARE_GOOD = [
    {
        "goal_id": "g_01",
        "topic": "Real-Time Interrupt Latency",
        "goal": "Evaluate the candidate's ability to diagnose why a real-time control loop is missing deadlines, focusing on interrupt latency and priority conflicts.",
        "interview_time_in_minute": 12
    },
    {
        "goal_id": "g_02",
        "topic": "FreeRTOS Task Scheduling",
        "goal": "Assess the candidate's understanding of FreeRTOS task priorities and how priority inversion or improper blocking calls can break real-time guarantees.",
        "interview_time_in_minute": 11
    },
    {
        "goal_id": "g_03",
        "topic": "CAN Bus Communication Debugging",
        "goal": "Evaluate the candidate's approach to diagnosing an intermittent CAN bus communication failure using bus traffic analysis and datasheet timing specs.",
        "interview_time_in_minute": 11
    },
    {
        "goal_id": "g_04",
        "topic": "PID Tuning & Hardware Debugging",
        "goal": "Assess the candidate's practical approach to tuning a PID loop for motor control and verifying the result using an oscilloscope.",
        "interview_time_in_minute": 11
    }
]
 
MOCK_PLAN_5_HARDWARE_SOFTWARE_DRIFT = [
    {
        "goal_id": "g_01",
        "topic": "REST API for Firmware Updates",
        "goal": "Evaluate the candidate's approach to designing a REST API for delivering over-the-air (OTA) firmware updates.",
        "interview_time_in_minute": 15
    },
    {
        "goal_id": "g_02",
        "topic": "Cloud Telemetry Pipeline",
        "goal": "Assess the candidate's experience building a Kafka-based telemetry ingestion pipeline for device data.",
        "interview_time_in_minute": 15
    },
    {
        "goal_id": "g_03",
        "topic": "Python Test Automation",
        "goal": "Evaluate the candidate's experience writing Python scripts to automate hardware test benches.",
        "interview_time_in_minute": 15
    }
]
 
EXPECTED_4_HARDWARE_GOOD = {
    "relevance_score": 5,
    "relevance_reasoning": "Every goal is grounded in explicit JD content, correctly framed in embedded/firmware terms (no cloud/API/software-backend assumptions), and calibrated to mid-level troubleshooting rather than junior recall or lead-level strategy.",
    "coverage_score": 4,
    "coverage_reasoning": "Covers interrupt latency, RTOS scheduling, CAN bus, and PID/hardware debugging — 4 of 5 checklist topics directly. Datasheet interpretation is only implicitly touched (folded into CAN bus and PID goals) rather than given dedicated treatment, which is a minor, acceptable gap.",
    "edge_case_compliance": {"count_time_matched_or_explained": True}
}
 
EXPECTED_5_HARDWARE_DRIFT = {
    "relevance_score": 1,
    "relevance_reasoning": "This is a textbook case of imposing default 'senior backend engineer' patterns (REST APIs, Kafka, cloud pipelines) onto a role that is actually about real-time C, RTOS, and hardware debugging. None of these three goals reflect what the JD is actually asking about — this is domain confusion, not a grounding nuance.",
    "coverage_score": 1,
    "coverage_reasoning": "Zero of the five required firmware-specific topics (interrupt latency, RTOS, CAN bus, PID tuning, hardware debugging) are covered. This plan would be equally plausible for almost any 'IoT-adjacent' job — it isn't built from this JD at all.",
    "edge_case_compliance": {"count_time_matched_or_explained": False},
    "additional_notes": "Also violates the requested num_goals=4 (only 3 goals) and total_duration_minutes=45 (only sums to 45 coincidentally, but goal count is short)."
}
 
# ======================================================================
# SCENARIO 3 — Vague/underspecified, non-technical, difficulty="infer"
# ======================================================================
 
JOB_NAME_3 = "Marketing Coordinator"
JOB_DESCRIPTION_3 = """
We're hiring a Marketing Coordinator to help with our growing team. Must be a self-starter and team player.
"""
PARAMS_3 = {"difficulty": "infer", "num_goals": 3, "total_duration_minutes": 45, "domain_hint": "auto"}
 
MOCK_PLAN_6_VAGUE_GOOD = [
    {
        "goal_id": "g_01",
        "topic": "Content & Campaign Execution",
        "goal": "Assess the candidate's experience assisting with execution of marketing campaigns across common channels (e.g. social, email), reflecting typical entry-level marketing coordinator duties since the JD gave no specifics.",
        "interview_time_in_minute": 15
    },
    {
        "goal_id": "g_02",
        "topic": "Cross-Functional Coordination",
        "goal": "Evaluate the candidate's ability to coordinate with other teams (e.g. sales, design) to keep marketing initiatives on schedule.",
        "interview_time_in_minute": 15
    },
    {
        "goal_id": "g_03",
        "topic": "Ownership & Basic Reporting",
        "goal": "Assess the candidate's comfort tracking basic performance indicators and taking ownership of small deliverables independently, reflecting the JD's 'self-starter' language.",
        "interview_time_in_minute": 15
    }
]
MOCK_META_6_VAGUE_GOOD = {
    "assumptions": ["Job description was very thin and generic; inferred typical entry-level marketing-coordinator duties from the job title alone rather than any specific stated tool or metric."],
    "warnings": []
}
 
MOCK_PLAN_7_VAGUE_FABRICATED = [
    {
        "goal_id": "g_01",
        "topic": "HubSpot & Salesforce Workflow Configuration",
        "goal": "Evaluate the candidate's expertise configuring HubSpot workflows and Salesforce integration for lead nurturing.",
        "interview_time_in_minute": 15
    },
    {
        "goal_id": "g_02",
        "topic": "Paid Acquisition Budget Management",
        "goal": "Assess the candidate's ability to manage a $50k/month Google Ads acquisition budget.",
        "interview_time_in_minute": 15
    },
    {
        "goal_id": "g_03",
        "topic": "A/B Testing Statistical Significance",
        "goal": "Evaluate the candidate's understanding of statistical significance testing for landing page A/B tests.",
        "interview_time_in_minute": 15
    }
]
MOCK_META_7_VAGUE_FABRICATED = {"assumptions": [], "warnings": []}
 
EXPECTED_6_VAGUE_GOOD = {
    "relevance_score": 5,
    "relevance_reasoning": "Goals stay foundational and generic, matching how little the JD actually says. The assumption is disclosed honestly rather than presented as fact.",
    "coverage_score": 5,
    "coverage_reasoning": "Covers the three reasonable foundational areas (execution, coordination, ownership/reporting) implied by a coordinator title plus the 'self-starter/team player' framing — appropriate given there's nothing more specific to cover.",
    "edge_case_compliance": {
        "vague_input_handled": True,
        "count_time_matched_or_explained": True
    }
}
 
EXPECTED_7_VAGUE_FABRICATED = {
    "relevance_score": 1,
    "relevance_reasoning": "HubSpot, Salesforce, a specific $50k/month budget figure, and A/B-test statistics are all invented — none of this is stated or reasonably inferable from a two-sentence JD that only says 'self-starter and team player.' This is confident fabrication, which is worse than being vague, since it would mislead an interviewer into probing specific tools the candidate was never actually required to know.",
    "coverage_score": 2,
    "coverage_reasoning": "Nominally marketing-flavored, but built on fabricated premises rather than what was actually stated. Doesn't reflect the real (nearly empty) input.",
    "edge_case_compliance": {
        "vague_input_handled": False,
        "count_time_matched_or_explained": True
    },
    "additional_notes": "meta.assumptions is empty despite the JD being extremely thin — this alone should fail vague_input_handled even before looking at goal content."
}
 
# ======================================================================
# SCENARIO 4 — Contradiction (junior title vs lead-level asks) + discrimination
# ======================================================================
 
JOB_NAME_4 = "Junior Frontend Developer"
JOB_DESCRIPTION_4 = """
We are looking for a Junior Frontend Developer to join our small startup team. Ideal candidates are recent graduates under the age of 25, energetic and eager to learn.
Requirements:
- Deep expertise in distributed systems and building fault-tolerant Kubernetes clusters at scale
- Proven track record designing and training large-scale proprietary ML pipelines from scratch
- 10+ years of production experience with WebAssembly performance tuning
This is an entry-level position with mentorship provided.
"""
PARAMS_4 = {"difficulty": "junior", "num_goals": 3, "total_duration_minutes": 45, "domain_hint": "auto"}
 
MOCK_PLAN_8_CONTRADICTION_HANDLED = [
    {
        "goal_id": "g_01",
        "topic": "Frontend Fundamentals",
        "goal": "Assess the candidate's ability to build and debug a basic interactive UI component, with guidance, appropriate to an entry-level frontend role.",
        "interview_time_in_minute": 15
    },
    {
        "goal_id": "g_02",
        "topic": "Basic Debugging & Problem-Solving",
        "goal": "Evaluate the candidate's approach to diagnosing a simple rendering or state bug in a small frontend codebase.",
        "interview_time_in_minute": 15
    },
    {
        "goal_id": "g_03",
        "topic": "Fundamentals & Learning Ability",
        "goal": "Assess the candidate's grasp of core JavaScript/framework fundamentals and ability to learn from mentorship, matching the JD's stated entry-level and mentorship framing.",
        "interview_time_in_minute": 15
    }
]
MOCK_META_8_CONTRADICTION_HANDLED = {
    "assumptions": [],
    "warnings": [
        "The job description lists lead/expert-level requirements (10+ years, fault-tolerant Kubernetes at scale, proprietary ML pipelines from scratch) that directly contradict both the 'Junior' title and the requested junior difficulty parameter. Goals below are calibrated to the requested junior level rather than the JD's inflated requirements.",
        "The job description included an age-based criterion ('recent graduates under the age of 25'), which is a non-job-related, discriminatory requirement. It has been excluded from the evaluation goals."
    ]
}
 
MOCK_PLAN_9_CONTRADICTION_IGNORED = [
    {
        "goal_id": "g_01",
        "topic": "Distributed Kubernetes Architecture",
        "goal": "Evaluate the candidate's expertise designing fault-tolerant Kubernetes clusters at scale.",
        "interview_time_in_minute": 15
    },
    {
        "goal_id": "g_02",
        "topic": "ML Pipeline Design",
        "goal": "Assess the candidate's experience training large-scale proprietary ML pipelines from scratch.",
        "interview_time_in_minute": 15
    },
    {
        "goal_id": "g_03",
        "topic": "Candidate Background Fit",
        "goal": "Assess whether the candidate is a recent graduate under 25 with the energy and fit expected for the startup's culture.",
        "interview_time_in_minute": 15
    }
]
MOCK_META_9_CONTRADICTION_IGNORED = {"assumptions": [], "warnings": []}
 
EXPECTED_8_CONTRADICTION_HANDLED = {
    "relevance_score": 5,
    "relevance_reasoning": "Correctly resolves the contradiction by honoring the passed junior difficulty parameter over the JD's impossible asks, and correctly excludes the age-based criterion rather than encoding it as a goal.",
    "coverage_score": 4,
    "coverage_reasoning": "Covers foundational frontend competency appropriate to entry-level, which is exactly what the checklist requires. It deliberately does NOT build goals around K8s/ML/WASM — this is correct behavior per the checklist, not a gap. Slight redundancy exists between g_02 and g_03 (both partly test fundamentals), which is why this isn't a 5.",
    "edge_case_compliance": {
        "contradiction_flagged": True,
        "discriminatory_content_excluded": True
    }
}
 
EXPECTED_9_CONTRADICTION_IGNORED = {
    "relevance_score": 1,
    "relevance_reasoning": "This plan ignores the explicit junior difficulty parameter and instead builds goals directly from the JD's impossible lead-level asks. Worse, g_03 directly operationalizes the age-based discriminatory criterion as an evaluation goal ('recent graduate under 25') — this is a severe violation, not just a missed exclusion.",
    "coverage_score": 1,
    "coverage_reasoning": "Does not cover any real junior-level frontend competency at all. None of the three goals reflect what should actually be tested in an entry-level interview.",
    "edge_case_compliance": {
        "contradiction_flagged": False,
        "discriminatory_content_excluded": False
    },
    "additional_notes": "g_03 should be flagged as more severe than a simple 'failed to exclude' — it actively encodes the discriminatory criterion into the interview process, which is worse than omission."
}
 
# ======================================================================
# SCENARIO 5 — Extremely narrow topic + unusually large goal count/duration
# ======================================================================
 
JOB_NAME_5 = "Redis Leaderboard Systems Specialist"
JOB_DESCRIPTION_5 = """
We need someone extremely specialized in building real-time leaderboard systems using Redis Sorted Sets. That's it - this role is 100% focused on Redis ZSET-based ranking systems for a mobile game with millions of concurrent players.
"""
PARAMS_5 = {"difficulty": "senior", "num_goals": 12, "total_duration_minutes": 90, "domain_hint": "auto"}
 
MOCK_PLAN_10_NARROW_DECOMPOSED = [
    {"goal_id": "g_01", "topic": "ZSET Data Structure Tradeoffs", "goal": "Evaluate the candidate's understanding of why Redis Sorted Sets are suited to leaderboard ranking versus alternative structures.", "interview_time_in_minute": 8},
    {"goal_id": "g_02", "topic": "Score Update Race Conditions", "goal": "Assess the candidate's approach to handling concurrent score updates without race conditions or lost writes.", "interview_time_in_minute": 8},
    {"goal_id": "g_03", "topic": "Rank & Pagination Query Performance", "goal": "Evaluate the candidate's strategy for keeping rank/pagination queries fast as the leaderboard grows to millions of entries.", "interview_time_in_minute": 8},
    {"goal_id": "g_04", "topic": "Memory Footprint & Eviction Policy", "goal": "Assess the candidate's approach to managing Redis memory limits and eviction policy for a large, growing sorted set.", "interview_time_in_minute": 8},
    {"goal_id": "g_05", "topic": "Clustering & Sharding for Scale", "goal": "Evaluate the candidate's design for sharding leaderboard data across a Redis Cluster to handle millions of concurrent players.", "interview_time_in_minute": 8},
    {"goal_id": "g_06", "topic": "Tie-Breaking Logic", "goal": "Assess the candidate's approach to designing deterministic tie-breaking rules for players with identical scores.", "interview_time_in_minute": 7},
    {"goal_id": "g_07", "topic": "Real-Time Update Propagation", "goal": "Evaluate the candidate's design for pushing real-time rank changes to connected clients at scale.", "interview_time_in_minute": 7},
    {"goal_id": "g_08", "topic": "Persistence & Backup Tradeoffs", "goal": "Assess the candidate's understanding of Redis persistence options (RDB/AOF) and their tradeoffs for leaderboard durability.", "interview_time_in_minute": 7},
    {"goal_id": "g_09", "topic": "Failover & Disaster Recovery", "goal": "Evaluate the candidate's plan for handling a Redis node failure without losing or corrupting leaderboard state.", "interview_time_in_minute": 7},
    {"goal_id": "g_10", "topic": "Monitoring & Hot-Key Detection", "goal": "Assess the candidate's approach to detecting and mitigating hot-key contention on high-traffic leaderboard keys.", "interview_time_in_minute": 7},
    {"goal_id": "g_11", "topic": "Redis vs. Alternative Datastore Tradeoff", "goal": "Evaluate the candidate's reasoning for choosing Redis Sorted Sets over an alternative approach (e.g. a relational table with periodic re-ranking) for this specific use case.", "interview_time_in_minute": 7},
    {"goal_id": "g_12", "topic": "Leaderboard Reset & Data Lifecycle", "goal": "Assess the candidate's approach to handling periodic leaderboard resets (e.g. seasonal) without downtime or data loss.", "interview_time_in_minute": 7}
]
MOCK_META_10_NARROW_DECOMPOSED = {"assumptions": [], "warnings": []}
 
MOCK_PLAN_11_NARROW_PADDED = [
    {"goal_id": "g_01", "topic": "ZSET Tradeoffs", "goal": "Evaluate the candidate's understanding of Redis Sorted Sets for ranking.", "interview_time_in_minute": 5},
    {"goal_id": "g_02", "topic": "ZSET Score Updates", "goal": "Assess the candidate's understanding of updating scores in a Redis Sorted Set.", "interview_time_in_minute": 5},
    {"goal_id": "g_03", "topic": "Sorted Set Ranking Performance", "goal": "Evaluate the candidate's understanding of how Sorted Set ranking performance works.", "interview_time_in_minute": 5},
    {"goal_id": "g_04", "topic": "Redis Clustering", "goal": "Assess the candidate's familiarity with Redis Cluster.", "interview_time_in_minute": 5},
    {"goal_id": "g_05", "topic": "Kafka Event Streaming", "goal": "Evaluate the candidate's experience using Kafka to stream leaderboard update events.", "interview_time_in_minute": 5},
    {"goal_id": "g_06", "topic": "SQL Leaderboard Persistence", "goal": "Assess the candidate's approach to persisting leaderboard data in a relational SQL database instead.", "interview_time_in_minute": 5},
    {"goal_id": "g_07", "topic": "Sorted Set Basics", "goal": "Ask the candidate to explain what a Redis Sorted Set is.", "interview_time_in_minute": 5},
    {"goal_id": "g_08", "topic": "Ranking Concepts", "goal": "Ask the candidate to explain how ranking works conceptually.", "interview_time_in_minute": 5},
    {"goal_id": "g_09", "topic": "Redis General Use Cases", "goal": "Evaluate the candidate's general knowledge of Redis use cases beyond leaderboards.", "interview_time_in_minute": 5},
    {"goal_id": "g_10", "topic": "Sorted Set Data Model", "goal": "Assess the candidate's understanding of the Sorted Set data model.", "interview_time_in_minute": 5},
    {"goal_id": "g_11", "topic": "Leaderboard Definition", "goal": "Ask the candidate to define what a leaderboard system is.", "interview_time_in_minute": 5},
    {"goal_id": "g_12", "topic": "Redis vs Memcached", "goal": "Evaluate the candidate's understanding of Redis versus Memcached in general.", "interview_time_in_minute": 5}
]
MOCK_META_11_NARROW_PADDED = {"assumptions": [], "warnings": []}
 
EXPECTED_10_NARROW_DECOMPOSED = {
    "relevance_score": 5,
    "relevance_reasoning": "Every goal stays within the narrow Redis/leaderboard scope the JD describes, at senior-appropriate depth (tradeoffs, failure modes, scale), with no unrelated technologies introduced.",
    "coverage_score": 5,
    "coverage_reasoning": "All 9 checklist required_topics are represented as distinct, non-redundant goals, plus reasonable additional depth (tie-breaking, reset/lifecycle) that fits the same narrow scope without padding.",
    "edge_case_compliance": {
        "narrow_topic_decomposed_not_padded": True,
        "count_time_matched_or_explained": True
    }
}
 
EXPECTED_11_NARROW_PADDED = {
    "relevance_score": 2,
    "relevance_reasoning": "g_05 (Kafka) and g_06 (SQL persistence instead of Redis) directly contradict the JD's explicit '100% Redis-focused' framing — these are ungrounded, unrelated-domain goals. Several others (g_07, g_08, g_11) are textbook-definition trivia rather than senior-level scenario goals.",
    "coverage_score": 1,
    "coverage_reasoning": "Despite having 12 'goals,' only about 2-3 genuinely distinct competencies are tested (g_01/g_02/g_03/g_10 are all near-duplicate rewordings of the same ZSET-ranking idea). Memory/eviction, sharding depth, real-time propagation, persistence/backup, failover, monitoring, and lifecycle/reset are all absent. This is padding, not decomposition.",
    "edge_case_compliance": {
        "narrow_topic_decomposed_not_padded": False,
        "count_time_matched_or_explained": False
    },
    "additional_notes": "Time sums to 60 minutes, not the requested 90 — a second, independent constraint violation on top of the padding problem."
}
 
# ======================================================================
# EXAMPLES — full set for execution loop, with expected scores attached
# ======================================================================
 
EXAMPLES = [
    {
        "name": "Scenario 1a: Baseline Backend - High Quality Plan (Expected: mostly Pass, but check Celery gap)",
        "job_name": JOB_NAME_1, "job_description": JOB_DESCRIPTION_1, "params": PARAMS_1,
        "goals": MOCK_PLAN_1_GOOD, "meta": {"assumptions": [], "warnings": []},
        "expected": EXPECTED_1_GOOD
    },
    {
        "name": "Scenario 1b: Baseline Backend - Textbook Trivia (Expected: Low Scores)",
        "job_name": JOB_NAME_1, "job_description": JOB_DESCRIPTION_1, "params": PARAMS_1,
        "goals": MOCK_PLAN_2_TRIVIA, "meta": {"assumptions": [], "warnings": []},
        "expected": EXPECTED_2_TRIVIA
    },
    {
        "name": "Scenario 1c: Baseline Backend - Constraint Violations (Expected: Fail count/duration + ungrounded goal)",
        "job_name": JOB_NAME_1, "job_description": JOB_DESCRIPTION_1, "params": PARAMS_1,
        "goals": MOCK_PLAN_3_CONSTRAINTS_FAILED, "meta": {"assumptions": [], "warnings": []},
        "expected": EXPECTED_3_CONSTRAINTS_FAILED
    },
    {
        "name": "Scenario 2a: Hardware/Firmware - Correctly Grounded (Expected: Pass)",
        "job_name": JOB_NAME_2, "job_description": JOB_DESCRIPTION_2, "params": PARAMS_2,
        "goals": MOCK_PLAN_4_HARDWARE_GOOD, "meta": {"assumptions": [], "warnings": []},
        "expected": EXPECTED_4_HARDWARE_GOOD
    },
    {
        "name": "Scenario 2b: Hardware/Firmware - Software-Pattern Domain Drift (Expected: Fail)",
        "job_name": JOB_NAME_2, "job_description": JOB_DESCRIPTION_2, "params": PARAMS_2,
        "goals": MOCK_PLAN_5_HARDWARE_SOFTWARE_DRIFT, "meta": {"assumptions": [], "warnings": []},
        "expected": EXPECTED_5_HARDWARE_DRIFT
    },
    {
        "name": "Scenario 3a: Vague Marketing JD - Honest Inference (Expected: Pass)",
        "job_name": JOB_NAME_3, "job_description": JOB_DESCRIPTION_3, "params": PARAMS_3,
        "goals": MOCK_PLAN_6_VAGUE_GOOD, "meta": MOCK_META_6_VAGUE_GOOD,
        "expected": EXPECTED_6_VAGUE_GOOD
    },
    {
        "name": "Scenario 3b: Vague Marketing JD - Fabricated Specifics (Expected: Fail vague-handling)",
        "job_name": JOB_NAME_3, "job_description": JOB_DESCRIPTION_3, "params": PARAMS_3,
        "goals": MOCK_PLAN_7_VAGUE_FABRICATED, "meta": MOCK_META_7_VAGUE_FABRICATED,
        "expected": EXPECTED_7_VAGUE_FABRICATED
    },
    {
        "name": "Scenario 4a: Junior/Contradiction+Discrimination - Correctly Handled (Expected: Pass)",
        "job_name": JOB_NAME_4, "job_description": JOB_DESCRIPTION_4, "params": PARAMS_4,
        "goals": MOCK_PLAN_8_CONTRADICTION_HANDLED, "meta": MOCK_META_8_CONTRADICTION_HANDLED,
        "expected": EXPECTED_8_CONTRADICTION_HANDLED
    },
    {
        "name": "Scenario 4b: Junior/Contradiction+Discrimination - Ignored (Expected: Severe Fail)",
        "job_name": JOB_NAME_4, "job_description": JOB_DESCRIPTION_4, "params": PARAMS_4,
        "goals": MOCK_PLAN_9_CONTRADICTION_IGNORED, "meta": MOCK_META_9_CONTRADICTION_IGNORED,
        "expected": EXPECTED_9_CONTRADICTION_IGNORED
    },
    {
        "name": "Scenario 5a: Narrow Redis Topic + Large Count - Properly Decomposed (Expected: Pass)",
        "job_name": JOB_NAME_5, "job_description": JOB_DESCRIPTION_5, "params": PARAMS_5,
        "goals": MOCK_PLAN_10_NARROW_DECOMPOSED, "meta": MOCK_META_10_NARROW_DECOMPOSED,
        "expected": EXPECTED_10_NARROW_DECOMPOSED
    },
    {
        "name": "Scenario 5b: Narrow Redis Topic + Large Count - Padded with Duplicates/Off-Topic (Expected: Fail)",
        "job_name": JOB_NAME_5, "job_description": JOB_DESCRIPTION_5, "params": PARAMS_5,
        "goals": MOCK_PLAN_11_NARROW_PADDED, "meta": MOCK_META_11_NARROW_PADDED,
        "expected": EXPECTED_11_NARROW_PADDED
    },
]


def run_algorithmic_checks(goals: list, target_count: int, target_duration: int) -> dict:
    """
    Performs deterministic validation on goal lists using simple Python logic.
    """
    actual_count = len(goals)
    actual_duration = sum(g.get("interview_time_in_minute", 0) for g in goals)
    
    # Check for duplicate IDs
    ids = [g.get("goal_id") for g in goals if g.get("goal_id")]
    has_duplicate_ids = len(ids) != len(set(ids))
    
    return {
        "goal_count_matches": actual_count == target_count,
        "actual_count": actual_count,
        "duration_matches": actual_duration == target_duration,
        "actual_duration": actual_duration,
        "has_duplicate_ids": has_duplicate_ids
    }


def main():
    print("=" * 60)
    print("Testing the Re-created qualitative LLM Judge")
    print("=" * 60)
    
    # Initialize the structured LLM judge
    structured_judge = gemini_flash_lite.with_structured_output(PlannerEvaluationResult)
    
    for item in EXAMPLES:
        print(f"\nEvaluating: {item['name']}")
        print("-" * 50)
        
        # 1. Algorithmic checks (fixed logic)
        algo_results = run_algorithmic_checks(
            goals=item["goals"],
            target_count=item["params"]["num_goals"],
            target_duration=item["params"]["total_duration_minutes"]
        )
        
        # Resolve difficulty if it is "infer"
        resolved_diff = item["params"]["difficulty"]
        if resolved_diff == "infer":
            resolved_diff = "junior"
            
        # 2. Format the qualitative user prompt for the LLM
        user_prompt = PLANNER_EVAL_USER_TEMPLATE.format(
            job_name=item["job_name"],
            job_description=item["job_description"],
            difficulty=item["params"]["difficulty"],
            num_goals=item["params"]["num_goals"],
            total_duration_minutes=item["params"]["total_duration_minutes"],
            domain_hint=item["params"].get("domain_hint", "auto"),
            resolved_difficulty=resolved_diff,
            meta_json=json.dumps(item.get("meta", {"assumptions": [], "warnings": []}), indent=2),
            goals_json=json.dumps(item["goals"], indent=2)
        )
        
        messages = [
            SystemMessage(content=PLANNER_EVAL_SYSTEM_INSTRUCTION),
            HumanMessage(content=user_prompt)
        ]
        
        # 3. Invoke LLM Judge for qualitative aspects
        try:
            eval_result: PlannerEvaluationResult = structured_judge.invoke(messages)
            
            # 4. Print Algorithmic Checks
            expected_compliance = item["expected"].get("edge_case_compliance", {})
            expected_count_time = expected_compliance.get("count_time_matched_or_explained")
            
            print("Fixed Algorithmic Checks:")
            print(f"  Goal Count Matches?: {algo_results['goal_count_matches']} (Actual: {algo_results['actual_count']}, Target: {item['params']['num_goals']})")
            print(f"  Duration Sum Matches?: {algo_results['duration_matches']} (Actual: {algo_results['actual_duration']} mins, Target: {item['params']['total_duration_minutes']} mins)")
            print(f"  Has Duplicate Goal IDs?: {algo_results['has_duplicate_ids']}")
            if expected_count_time is not None:
                print(f"  [Expected Budget Match: {expected_count_time}]")
            
            print("\nQualitative LLM Judge Ratings:")
            expected = item["expected"]
            print(f"  Relevance Score: {eval_result.relevance_score}/5 (Expected: {expected.get('relevance_score')}/5)")
            print(f"    Justification: {eval_result.relevance_justification}")
            print(f"  Coverage Score:  {eval_result.coverage_score}/5 (Expected: {expected.get('coverage_score')}/5)")
            print(f"    Justification: {eval_result.coverage_justification}")
            print(f"  Ungrounded Goals: {eval_result.ungrounded_goals}")
            
            # Print actual vs expected edge case compliance
            print("\nLLM Edge Case Compliance Ratings:")
            actual_compliance = eval_result.edge_case_compliance.model_dump()
            for key, val in actual_compliance.items():
                if val is not None or key in expected_compliance:
                    print(f"  {key}: {val} (Expected: {expected_compliance.get(key)})")
            
            print(f"\nOverall Notes: {eval_result.overall_notes}")
        except Exception as e:
            print(f"Error during evaluation: {e}")
            import traceback
            traceback.print_exc()
            
        print("=" * 60)

if __name__ == "__main__":
    main()
