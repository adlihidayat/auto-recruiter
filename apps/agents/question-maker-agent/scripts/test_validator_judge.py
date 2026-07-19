import sys
import os
import json
import importlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from langchain_core.messages import SystemMessage, HumanMessage
from apps.agents.shared.clients import gemini_flash_lite

state_module = importlib.import_module("question-maker-agent.state")
prompts_module = importlib.import_module("question-maker-agent.prompts.validator_prompt")

CriticFeedback = state_module.CriticFeedback
VALIDATOR_SYSTEM_INSTRUCTION = getattr(prompts_module, "JUDGE_SYSTEM_INSTRUCTION", getattr(prompts_module, "VALIDATOR_SYSTEM_INSTRUCTION", ""))

scenarios = [
    # 1 — Baseline: everything correct, should cleanly pass all 5 checks.
    {
        "name": "Clean Pass - Python asyncio",
        "goal_id": "g_01",
        "topic": "Python concurrency",
        "goal": "Evaluate candidate's understanding of event loops and coroutines in Python.",
        "time_budget_minutes": 10,
        "grounding_theory": (
            "The asyncio event loop manages execution of asynchronous tasks. "
            "'await' yields control back to the event loop until the awaited "
            "I/O task is complete. Coroutines are the building blocks of asyncio."
        ),
        "question": {
            "suggested_opening": (
                "We have a Python service that needs to fetch data from three "
                "external APIs concurrently. How would you use asyncio to handle "
                "these requests, and what happens under the hood when your code "
                "hits an 'await'?"
            ),
            "passing_criteria": [
                "Explains that 'await' pauses the coroutine and yields control back to the event loop",
                "Identifies the event loop as the scheduler that manages task execution",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims 'await' runs the code in a separate OS thread automatically", "severity": "critical"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Says 'await' blocks the whole program without clarifying what it blocks",
                    "follow_up_prompt": "When you say it blocks — does it block the whole process, or just that one coroutine?",
                }
            ],
        },
        "expected": {
            "verdict": "pass",
            "checks": {
                "goal_alignment": {"pass": True},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": True},
                "signal_classification": {"pass": True},
                "pushback_actionability": {"pass": True},
            },
        },
    },
 
    # 2 — Isolated failure: goal_alignment. Question is well-formed but
    # evaluates a completely different concept than the stated goal.
    {
        "name": "Goal Misalignment - SQL Injection goal, normalization question",
        "goal_id": "g_02",
        "topic": "Database security",
        "goal": "Evaluate candidate's understanding of SQL injection prevention techniques.",
        "time_budget_minutes": 8,
        "grounding_theory": (
            "Parameterized queries (prepared statements) prevent SQL injection "
            "by separating query structure from user-supplied data, so input is "
            "never interpreted as SQL syntax."
        ),
        "question": {
            "suggested_opening": (
                "You're designing a schema for an e-commerce orders table. "
                "How would you decide whether to normalize customer address data "
                "into a separate table versus storing it inline?"
            ),
            "passing_criteria": [
                "Explains third normal form and when denormalization is acceptable for performance",
                "Discusses tradeoffs between join cost and data duplication",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims normalization has no performance implications at all", "severity": "moderate"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Mentions denormalization for performance without naming a specific tradeoff",
                    "follow_up_prompt": "What's the specific cost you're trying to avoid by denormalizing here?",
                }
            ],
        },
        "expected": {
            "verdict": "fail",
            "checks": {
                "goal_alignment": {"pass": False},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": True},
                "signal_classification": {"pass": True},
                "pushback_actionability": {"pass": True},
            },
        },
    },
 
    # 3 — Isolated failure: passing_criteria_valid. Criteria are not
    # observable/checkable from a transcript.
    {
        "name": "Vague Passing Criteria - CAP theorem",
        "goal_id": "g_03",
        "topic": "Distributed systems",
        "goal": "Evaluate candidate's understanding of CAP theorem tradeoffs.",
        "time_budget_minutes": 12,
        "grounding_theory": (
            "The CAP theorem states a distributed system cannot simultaneously "
            "guarantee Consistency, Availability, and Partition tolerance during "
            "a network partition — it must sacrifice one of Consistency or "
            "Availability."
        ),
        "question": {
            "suggested_opening": (
                "We're building a globally distributed key-value store and a "
                "network partition splits our datacenters. Walk me through how "
                "you'd think about consistency versus availability here."
            ),
            "passing_criteria": [
                "Understands CAP theorem well",
                "Has a good grasp of distributed systems tradeoffs",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims a distributed system can guarantee all three of C, A, and P simultaneously", "severity": "critical"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Says the system should 'just handle it gracefully' without picking C or A",
                    "follow_up_prompt": "If you had to pick one to sacrifice during the partition, which would it be and why?",
                }
            ],
        },
        "expected": {
            "verdict": "fail",
            "checks": {
                "goal_alignment": {"pass": True},
                "passing_criteria_valid": {"pass": False},
                "grounding_fidelity": {"pass": True},
                "signal_classification": {"pass": True},
                "pushback_actionability": {"pass": True},
            },
        },
    },
 
    # 4 — Isolated failure: grounding_fidelity. A specific fabricated detail
    # not present in (and not implied by) the grounding theory.
    {
        "name": "Hallucinated Fact - Kubernetes scheduler",
        "goal_id": "g_04",
        "topic": "Kubernetes",
        "goal": "Evaluate candidate's understanding of Kubernetes pod scheduling.",
        "time_budget_minutes": 15,
        "grounding_theory": (
            "The kube-scheduler assigns pods to nodes based on resource "
            "requests, affinity/anti-affinity rules, and taints/tolerations."
        ),
        "question": {
            "suggested_opening": (
                "Some of your pods are stuck in Pending state even though nodes "
                "have free capacity. How would you debug why the scheduler "
                "isn't placing them?"
            ),
            "passing_criteria": [
                "Checks resource requests against available node capacity",
                "States that the scheduler uses the 'Bin-Packing v3 algorithm introduced in Kubernetes 1.29' to make placement decisions",
                "Checks for taints on nodes without matching tolerations on the pod",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims pods are scheduled purely at random with no resource awareness", "severity": "critical"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Mentions taints/tolerations but doesn't explain how they interact with scheduling",
                    "follow_up_prompt": "How exactly does a toleration change whether a pod can land on a tainted node?",
                }
            ],
        },
        "expected": {
            "verdict": "fail",
            "checks": {
                "goal_alignment": {"pass": True},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": False},
                "signal_classification": {"pass": True},
                "pushback_actionability": {"pass": True},
            },
        },
    },
 
    # 5 — Isolated failure: signal_classification. A hard misconception is
    # mislabeled as a pushback_trigger instead of wrong_answer_signal.
    {
        "name": "Signal Misclassification - Python pass-by-reference",
        "goal_id": "g_05",
        "topic": "Python semantics",
        "goal": "Evaluate candidate's understanding of how arguments are passed in Python.",
        "time_budget_minutes": 10,
        "grounding_theory": (
            "In Python, arguments are passed by object reference. Mutating a "
            "mutable object inside a function affects the caller's object; "
            "reassigning a parameter inside the function does not affect the "
            "caller's binding."
        ),
        "question": {
            "suggested_opening": (
                "You pass a list into a function and the function appends an "
                "item to it. After the function returns, is the caller's list "
                "changed? Why or why not?"
            ),
            "passing_criteria": [
                "States that mutating the object in place affects the caller because both names point to the same object",
                "Distinguishes mutation from reassignment inside the function",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims lists are always copied when passed to a function", "severity": "moderate"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Claims Python passes everything by value, copying the entire object every time it's passed to a function",
                    "follow_up_prompt": "So if that's true, why would appending inside the function still show up outside it?",
                }
            ],
        },
        "expected": {
            "verdict": "fail",
            "checks": {
                "goal_alignment": {"pass": True},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": True},
                "signal_classification": {"pass": False},
                "pushback_actionability": {"pass": True},
            },
        },
    },
 
    # 6 — Isolated failure: pushback_actionability. follow_up_prompt is a
    # category label, not a real askable question.
    {
        "name": "Non-Actionable Pushback - React state vs props",
        "goal_id": "g_06",
        "topic": "React",
        "goal": "Evaluate candidate's understanding of when to lift state up versus keep it local.",
        "time_budget_minutes": 10,
        "grounding_theory": (
            "In React, state should be lifted to the closest common ancestor "
            "of components that need to share it. Props pass data down; state "
            "changes should generally flow through the component that owns it."
        ),
        "question": {
            "suggested_opening": (
                "Two sibling components both need to reflect the same filter "
                "selection. Where would you put that state, and why?"
            ),
            "passing_criteria": [
                "States that the state should be lifted to the closest common parent",
                "Explains that the parent passes the value and an updater down as props",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims sibling components can share state directly without a common parent or external store", "severity": "critical"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Mentions 'lifting state up' vaguely without describing the mechanism",
                    "follow_up_prompt": "Probe deeper on state management.",
                }
            ],
        },
        "expected": {
            "verdict": "fail",
            "checks": {
                "goal_alignment": {"pass": True},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": True},
                "signal_classification": {"pass": True},
                "pushback_actionability": {"pass": False},
            },
        },
    },
 
    # 7 — Combined failure: goal_alignment AND grounding_fidelity both fail
    # at once. Tests whether the judge evaluates all 5 checks independently
    # rather than stopping at the first problem found.
    {
        "name": "Combined Failure - TCP goal, DNS question, fabricated RFC",
        "goal_id": "g_07",
        "topic": "Networking",
        "goal": "Evaluate candidate's understanding of the TCP three-way handshake.",
        "time_budget_minutes": 6,
        "grounding_theory": (
            "The TCP three-way handshake consists of SYN, SYN-ACK, and ACK "
            "packets exchanged to establish a reliable connection between "
            "client and server before data transfer begins."
        ),
        "question": {
            "suggested_opening": (
                "A user types a URL into their browser. Walk me through how the "
                "browser resolves that domain name to an IP address."
            ),
            "passing_criteria": [
                "Explains the recursive resolver querying root, TLD, and authoritative nameservers",
                "Cites RFC 9293 section 4.2.1 as specifying a 3-second retry timer for handshake retransmission",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims DNS resolution requires a TCP connection for every query", "severity": "moderate"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Mentions caching without specifying at which layer (browser, OS, resolver) it happens",
                    "follow_up_prompt": "Which of those caches would actually be checked first?",
                }
            ],
        },
        "expected": {
            "verdict": "fail",
            "checks": {
                "goal_alignment": {"pass": False},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": False},
                "signal_classification": {"pass": True},
                "pushback_actionability": {"pass": True},
            },
        },
    },
 
    # 8 — No grounding_theory provided, but the question fabricates a
    # suspiciously specific statistic anyway. Tests the "no theory" branch
    # of grounding_fidelity actually catches invented specifics.
    {
        "name": "No Grounding + Real Hallucination - L2 regularization",
        "goal_id": "g_08",
        "topic": "Machine learning",
        "goal": "Evaluate candidate's understanding of L2 regularization.",
        "time_budget_minutes": 8,
        "grounding_theory": None,
        "question": {
            "suggested_opening": (
                "Your model performs great on training data but poorly on the "
                "validation set. How would L2 regularization help, and how does "
                "it actually work?"
            ),
            "passing_criteria": [
                "States that L2 regularization penalizes large weights, discouraging overfitting",
                "States that L2 regularization improved accuracy by exactly 4.7% on ResNet-50 ImageNet in the original paper",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims regularization only affects training speed, not generalization", "severity": "moderate"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Says regularization 'prevents overfitting' without explaining the mechanism",
                    "follow_up_prompt": "What is L2 regularization actually doing to the loss function that produces that effect?",
                }
            ],
        },
        "expected": {
            "verdict": "fail",
            "checks": {
                "goal_alignment": {"pass": True},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": False},
                "signal_classification": {"pass": True},
                "pushback_actionability": {"pass": True},
            },
        },
    },
 
    # 9 — No grounding_theory, but everything stated is uncontested common
    # knowledge with no invented specifics. False-positive trap: does the
    # judge wrongly fail this just because grounding_theory is absent?
    {
        "name": "No Grounding + Legitimate Common Knowledge - Code review",
        "goal_id": "g_09",
        "topic": "Software engineering practices",
        "goal": "Evaluate candidate's understanding of why code review improves software quality.",
        "time_budget_minutes": 5,
        "grounding_theory": None,
        "question": {
            "suggested_opening": (
                "Your team is deciding whether to require code review on every "
                "pull request, even small ones. How would you make that case?"
            ),
            "passing_criteria": [
                "States that code review helps catch bugs before they reach production",
                "Mentions knowledge sharing across the team as a benefit",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims code review has no value for small changes and should always be skipped", "severity": "moderate"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Says review 'improves quality' without naming a specific mechanism",
                    "follow_up_prompt": "What specifically about having a second person look at the code improves quality?",
                }
            ],
        },
        "expected": {
            "verdict": "pass",
            "checks": {
                "goal_alignment": {"pass": True},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": True},
                "signal_classification": {"pass": True},
                "pushback_actionability": {"pass": True},
            },
        },
    },
 
    # 10 — Perfect on all 5 defined checks, but the scenario complexity is
    # wildly mismatched with the 2-minute time budget. Time-budget fit is
    # NOT one of the judge's 5 checks. Tests whether a weak model stays
    # disciplined to its actual rubric instead of inventing a 6th reason
    # to fail something that "feels off."
    {
        "name": "Out-of-Scope Trap - Raft consensus in 2 minutes",
        "goal_id": "g_10",
        "topic": "Distributed consensus",
        "goal": "Evaluate deep understanding of Raft leader election and log replication under multi-datacenter failure scenarios.",
        "time_budget_minutes": 2,
        "grounding_theory": (
            "In Raft, a leader is elected via randomized election timeouts and "
            "majority vote. The leader replicates log entries to followers and "
            "commits an entry once a majority of nodes acknowledge it. A term "
            "number increases with each new election."
        ),
        "question": {
            "suggested_opening": (
                "You have a 5-node Raft cluster split across two datacenters "
                "(3 nodes in DC-A, 2 in DC-B). A network partition isolates "
                "DC-B, and simultaneously the current leader in DC-A crashes. "
                "Walk me through exactly what happens to leader election and "
                "log replication in this scenario, step by step."
            ),
            "passing_criteria": [
                "States that DC-A can still elect a new leader since it holds a majority (3 of 5 nodes)",
                "States that DC-B cannot elect a leader because it lacks a majority",
                "Explains that once the partition heals, DC-B's stale entries are overwritten by the new leader's log",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims both partitions can independently elect leaders and both remain valid", "severity": "critical"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Says DC-B 'waits' without explaining why it specifically can't reach a majority",
                    "follow_up_prompt": "Why exactly can't DC-B's 2 nodes elect a leader on their own?",
                }
            ],
        },
        "expected": {
            "verdict": "pass",
            "checks": {
                "goal_alignment": {"pass": True},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": True},
                "signal_classification": {"pass": True},
                "pushback_actionability": {"pass": True},
            },
        },
    },
 
    # 11 — Clean pass, fresh domain: security/cryptography.
    {
        "name": "Clean Pass - Password Hashing and Salting",
        "goal_id": "g_11",
        "topic": "Application security",
        "goal": "Evaluate candidate's understanding of why passwords must be hashed and salted before storage.",
        "time_budget_minutes": 10,
        "grounding_theory": (
            "Passwords should be hashed with a slow, purpose-built algorithm "
            "such as bcrypt, scrypt, or Argon2 rather than a fast general-"
            "purpose hash like MD5 or SHA-256. A unique salt per password "
            "prevents attackers from using precomputed rainbow tables and "
            "ensures identical passwords produce different stored hashes."
        ),
        "question": {
            "suggested_opening": (
                "You're reviewing a colleague's PR and notice they're storing "
                "user passwords as SHA-256(password) with no salt. What's wrong "
                "with this, and what would you recommend instead?"
            ),
            "passing_criteria": [
                "States that a unique per-user salt prevents rainbow table attacks and identical passwords from producing identical hashes",
                "Recommends a slow, purpose-built algorithm like bcrypt/scrypt/Argon2 instead of a fast general-purpose hash",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims hashing and encryption are the same thing and passwords should be 'decrypted' to verify login", "severity": "critical"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Recommends 'a strong hash function' without naming one or explaining why speed matters",
                    "follow_up_prompt": "Why would a fast hash function like SHA-256 actually be a liability here, compared to something like bcrypt?",
                }
            ],
        },
        "expected": {
            "verdict": "pass",
            "checks": {
                "goal_alignment": {"pass": True},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": True},
                "signal_classification": {"pass": True},
                "pushback_actionability": {"pass": True},
            },
        },
    },
 
    # 12 — Isolated failure: grounding_fidelity, via a fabricated tool
    # version/feature detail not present in the grounding theory.
    {
        "name": "Hallucinated Fact - Git rebase fabricated version detail",
        "goal_id": "g_12",
        "topic": "Version control",
        "goal": "Evaluate candidate's understanding of git rebase versus merge.",
        "time_budget_minutes": 10,
        "grounding_theory": (
            "git merge creates a new commit joining two histories, preserving "
            "both branches' commit history. git rebase replays commits from "
            "one branch onto another, producing a linear history but rewriting "
            "commit hashes."
        ),
        "question": {
            "suggested_opening": (
                "Your team is arguing about whether to use rebase or merge when "
                "integrating feature branches into main. How would you explain "
                "the tradeoff to them?"
            ),
            "passing_criteria": [
                "States that rebase rewrites commit history producing a linear log, while merge preserves the original branch structure",
                "States that git rebase --autosquash was introduced in Git 3.0 to automatically combine fixup commits",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims merge and rebase produce identical commit histories with no practical difference", "severity": "moderate"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Says rebase is 'cleaner' without explaining what specifically becomes cleaner",
                    "follow_up_prompt": "Cleaner in what specific way — what does the commit graph look like differently?",
                }
            ],
        },
        "expected": {
            "verdict": "fail",
            "checks": {
                "goal_alignment": {"pass": True},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": False},
                "signal_classification": {"pass": True},
                "pushback_actionability": {"pass": True},
            },
        },
    },
 
    # 13 — Isolated failure: signal_classification, fresh domain: web
    # accessibility. A hard misconception mislabeled as pushback.
    {
        "name": "Signal Misclassification - Semantic HTML and screen readers",
        "goal_id": "g_13",
        "topic": "Web accessibility",
        "goal": "Evaluate candidate's understanding of why semantic HTML matters for accessibility.",
        "time_budget_minutes": 8,
        "grounding_theory": (
            "Screen readers rely on semantic HTML elements and ARIA roles to "
            "convey structure and meaning. A generic <div> with a click "
            "handler is not announced as a button and is not keyboard-"
            "focusable unless explicitly given a role and tabindex."
        ),
        "question": {
            "suggested_opening": (
                "A designer wants a custom-styled button built as a <div> with "
                "an onClick handler instead of a <button> element. What's your "
                "concern from an accessibility standpoint?"
            ),
            "passing_criteria": [
                "States that a plain <div> is not announced as interactive by screen readers without ARIA role and tabindex",
                "States that a native <button> gets keyboard focus and activation for free",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims CSS styling alone determines what screen readers announce", "severity": "moderate"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Claims any screen reader can correctly interpret a div-based control regardless of ARIA roles, since it can 'see' the click handler",
                    "follow_up_prompt": "How would a screen reader know a div is clickable at all if there's no ARIA role or semantic element telling it so?",
                }
            ],
        },
        "expected": {
            "verdict": "fail",
            "checks": {
                "goal_alignment": {"pass": True},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": True},
                "signal_classification": {"pass": False},
                "pushback_actionability": {"pass": True},
            },
        },
    },
 
    # 14 — Isolated failure: pushback_actionability, fresh domain: data
    # structures.
    {
        "name": "Non-Actionable Pushback - Hash table vs balanced tree",
        "goal_id": "g_14",
        "topic": "Data structures",
        "goal": "Evaluate candidate's understanding of when to use a hash table versus a balanced tree.",
        "time_budget_minutes": 10,
        "grounding_theory": (
            "Hash tables offer average O(1) lookup/insert but no ordering "
            "guarantee and worst-case O(n) under heavy collisions. Balanced "
            "trees (e.g. red-black trees) offer O(log n) operations but "
            "maintain sorted order, enabling range queries and ordered "
            "traversal."
        ),
        "question": {
            "suggested_opening": (
                "You need a data structure to store user sessions by ID for "
                "fast lookup, and separately one to store a leaderboard that "
                "needs range queries like 'top 10 scores.' Which would you use "
                "for each, and why?"
            ),
            "passing_criteria": [
                "Chooses a hash table for session lookup, citing average O(1) access with no ordering need",
                "Chooses a balanced tree for the leaderboard, citing the need for ordered traversal and range queries",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims hash tables maintain insertion or sorted order by default", "severity": "moderate"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Picks a hash table for the leaderboard without addressing how range queries would work",
                    "follow_up_prompt": "Ask for more detail.",
                }
            ],
        },
        "expected": {
            "verdict": "fail",
            "checks": {
                "goal_alignment": {"pass": True},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": True},
                "signal_classification": {"pass": True},
                "pushback_actionability": {"pass": False},
            },
        },
    },
 
    # 15 — Isolated failure: passing_criteria_valid, fresh domain:
    # statistics.
    {
        "name": "Vague Passing Criteria - p-values",
        "goal_id": "g_15",
        "topic": "Statistics",
        "goal": "Evaluate candidate's understanding of p-values in hypothesis testing.",
        "time_budget_minutes": 10,
        "grounding_theory": (
            "A p-value is the probability of observing a result at least as "
            "extreme as the one measured, assuming the null hypothesis is "
            "true. It is not the probability that the null hypothesis is "
            "true, and a small p-value does not by itself indicate a large "
            "or practically significant effect."
        ),
        "question": {
            "suggested_opening": (
                "An A/B test comes back with p = 0.03 for a new feature. A "
                "product manager says 'great, there's a 97% chance this "
                "feature works.' How would you respond?"
            ),
            "passing_criteria": [
                "Understands statistics well",
                "Knows about p-values",
            ],
            "wrong_answer_signals": [
                {"signal": "Agrees that p = 0.03 means there's a 97% chance the effect is real", "severity": "critical"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Correctly says the PM's interpretation is wrong but doesn't state what the p-value actually represents",
                    "follow_up_prompt": "If it's not 'the chance the effect is real,' what does the p-value actually tell us?",
                }
            ],
        },
        "expected": {
            "verdict": "fail",
            "checks": {
                "goal_alignment": {"pass": True},
                "passing_criteria_valid": {"pass": False},
                "grounding_fidelity": {"pass": True},
                "signal_classification": {"pass": True},
                "pushback_actionability": {"pass": True},
            },
        },
    },
 
    # 16 — Isolated failure: goal_alignment, fresh domain: SRE / incident
    # response.
    {
        "name": "Goal Misalignment - Postmortem goal, on-call scheduling question",
        "goal_id": "g_16",
        "topic": "Site reliability engineering",
        "goal": "Evaluate candidate's approach to writing blameless postmortems after an incident.",
        "time_budget_minutes": 12,
        "grounding_theory": (
            "A blameless postmortem focuses on identifying systemic and "
            "process failures rather than assigning fault to individuals. It "
            "documents a timeline, root cause, impact, and concrete follow-up "
            "action items with owners."
        ),
        "question": {
            "suggested_opening": (
                "Your team is growing and the on-call rotation is getting "
                "unevenly distributed. How would you redesign the on-call "
                "schedule to be fairer across time zones?"
            ),
            "passing_criteria": [
                "Proposes a rotation scheme that accounts for time zone distribution",
                "Discusses tradeoffs between rotation length and burnout risk",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims on-call schedules don't need to account for time zones at all", "severity": "moderate"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Proposes a rotation without addressing handoff communication between shifts",
                    "follow_up_prompt": "How would engineers actually hand off context to the next on-call person?",
                }
            ],
        },
        "expected": {
            "verdict": "fail",
            "checks": {
                "goal_alignment": {"pass": False},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": True},
                "signal_classification": {"pass": True},
                "pushback_actionability": {"pass": True},
            },
        },
    },
 
    # 17 — Combined failure, a different pair than scenario 7:
    # signal_classification AND pushback_actionability fail together.
    {
        "name": "Combined Failure - iOS ARC retain cycles",
        "goal_id": "g_17",
        "topic": "Mobile development (iOS)",
        "goal": "Evaluate candidate's understanding of retain cycles under Automatic Reference Counting (ARC).",
        "time_budget_minutes": 10,
        "grounding_theory": (
            "ARC automatically manages memory via reference counting. A "
            "retain cycle occurs when two objects hold strong references to "
            "each other, so neither's count ever reaches zero and neither is "
            "deallocated. Using a 'weak' or 'unowned' reference on one side "
            "breaks the cycle."
        ),
        "question": {
            "suggested_opening": (
                "A view controller holds a closure that captures 'self' "
                "strongly, and that closure is stored as a property on the "
                "view controller. What happens to memory here, and how would "
                "you fix it?"
            ),
            "passing_criteria": [
                "Identifies this as a retain cycle: the closure retains self, and self retains the closure",
                "Proposes using [weak self] or [unowned self] in the closure's capture list to break the cycle",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims ARC automatically detects and breaks all retain cycles at runtime with no developer action needed", "severity": "moderate"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Claims ARC will eventually garbage-collect the cycle the same way Java or Python would, given enough time",
                    "follow_up_prompt": "Does ARC ever run a cycle-detecting collector the way a tracing garbage collector does?",
                },
                {
                    "trigger_condition": "Suggests using 'weak self' without explaining why weak versus unowned matters here",
                    "follow_up_prompt": "Consider the difference.",
                },
            ],
        },
        "expected": {
            "verdict": "fail",
            "checks": {
                "goal_alignment": {"pass": True},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": True},
                "signal_classification": {"pass": False},
                "pushback_actionability": {"pass": False},
            },
        },
    },
 
    # 18 — No grounding_theory, non-technical/behavioral domain, all
    # content is uncontested common practice with nothing fabricated.
    # Tests whether grounding_fidelity behaves sanely for soft-skill goals
    # where "facts" are best-practices, not verifiable claims.
    {
        "name": "No Grounding + Legitimate Content - Conflict with a teammate",
        "goal_id": "g_18",
        "topic": "Behavioral / interpersonal skills",
        "goal": "Evaluate candidate's ability to handle conflict constructively with a teammate.",
        "time_budget_minutes": 8,
        "grounding_theory": None,
        "question": {
            "suggested_opening": (
                "Tell me about a time you disagreed with a teammate about a "
                "technical approach. How did you handle it?"
            ),
            "passing_criteria": [
                "Describes seeking to understand the teammate's reasoning before pushing their own view",
                "Describes reaching a resolution through discussion of tradeoffs rather than escalation or avoidance",
            ],
            "wrong_answer_signals": [
                {"signal": "Describes simply overriding the teammate's decision without any discussion", "severity": "moderate"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Says they 'talked it out' without describing what was actually said or decided",
                    "follow_up_prompt": "What did that conversation actually look like — what did you say, and what did they say back?",
                }
            ],
        },
        "expected": {
            "verdict": "pass",
            "checks": {
                "goal_alignment": {"pass": True},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": True},
                "signal_classification": {"pass": True},
                "pushback_actionability": {"pass": True},
            },
        },
    },
 
    # 19 — No grounding_theory, legal/compliance domain, with a fabricated
    # specific legal citation. Tests catching a hallucinated *authority*
    # (a regulation citation), not just a hallucinated technical fact.
    {
        "name": "No Grounding + Fabricated Legal Citation - HIPAA",
        "goal_id": "g_19",
        "topic": "Regulatory compliance",
        "goal": "Evaluate candidate's understanding of HIPAA requirements for handling patient data.",
        "time_budget_minutes": 10,
        "grounding_theory": None,
        "question": {
            "suggested_opening": (
                "Your team is building a feature that stores patient lab "
                "results. What HIPAA considerations would shape how you design "
                "data storage and access?"
            ),
            "passing_criteria": [
                "States that access to patient data (PHI) should be limited to those with a legitimate need (minimum necessary standard)",
                "Cites 45 CFR § 164.312(a)(2)(iv) as specifically requiring AES-256 encryption at rest",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims HIPAA only applies to hospitals and not to software vendors handling patient data on their behalf", "severity": "critical"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Mentions 'encrypting the data' without specifying at rest, in transit, or both",
                    "follow_up_prompt": "Encrypted where specifically — at rest, in transit, or both, and does that change your design?",
                }
            ],
        },
        "expected": {
            "verdict": "fail",
            "checks": {
                "goal_alignment": {"pass": True},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": False},
                "signal_classification": {"pass": True},
                "pushback_actionability": {"pass": True},
            },
        },
    },
 
    # 20 — Restraint trap, different flavor than scenario 10: correct
    # category classification throughout, but one severity label is
    # debatable (arguably should be "critical" not "moderate"). The
    # rubric (CHECK 4) only requires correct wrong-vs-pushback category,
    # not exact severity calibration — tests whether the judge invents a
    # 6th criterion by policing severity choice.
    {
        "name": "Out-of-Scope Trap - Debatable severity, correct classification",
        "goal_id": "g_20",
        "topic": "Load balancing",
        "goal": "Evaluate candidate's understanding of round-robin versus least-connections load balancing.",
        "time_budget_minutes": 10,
        "grounding_theory": (
            "Round-robin distributes requests evenly in sequence regardless "
            "of backend load. Least-connections routes each new request to "
            "the backend with the fewest active connections, which handles "
            "uneven request durations better than round-robin."
        ),
        "question": {
            "suggested_opening": (
                "Some of your backend requests take 10ms and others take 2 "
                "seconds, and they're mixed randomly. Would round-robin or "
                "least-connections serve you better here, and why?"
            ),
            "passing_criteria": [
                "Chooses least-connections and explains that round-robin can overload a backend stuck with several slow requests",
                "Explains that round-robin assumes uniform request cost, which doesn't hold here",
            ],
            "wrong_answer_signals": [
                {"signal": "Claims round-robin and least-connections always produce identical request distribution over time", "severity": "moderate"},
            ],
            "pushback_triggers": [
                {
                    "trigger_condition": "Chooses least-connections correctly but doesn't explain why round-robin specifically fails under uneven request duration",
                    "follow_up_prompt": "Walk me through exactly how round-robin could overload one backend in this scenario.",
                }
            ],
        },
        "expected": {
            "verdict": "pass",
            "checks": {
                "goal_alignment": {"pass": True},
                "passing_criteria_valid": {"pass": True},
                "grounding_fidelity": {"pass": True},
                "signal_classification": {"pass": True},
                "pushback_actionability": {"pass": True},
            },
        },
    },
]

def test_validator_judge():
    structured_judge = gemini_flash_lite.with_structured_output(CriticFeedback)
    sys_msg = SystemMessage(content=VALIDATOR_SYSTEM_INSTRUCTION)
    
    print("=== RUNNING VALIDATOR JUDGE EXPERIMENTS (LAYER 2 ONLY) ===\n")
    
    for idx, scenario in enumerate(scenarios):
        print(f"Scenario {idx + 1}: {scenario['name']}")
        
        # Build prompt
        human_content = f"Goal ID: {scenario['goal_id']}\n"
        human_content += f"Goal: {scenario['goal']}\n\n"
        human_content += f"--- Grounding Theory ---\n{scenario.get('grounding_theory', 'None')}\n\n"
        human_content += "--- Generated Question ---\n"
        human_content += f"Suggested Opening: {scenario['question']['suggested_opening']}\n"
        human_content += f"Passing Criteria: {scenario['question']['passing_criteria']}\n"
        human_content += f"Wrong Answer Signals: {scenario['question']['wrong_answer_signals']}\n"
        human_content += f"Pushback Triggers: {scenario['question']['pushback_triggers']}\n"
        
        human_msg = HumanMessage(content=human_content)
        
        try:
            result: CriticFeedback = structured_judge.invoke([sys_msg, human_msg])
            checks = result.checks
            
            # Print Expected vs Actual Side-by-Side
            expected_verdict = scenario['expected']['verdict']
            expected_checks = scenario['expected']['checks']
            
            print(f"[Verdict] Actual: {result.verdict} | Expected: {expected_verdict}")
            print(f"[Goal Align] Actual: {checks.goal_alignment.pass_} | Expected: {expected_checks['goal_alignment']['pass']}")
            if not checks.goal_alignment.pass_:
                print(f"    -> {checks.goal_alignment.reasoning}")
                
            print(f"[Criteria] Actual: {checks.passing_criteria_valid.pass_} | Expected: {expected_checks['passing_criteria_valid']['pass']}")
            if not checks.passing_criteria_valid.pass_:
                print(f"    -> {checks.passing_criteria_valid.reasoning}")
                
            print(f"[Grounding] Actual: {checks.grounding_fidelity.pass_} | Expected: {expected_checks['grounding_fidelity']['pass']}")
            if not checks.grounding_fidelity.pass_:
                print(f"    -> {checks.grounding_fidelity.unsupported_claims}")
                
            print(f"[Signals] Actual: {checks.signal_classification.pass_} | Expected: {expected_checks['signal_classification']['pass']}")
            if not checks.signal_classification.pass_:
                print(f"    -> {checks.signal_classification.issues}")
                
            print(f"[Pushbacks] Actual: {checks.pushback_actionability.pass_} | Expected: {expected_checks['pushback_actionability']['pass']}")
            if not checks.pushback_actionability.pass_:
                print(f"    -> {checks.pushback_actionability.issues}")
            
        except Exception as e:
            print(f"\n[ACTUAL ERROR]: {e}")
            
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_validator_judge()
