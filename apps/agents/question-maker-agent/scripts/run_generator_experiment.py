import os
import sys
import json
import importlib
from typing import Dict, Any

os.environ["LANGCHAIN_PROJECT"] = "auto-recruiter"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env")))

from langsmith import Client, evaluate
from langchain_core.messages import SystemMessage, HumanMessage

# Import Gemini client
from apps.agents.shared.clients import gemini_flash_lite

# Import generator node
generator_module = importlib.import_module("question-maker-agent.nodes.generator")
generateQuestionItemFromGoal = generator_module.generateQuestionItemFromGoal

# Import schemas
state_module = importlib.import_module("question-maker-agent.state")
InterviewGoal = state_module.InterviewGoal
GroundingTheory = state_module.GroundingTheory
GeneratorState = state_module.GeneratorState
CriticFeedback = state_module.CriticFeedback

# Import Validator prompt
validator_prompt_module = importlib.import_module("question-maker-agent.prompts.validator_prompt")
# Use the correct variable name we fixed earlier
JUDGE_SYSTEM_INSTRUCTION = getattr(validator_prompt_module, "JUDGE_SYSTEM_INSTRUCTION", "")

"""
Generator eval fixtures. Each entry provides realistic `inputs` (matching
the retriever/planner output shape) with `outputs: {}` left for the
generator to fill in during a real run.

Coverage map (why each of the 20 exists):
  1  - baseline clean case
  2  - nuanced/conditional theory (real exceptions, must not invent more)
  3  - shortest time tier (1-2 min)
  4  - longest time tier (30 min), no grounding, staged system design
  5  - GROUNDING INTEGRITY: need_grounding=True but theory is missing/null
  6  - GROUNDING INTEGRITY: need_grounding=False but theory attached anyway
  7  - non-technical/behavioral goal, no grounding
  8  - precise list-based grounding (exact enumerated identifiers)
  9  - formula/numeric grounding
  10 - hallucination-bait: deep DB internals, easy to overreach past theory
  11 - security domain, moderate grounding
  12 - deliberately vague/broad goal, no grounding
  13 - deliberately terse one-line theory
  14 - mixed-credibility references (tier A + tier B, non-corroborated)
  15 - design/UX domain (non-engineering technical)
  16 - statistics domain with real numeric grounding
  17 - hallucination-bait: expert-level networking, long time tier
  18 - deliberately trivial/low-bar goal, short time
  19 - SCOPE PRECISION: explicit negative constraint ("X, not Y")
  20 - shortest possible time tier + trivial goal + no grounding
"""

DATASET_EXAMPLES = [

    # 1 — Baseline clean case.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_01",
                "topic": "Python Concurrency",
                "goal": "Evaluate candidate's understanding of event loops and coroutines in Python.",
                "interview_time_in_minute": 10,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_01",
                "theory": (
                    "The event loop is the core of asyncio. Coroutines pause "
                    "execution at await, yielding control to the event loop. "
                    "asyncio.gather runs awaitables concurrently."
                ),
                "references": [],
            },
        },
        "outputs": {},
    },

    # 2 — Nuanced/conditional theory with real exceptions (given example,
    # kept verbatim). Tests whether the generator represents the actual
    # exceptions rather than inventing simpler or additional ones.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_02",
                "topic": "GDPR Compliance",
                "goal": "Evaluate candidate's understanding of GDPR data retention limits and the right to erasure, including when erasure can legally be refused.",
                "interview_time_in_minute": 15,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_02",
                "theory": (
                    "### GDPR Data Retention and Erasure Obligations\n\n"
                    "#### Data Retention: The Storage Limitation Principle\n"
                    "Under the General Data Protection Regulation (GDPR), there is no single, "
                    "universal retention period for personal data. Instead, compliance is "
                    "governed by the storage limitation principle defined in Article 5(1)(e). "
                    "This principle mandates that personal data must be kept in a form which "
                    "permits identification of data subjects for no longer than is necessary "
                    "for the purposes for which the personal data are processed.\n\n"
                    "Organizations are required to:\n"
                    "* Document Purposes: Clearly define the purpose for which data is collected and processed.\n"
                    "* Maintain Retention Schedules: Rather than applying a blanket policy, organizations must "
                    "maintain a retention schedule that maps specific categories of data to defined retention "
                    "periods and their corresponding legal bases.\n"
                    "* Navigate Overlapping Laws: While GDPR sets the general principle, sector-specific "
                    "regulations (such as Anti-Money Laundering (AML) laws for financial records) may impose "
                    "mandatory minimum retention periods. These legal obligations override the general storage "
                    "limitation principle for the specific data categories they govern.\n\n"
                    "#### Right to Erasure (The \"Right to be Forgotten\")\n"
                    "The right to erasure, codified in Article 17, allows data subjects to request the deletion "
                    "of their personal data under specific circumstances. However, this right is not absolute.\n\n"
                    "Key Exceptions to Erasure:\n"
                    "Article 17(3) provides specific grounds under which an organization may refuse a request "
                    "for erasure. These include, but are not limited to:\n"
                    "* Compliance with a Legal Obligation: When processing is necessary for compliance with a "
                    "legal obligation which requires processing by Union or Member State law (e.g., tax or "
                    "financial record-keeping requirements).\n"
                    "* Freedom of Expression and Information: When the processing is necessary for exercising "
                    "the right of freedom of expression and information.\n"
                    "* Public Interest: When processing is necessary for reasons of public interest in the area "
                    "of public health.\n"
                    "* Legal Claims: When processing is necessary for the establishment, exercise, or defense "
                    "of legal claims.\n\n"
                    "Compliance requires organizations to balance the data subject's request against these "
                    "legal justifications, ensuring that data is only retained when a valid, documented legal "
                    "basis exists to override the request for deletion."
                ),
                "references": [
                    {
                        "url": "gdpr.eu",
                        "matched_query": "GDPR right to erasure Article 17 exceptions",
                        "title": "GDPR Article 17 Right to Erasure",
                        "credibility_tier": "A",
                        "excerpt": "Article 17(3) lists exceptions to erasure, including freedom of expression, compliance with a legal obligation, and public interest in public health.",
                        "corroborated": True,
                    },
                    {
                        "url": "gdpr.eu",
                        "matched_query": "GDPR data retention period requirements enterprise",
                        "title": "GDPR Storage Limitation Principle",
                        "credibility_tier": "A",
                        "excerpt": "There is no single fixed retention period defined by GDPR; Article 5(1)(e) requires data be kept no longer than necessary for its documented purpose (storage limitation principle).",
                        "corroborated": True,
                    },
                    {
                        "url": "edpb.europa.eu",
                        "matched_query": "GDPR data retention period requirements enterprise",
                        "title": "EDPB Retention Schedule Guidance",
                        "credibility_tier": "A",
                        "excerpt": "Organizations are expected to maintain a retention schedule mapping data categories to specific retention periods and legal bases, rather than a single blanket policy. Some sector-specific laws (e.g. AML financial record rules) impose fixed minimums that override the general storage-limitation principle for that data category.",
                        "corroborated": True,
                    },
                ],
            },
        },
        "outputs": {},
    },

    # 3 — Shortest realistic time tier. Simple topic, terse grounding.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_03",
                "topic": "HTTP Fundamentals",
                "goal": "Evaluate candidate's understanding of when to use 4xx versus 5xx status codes.",
                "interview_time_in_minute": 2,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_03",
                "theory": (
                    "4xx status codes indicate the client made an error (e.g. bad request, "
                    "unauthorized, not found). 5xx status codes indicate the server failed to "
                    "fulfill a valid request (e.g. internal error, service unavailable)."
                ),
                "references": [],
            },
        },
        "outputs": {},
    },

    # 4 — Longest time tier, staged system design, no grounding needed.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_04",
                "topic": "System Design",
                "goal": "Evaluate candidate's ability to design a rate limiter for a public API, including how it behaves under scale and failure.",
                "interview_time_in_minute": 30,
                "need_grounding": False,
            },
            "theory": None,
        },
        "outputs": {},
    },

    # 5 — GROUNDING INTEGRITY EDGE CASE: need_grounding=True but the
    # theory object is missing/null (simulated retriever failure).
    {
        "inputs": {
            "goal": {
                "goal_id": "g_05",
                "topic": "OAuth2",
                "goal": "Evaluate candidate's understanding of the OAuth2 authorization code flow and why it's preferred over the implicit flow for server-side apps.",
                "interview_time_in_minute": 10,
                "need_grounding": True,
            },
            "theory": None,
        },
        "outputs": {},
    },

    # 6 — GROUNDING INTEGRITY EDGE CASE: need_grounding=False but a theory
    # was attached anyway (simulated upstream inconsistency).
    {
        "inputs": {
            "goal": {
                "goal_id": "g_06",
                "topic": "Version Control",
                "goal": "Evaluate candidate's understanding of when to use git rebase versus git merge.",
                "interview_time_in_minute": 10,
                "need_grounding": False,
            },
            "theory": {
                "goal_id": "g_06",
                "theory": (
                    "git merge creates a new commit joining two histories, preserving both "
                    "branches' commit history. git rebase replays commits from one branch "
                    "onto another, producing a linear history but rewriting commit hashes."
                ),
                "references": [
                    {
                        "url": "git-scm.com",
                        "matched_query": "git rebase vs merge",
                        "title": "Git Branching - Rebasing",
                        "credibility_tier": "A",
                        "excerpt": "Rebasing replays commits on top of another base tip, producing a linear history.",
                        "corroborated": True,
                    }
                ],
            },
        },
        "outputs": {},
    },

    # 7 — Non-technical/behavioral goal, no grounding.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_07",
                "topic": "Product Management",
                "goal": "Evaluate candidate's ability to prioritize competing stakeholder requests under limited engineering capacity.",
                "interview_time_in_minute": 12,
                "need_grounding": False,
            },
            "theory": None,
        },
        "outputs": {},
    },

    # 8 — Precise, exhaustive list-based grounding. Tests whether the
    # generator gets the specifics right (or invents extra items) when
    # the theory contains an enumerated, countable list.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_08",
                "topic": "Healthcare Data Privacy",
                "goal": "Evaluate candidate's understanding of the HIPAA Safe Harbor de-identification method.",
                "interview_time_in_minute": 15,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_08",
                "theory": (
                    "Under the HIPAA Safe Harbor method, data is considered de-identified only "
                    "if 18 specific categories of identifiers are removed, including names, "
                    "geographic subdivisions smaller than a state, all elements of dates "
                    "(except year) directly related to an individual, telephone numbers, and "
                    "medical record numbers. Additionally, the covered entity must have no "
                    "actual knowledge that the remaining information could be used, alone or "
                    "in combination with other information, to identify the individual."
                ),
                "references": [
                    {
                        "url": "hhs.gov",
                        "matched_query": "HIPAA safe harbor de-identification 18 identifiers",
                        "title": "HHS Guidance on De-identification of PHI",
                        "credibility_tier": "A",
                        "excerpt": "The Safe Harbor method requires removal of 18 specified identifier categories and requires no actual knowledge that remaining data could re-identify an individual.",
                        "corroborated": True,
                    }
                ],
            },
        },
        "outputs": {},
    },

    # 9 — Formula/numeric grounding. Tests correct use of a given formula
    # without inventing a different one or extra numeric claims.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_09",
                "topic": "Personal Finance / Mortgages",
                "goal": "Evaluate candidate's understanding of how mortgage amortization allocates payments between principal and interest over time.",
                "interview_time_in_minute": 10,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_09",
                "theory": (
                    "In an amortizing loan, each fixed payment is split between interest and "
                    "principal. Interest for a period is calculated as the remaining principal "
                    "balance multiplied by the periodic interest rate. Early in the loan term, "
                    "the interest portion is larger because the outstanding balance is higher; "
                    "as the balance decreases, a larger share of each fixed payment goes toward "
                    "principal."
                ),
                "references": [],
            },
        },
        "outputs": {},
    },

    # 10 — HALLUCINATION-BAIT: deep database internals. A model's training
    # confidence on Postgres internals usually exceeds what's actually in
    # the supplied theory — tests overreach resistance.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_10",
                "topic": "PostgreSQL Internals",
                "goal": "Evaluate candidate's understanding of MVCC (multi-version concurrency control) and why VACUUM is necessary.",
                "interview_time_in_minute": 15,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_10",
                "theory": (
                    "PostgreSQL uses MVCC: instead of updating a row in place, an UPDATE marks "
                    "the old row version as dead and inserts a new row version. This allows "
                    "concurrent readers to see a consistent snapshot without blocking writers. "
                    "Dead row versions accumulate over time and must be reclaimed by VACUUM, "
                    "which also updates statistics used by the query planner and prevents "
                    "transaction ID wraparound."
                ),
                "references": [
                    {
                        "url": "postgresql.org",
                        "matched_query": "postgresql MVCC vacuum",
                        "title": "PostgreSQL Documentation: Concurrency Control",
                        "credibility_tier": "A",
                        "excerpt": "PostgreSQL provides MVCC by keeping multiple versions of rows; VACUUM reclaims space from dead row versions and prevents transaction ID wraparound.",
                        "corroborated": True,
                    }
                ],
            },
        },
        "outputs": {},
    },

    # 11 — Security domain, moderate grounding.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_11",
                "topic": "Application Security",
                "goal": "Evaluate candidate's understanding of why hardcoded secrets in source code are dangerous and what to use instead.",
                "interview_time_in_minute": 10,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_11",
                "theory": (
                    "Hardcoded secrets committed to source control remain in the repository's "
                    "history even after removal from the latest commit, and are exposed to "
                    "anyone with repo access, including in forks and CI logs. Secrets should "
                    "instead be injected at runtime via a secrets manager or environment "
                    "variables sourced from a secure vault, with access scoped and rotated "
                    "independently of code deployments."
                ),
                "references": [],
            },
        },
        "outputs": {},
    },

    # 12 — Deliberately vague/broad goal with no topic-level constraints.
    # Tests whether the generator narrows this into something concrete
    # rather than producing an equally vague question.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_12",
                "topic": "General Engineering Judgment",
                "goal": "Evaluate candidate's overall engineering judgment.",
                "interview_time_in_minute": 12,
                "need_grounding": False,
            },
            "theory": None,
        },
        "outputs": {},
    },

    # 13 — Deliberately terse, single-sentence theory.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_13",
                "topic": "Algorithms",
                "goal": "Evaluate candidate's understanding of Big-O notation.",
                "interview_time_in_minute": 8,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_13",
                "theory": "Big-O describes the upper bound growth rate of an algorithm's running time as input size grows.",
                "references": [],
            },
        },
        "outputs": {},
    },

    # 14 — Mixed-credibility references: tier A + tier B, one
    # non-corroborated. Tests whether the generator treats all grounding
    # as equally solid when it shouldn't, and whether it stays especially
    # conservative in a domain with real-world stakes.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_14",
                "topic": "Vaccine Cold Chain Logistics",
                "goal": "Evaluate candidate's understanding of temperature requirements and exceptions for vaccine cold chain storage.",
                "interview_time_in_minute": 12,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_14",
                "theory": (
                    "Most vaccines must be stored between 2-8°C throughout transport and "
                    "storage. Some vaccine formulations (e.g. certain mRNA vaccines) require "
                    "ultra-cold storage as low as -70°C, though some manufacturers have since "
                    "approved standard refrigerator temperatures for shorter storage windows "
                    "after formulation changes. Any excursion outside the approved range must "
                    "be logged and the affected doses evaluated before administration."
                ),
                "references": [
                    {
                        "url": "who.int",
                        "matched_query": "vaccine cold chain temperature requirements",
                        "title": "WHO Vaccine Management Handbook",
                        "credibility_tier": "A",
                        "excerpt": "Most vaccines require storage at 2-8°C; temperature excursions must be logged and doses assessed before use.",
                        "corroborated": True,
                    },
                    {
                        "url": "vaccinelogisticsblog.example",
                        "matched_query": "ultra cold storage mRNA vaccine updates",
                        "title": "Cold Chain Update: Storage Flexibility for mRNA Vaccines",
                        "credibility_tier": "B",
                        "excerpt": "Some manufacturers now permit standard refrigerator storage for limited windows following formulation updates, though guidance varies by product and region.",
                        "corroborated": False,
                    },
                ],
            },
        },
        "outputs": {},
    },

    # 15 — Design/UX domain, non-engineering technical content.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_15",
                "topic": "UX Design",
                "goal": "Evaluate candidate's understanding of when to use a modal versus inline validation for form errors.",
                "interview_time_in_minute": 10,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_15",
                "theory": (
                    "Inline validation shows errors next to the relevant field as the user "
                    "types or on blur, letting users correct mistakes without losing context. "
                    "Modals interrupt the flow entirely and are generally reserved for "
                    "blocking, high-severity errors (e.g. failed submission after a network "
                    "error) rather than routine field-level validation, since frequent modal "
                    "interruptions increase cognitive load and task abandonment."
                ),
                "references": [],
            },
        },
        "outputs": {},
    },

    # 16 — Statistics domain with real numeric grounding.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_16",
                "topic": "Statistics",
                "goal": "Evaluate candidate's understanding of Type I and Type II errors in hypothesis testing.",
                "interview_time_in_minute": 10,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_16",
                "theory": (
                    "A Type I error occurs when the null hypothesis is rejected even though it "
                    "is true (a false positive), with probability controlled by the chosen "
                    "significance level, typically 0.05. A Type II error occurs when the null "
                    "hypothesis is not rejected even though it is false (a false negative), "
                    "with probability denoted beta; statistical power is 1 - beta. Reducing "
                    "the significance level to lower Type I error risk generally increases "
                    "Type II error risk, all else equal."
                ),
                "references": [],
            },
        },
        "outputs": {},
    },

    # 17 — HALLUCINATION-BAIT: expert-level networking, long time tier.
    # Deep enough that a model's confident prior knowledge often exceeds
    # what's actually supplied in the theory.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_17",
                "topic": "Network Congestion Control",
                "goal": "Evaluate deep expert-level understanding of TCP congestion control behavior (Reno-style vs BBR-style) under high-latency, lossy links such as satellite connections.",
                "interview_time_in_minute": 25,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_17",
                "theory": (
                    "Loss-based congestion control algorithms (e.g. Reno, Cubic) treat packet "
                    "loss as the primary signal of congestion and reduce the congestion window "
                    "sharply on detecting loss. On high-latency, lossy links such as satellite "
                    "connections, this causes throughput collapse even when loss is due to "
                    "link error rather than actual congestion, since the algorithm cannot "
                    "distinguish the two. BBR instead models the bottleneck bandwidth and "
                    "round-trip propagation time directly and paces sending based on that "
                    "model, making it less sensitive to non-congestive packet loss."
                ),
                "references": [
                    {
                        "url": "research.google",
                        "matched_query": "BBR congestion control high latency lossy links",
                        "title": "BBR: Congestion-Based Congestion Control",
                        "credibility_tier": "A",
                        "excerpt": "Loss-based algorithms misinterpret non-congestive loss as a congestion signal, causing throughput collapse on lossy links; BBR models bandwidth and RTT directly instead.",
                        "corroborated": True,
                    }
                ],
            },
        },
        "outputs": {},
    },

    # 18 — Deliberately trivial/low-bar goal, short time. Tests whether
    # the generator avoids over-engineering complexity for a goal that
    # explicitly asks for a basic bar.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_18",
                "topic": "Web Basics",
                "goal": "Evaluate whether the candidate has basic familiarity with what a REST API is.",
                "interview_time_in_minute": 5,
                "need_grounding": False,
            },
            "theory": None,
        },
        "outputs": {},
    },

    # 19 — SCOPE PRECISION: explicit negative constraint. Tests whether
    # the generator stays narrowly on the stated focus (write cost) rather
    # than drifting into the adjacent, more commonly-discussed topic
    # (read benefits) that the goal explicitly excludes.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_19",
                "topic": "Database Indexing",
                "goal": "Evaluate candidate's understanding of the write-amplification cost that indexes impose on insert/update operations. Do not evaluate their understanding of read-performance benefits — that is covered by a separate goal.",
                "interview_time_in_minute": 10,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_19",
                "theory": (
                    "Every index on a table must be updated whenever a row is inserted, "
                    "updated, or deleted, since the index maintains its own ordered structure "
                    "reflecting the indexed column's values. More indexes on a table mean more "
                    "write work per row-modifying operation, which can significantly slow bulk "
                    "inserts and increase write-path latency, independent of any benefit the "
                    "indexes provide to read queries."
                ),
                "references": [],
            },
        },
        "outputs": {},
    },

    # 20 — Shortest possible time tier, trivial goal, no grounding.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_20",
                "topic": "Version Control Basics",
                "goal": "Confirm the candidate has basic familiarity with what version control is and why teams use it.",
                "interview_time_in_minute": 1,
                "need_grounding": False,
            },
            "theory": None,
        },
        "outputs": {},
    },

    # 21 — RETRY: single-check failure, pushback_actionability. Tests
    # whether the generator fixes only the flagged array and leaves the
    # rest of the previous attempt untouched.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_21",
                "topic": "Python Concurrency",
                "goal": "Evaluate candidate's understanding of event loops and coroutines in Python.",
                "interview_time_in_minute": 10,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_21",
                "theory": (
                    "The event loop is the core of asyncio. Coroutines pause "
                    "execution at await, yielding control to the event loop. "
                    "asyncio.gather runs awaitables concurrently."
                ),
                "references": [],
            },
            "critic_feedback": {
                "layer": 2,
                "failed_checks": [
                    {
                        "check": "pushback_actionability",
                        "issue": "pushback_triggers is empty. At least one actionable pushback_trigger with a real, literally-askable follow_up_prompt is required.",
                    }
                ],
            },
            "previous_generation": {
                "suggested_opening": "How does the event loop work in Python asyncio?",
                "passing_criteria": [
                    "Mentions event loop scheduling",
                    "Mentions await yielding control",
                ],
                "wrong_answer_signals": [
                    {"signal": "Says threads are used for everything", "severity": "critical"}
                ],
                "pushback_triggers": [],
            },
        },
        "outputs": {},
    },

    # 22 — RETRY: single-check failure, signal_classification. A hard
    # misconception was misplaced in pushback_triggers on the previous
    # attempt. Tests whether the retry moves it to wrong_answer_signals
    # with the correct shape, rather than just rewording it in place.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_22",
                "topic": "Memory Management",
                "goal": "Evaluate candidate's understanding of garbage collection timing in managed languages.",
                "interview_time_in_minute": 10,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_22",
                "theory": (
                    "Garbage collection reclaims memory from objects that are no longer "
                    "reachable, but it does not happen instantly upon an object becoming "
                    "unreachable — the collector runs on its own schedule (e.g. triggered by "
                    "allocation thresholds or explicit invocation), so there can be a delay "
                    "before memory is actually reclaimed."
                ),
                "references": [],
            },
            "critic_feedback": {
                "layer": 2,
                "failed_checks": [
                    {
                        "check": "signal_classification",
                        "issue": "pushback_triggers contains 'Claims garbage collection instantly frees memory the moment an object becomes unreachable' — this is a flat factual error, not an incomplete-but-plausible answer. It must be moved to wrong_answer_signals with severity 'critical', not left as a pushback_trigger.",
                    }
                ],
            },
            "previous_generation": {
                "suggested_opening": "You notice memory usage staying high right after a large object should have gone out of scope. What would you check?",
                "passing_criteria": [
                    "States that becoming unreachable doesn't guarantee immediate reclamation",
                    "Mentions checking for lingering references or waiting for the next collection cycle",
                ],
                "wrong_answer_signals": [
                    "Claims manually setting a reference to null always immediately frees the memory"
                ],
                "pushback_triggers": [
                    {
                        "trigger": "Claims garbage collection instantly frees memory the moment an object becomes unreachable",
                        "severity": "mild",
                        "pushback_type": "clarification"
                    }
                ],
            },
        },
        "outputs": {},
    },

    # 23 — RETRY: single-check failure, grounding_fidelity. A specific
    # detail in passing_criteria isn't traceable to the grounding_theory.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_23",
                "topic": "Kubernetes",
                "goal": "Evaluate candidate's understanding of Kubernetes pod scheduling.",
                "interview_time_in_minute": 15,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_23",
                "theory": (
                    "The kube-scheduler assigns pods to nodes based on resource requests, "
                    "affinity/anti-affinity rules, and taints/tolerations."
                ),
                "references": [],
            },
            "critic_feedback": {
                "layer": 2,
                "failed_checks": [
                    {
                        "check": "grounding_fidelity",
                        "issue": "passing_criteria states the scheduler uses the 'Bin-Packing v3 algorithm introduced in Kubernetes 1.29' — this specific algorithm name and version is not present in grounding_theory and must be removed or replaced with something traceable to it.",
                    }
                ],
            },
            "previous_generation": {
                "suggested_opening": "Some of your pods are stuck in Pending state even though nodes have free capacity. How would you debug why the scheduler isn't placing them?",
                "passing_criteria": [
                    "Checks resource requests against available node capacity",
                    "States that the scheduler uses the 'Bin-Packing v3 algorithm introduced in Kubernetes 1.29' to make placement decisions",
                    "Checks for taints on nodes without matching tolerations on the pod",
                ],
                "wrong_answer_signals": [
                    {"signal": "Claims pods are scheduled purely at random with no resource awareness", "severity": "critical"}
                ],
                "pushback_triggers": [
                    {
                        "trigger_condition": "Mentions taints/tolerations but doesn't explain how they interact with scheduling",
                        "follow_up_prompt": "How exactly does a toleration change whether a pod can land on a tainted node?",
                    }
                ],
            },
        },
        "outputs": {},
    },

    # 24 — RETRY: multi-check failure (goal_alignment + passing_criteria_
    # valid together). Tests whether a broader failure correctly triggers
    # a larger rewrite of suggested_opening and passing_criteria, while
    # wrong_answer_signals and pushback_triggers — which weren't flagged
    # — can still reasonably carry over or be lightly adapted.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_24",
                "topic": "Database Security",
                "goal": "Evaluate candidate's understanding of SQL injection prevention techniques.",
                "interview_time_in_minute": 8,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_24",
                "theory": (
                    "Parameterized queries (prepared statements) prevent SQL injection by "
                    "separating query structure from user-supplied data, so input is never "
                    "interpreted as SQL syntax."
                ),
                "references": [],
            },
            "critic_feedback": {
                "layer": 2,
                "failed_checks": [
                    {
                        "check": "goal_alignment",
                        "issue": "suggested_opening asks about schema normalization tradeoffs, which does not evaluate SQL injection prevention at all — it's off-topic for this goal.",
                    },
                    {
                        "check": "passing_criteria_valid",
                        "issue": "passing_criteria items ('Understands database design well', 'Has good judgment about tradeoffs') are not observable and don't relate to the actual goal of SQL injection prevention.",
                    },
                ],
            },
            "previous_generation": {
                "suggested_opening": "You're designing a schema for an e-commerce orders table. How would you decide whether to normalize customer address data into a separate table?",
                "passing_criteria": [
                    "Understands database design well",
                    "Has good judgment about tradeoffs",
                ],
                "wrong_answer_signals": [
                    {"signal": "Claims normalization has no performance implications at all", "severity": "moderate"}
                ],
                "pushback_triggers": [
                    {
                        "trigger_condition": "Mentions denormalization for performance without naming a specific tradeoff",
                        "follow_up_prompt": "What's the specific cost you're trying to avoid by denormalizing here?",
                    }
                ],
            },
        },
        "outputs": {},
    },

    # 25 — RETRY: Layer 1 schema failure. Different, terser feedback
    # shape than a Layer 2 qualitative failure — no reasoning text, just
    # a list of structurally missing/invalid fields. Tests whether the
    # generator handles this format correctly per the prompt's explicit
    # instruction to treat it the same way as a named Layer 2 check.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_25",
                "topic": "React",
                "goal": "Evaluate candidate's understanding of when to lift state up versus keep it local.",
                "interview_time_in_minute": 10,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_25",
                "theory": (
                    "In React, state should be lifted to the closest common ancestor of "
                    "components that need to share it. Props pass data down; state changes "
                    "should generally flow through the component that owns it."
                ),
                "references": [],
            },
            "critic_feedback": {
                "layer": 1,
                "failed_checks": [
                    "missing or empty: wrong_answer_signals",
                    "invalid severity: None",
                ],
            },
            "previous_generation": {
                "suggested_opening": "Two sibling components both need to reflect the same filter selection. Where would you put that state, and why?",
                "passing_criteria": [
                    "States that the state should be lifted to the closest common parent",
                    "Explains that the parent passes the value and an updater down as props",
                ],
                "wrong_answer_signals": [],
                "pushback_triggers": [
                    {
                        "trigger_condition": "Mentions 'lifting state up' vaguely without describing the mechanism",
                        "follow_up_prompt": "What would the parent component actually need to pass down to make this work?",
                    }
                ],
            },
        },
        "outputs": {},
    },

    # 26 — RETRY: stubborn second attempt. The SAME check failed twice in
    # a row, with different specifics each time — simulates a model that
    # fixed the letter of the first complaint but not the underlying
    # pattern. Tests whether feedback that's more specific the second
    # time actually produces a correct fix, or whether the model repeats
    # a similar mistake.
    {
        "inputs": {
            "goal": {
                "goal_id": "g_26",
                "topic": "Data Structures",
                "goal": "Evaluate candidate's understanding of when to use a hash table versus a balanced tree.",
                "interview_time_in_minute": 10,
                "need_grounding": True,
            },
            "theory": {
                "goal_id": "g_26",
                "theory": (
                    "Hash tables offer average O(1) lookup/insert but no ordering guarantee. "
                    "Balanced trees offer O(log n) operations but maintain sorted order, "
                    "enabling range queries and ordered traversal."
                ),
                "references": [],
            },
            "critic_feedback": {
                "layer": 2,
                "failed_checks": [
                    {
                        "check": "pushback_actionability",
                        "issue": "This is the SECOND attempt. Your first fix changed the follow_up_prompt to 'Think about how range queries would work with a hash table' — this is still an instruction to the interviewer, not a question the interviewer could read aloud to the candidate. It must be phrased as a direct question addressed to the candidate.",
                    }
                ],
            },
            "previous_generation": {
                "suggested_opening": "You need a data structure to store user sessions by ID for fast lookup, and separately one to store a leaderboard that needs range queries like 'top 10 scores.' Which would you use for each, and why?",
                "passing_criteria": [
                    "Chooses a hash table for session lookup, citing average O(1) access with no ordering need",
                    "Chooses a balanced tree for the leaderboard, citing the need for ordered traversal and range queries",
                ],
                "wrong_answer_signals": [
                    {"signal": "Claims hash tables maintain insertion or sorted order by default", "severity": "moderate"}
                ],
                "pushback_triggers": [
                    {
                        "trigger_condition": "Picks a hash table for the leaderboard without addressing how range queries would work",
                        "follow_up_prompt": "Think about how range queries would work with a hash table.",
                    }
                ],
            },
        },
        "outputs": {},
    },
]


def evaluate_generator_target(inputs: dict) -> dict:
    """
    Transforms the dataset inputs into models and runs the generator node.
    """
    goal_data = inputs.get("goal", {})
    theory_data = inputs.get("theory")
    critic_feedback = inputs.get("critic_feedback")
    previous_generation_data = inputs.get("previous_generation")
    
    goal = InterviewGoal(**goal_data)
    theory = GroundingTheory(**theory_data) if theory_data else None
    
    state_module = importlib.import_module("question-maker-agent.state")
    QuestionItem = state_module.QuestionItem
    
    if previous_generation_data:
        # Fill missing required fields from the main goal (for older datasets)
        if "goal_id" not in previous_generation_data:
            previous_generation_data["goal_id"] = goal.goal_id
        if "topic" not in previous_generation_data:
            previous_generation_data["topic"] = goal.topic
        if "goal" not in previous_generation_data:
            previous_generation_data["goal"] = goal.goal
        if "references" not in previous_generation_data:
            previous_generation_data["references"] = []
        if "interview_time_in_minute" not in previous_generation_data:
            previous_generation_data["interview_time_in_minute"] = goal.interview_time_in_minute
            
        # Fix wrong_answer_signals if they are dicts instead of strings
        if "wrong_answer_signals" in previous_generation_data:
            fixed_signals = []
            for w in previous_generation_data["wrong_answer_signals"]:
                if isinstance(w, dict):
                    fixed_signals.append(w.get("signal", str(w)))
                else:
                    fixed_signals.append(w)
            previous_generation_data["wrong_answer_signals"] = fixed_signals
            
        # Fix pushback_triggers if they use old schema keys
        if "pushback_triggers" in previous_generation_data:
            fixed_triggers = []
            for p in previous_generation_data["pushback_triggers"]:
                if "trigger" not in p and "trigger_condition" in p:
                    fixed_triggers.append({
                        "trigger": p["trigger_condition"],
                        "severity": p.get("severity") if p.get("severity") in ["critical", "mild"] else "mild",
                        "pushback_type": p.get("pushback_type", "clarification")
                    })
                else:
                    if p.get("severity") not in ["critical", "mild"]:
                        p["severity"] = "mild"
                    fixed_triggers.append(p)
            previous_generation_data["pushback_triggers"] = fixed_triggers
            
    previous_generation = QuestionItem(**previous_generation_data) if previous_generation_data else None
    
    state = GeneratorState(
        goal=goal, 
        theory=theory,
        critic_feedback=critic_feedback,
        previous_generation=previous_generation
    )
    
    # Generate the question
    try:
        result = generateQuestionItemFromGoal(state)
        questions = result.get("generated_questions", [])
        if not questions:
            return {"error": "No questions generated"}
        
        # Return the generated question as a dict
        q = questions[0]
        return {
            "suggested_opening": q.suggested_opening,
            "passing_criteria": q.passing_criteria,
            "wrong_answer_signals": [w for w in q.wrong_answer_signals],
            "pushback_triggers": [{"trigger": getattr(p, "trigger", getattr(p, "trigger_condition", "")), "severity": getattr(p, "severity", ""), "pushback_type": getattr(p, "pushback_type", "")} for p in q.pushback_triggers]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def validator_judge_evaluator(run, example) -> dict:
    """
    Evaluates the generated output using the Validator Judge logic.
    Returns a multi-metric dictionary.
    """
    output = run.outputs
    if "error" in output:
        return {"key": "generation_success", "score": 0, "comment": output["error"]}
        
    inputs = example.inputs
    topic = inputs["goal"]["topic"]
    goal_desc = inputs["goal"]["goal"]
    theory_text = (inputs.get("theory") or {}).get("theory", "None provided")
    
    generated_json = json.dumps(output, indent=2)
    
    user_prompt = f"""
    [TOPIC]: {topic}
    [GOAL]: {goal_desc}
    [GROUNDING_THEORY]: {theory_text}
    
    [GENERATED_QUESTION]:
    {generated_json}
    """
    
    messages = [
        SystemMessage(content=JUDGE_SYSTEM_INSTRUCTION),
        HumanMessage(content=user_prompt)
    ]
    
    judge_model = gemini_flash_lite.with_structured_output(CriticFeedback)
    
    try:
        feedback = judge_model.invoke(messages)
        
        # Map boolean pass to 1/0
        return {
            "results": [
                {
                    "key": "goal_alignment",
                    "score": 1 if feedback.checks.goal_alignment.pass_ else 0,
                    "comment": feedback.checks.goal_alignment.reasoning
                },
                {
                    "key": "passing_criteria_valid",
                    "score": 1 if feedback.checks.passing_criteria_valid.pass_ else 0,
                    "comment": feedback.checks.passing_criteria_valid.reasoning
                },
                {
                    "key": "grounding_fidelity",
                    "score": 1 if feedback.checks.grounding_fidelity.pass_ else 0,
                    "comment": "; ".join(feedback.checks.grounding_fidelity.unsupported_claims) if feedback.checks.grounding_fidelity.unsupported_claims else "Pass"
                },
                {
                    "key": "signal_classification",
                    "score": 1 if feedback.checks.signal_classification.pass_ else 0,
                    "comment": "; ".join(feedback.checks.signal_classification.issues) if feedback.checks.signal_classification.issues else "Pass"
                },
                {
                    "key": "pushback_actionability",
                    "score": 1 if feedback.checks.pushback_actionability.pass_ else 0,
                    "comment": "; ".join(feedback.checks.pushback_actionability.issues) if feedback.checks.pushback_actionability.issues else "Pass"
                },
                {
                    "key": "overall_verdict",
                    "score": 1 if feedback.verdict == "pass" else 0,
                    "comment": feedback.verdict
                }
            ]
        }
    except Exception as e:
        return {"key": "evaluation_error", "score": 0, "comment": str(e)}

if __name__ == "__main__":
    client = Client()
    
    dataset_name = "Generator-Eval-Dataset-v2"
    
    # Check if dataset exists, if not create it
    if not client.has_dataset(dataset_name=dataset_name):
        print(f"Creating dataset '{dataset_name}'...")
        dataset = client.create_dataset(dataset_name=dataset_name, description="Dataset for evaluating Generator Node with Validator Judge")
        for ex in DATASET_EXAMPLES:
            client.create_example(
                inputs=ex["inputs"],
                outputs=ex["outputs"],
                dataset_id=dataset.id,
            )
        print("Dataset created and populated.")
    else:
        print(f"Dataset '{dataset_name}' already exists.")

    print("Running Generator evaluation experiment...")
    
    experiment_results = evaluate(
        evaluate_generator_target,
        data=dataset_name,
        evaluators=[validator_judge_evaluator],
        experiment_prefix="Generator-Eval",
        metadata={"project": "auto-recruiter"}
    )
    
    print("Experiment completed. Check the LangSmith UI for detailed results.")
