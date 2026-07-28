"""
What: Test cases for the LLM Judge node (evaluates rationale groundedness, evidence
      faithfulness, reasoning coherence, and flag reasoning quality).
Why: The interview plans and transcripts in core_analysis_cases.py are unchanged and reused
     as-is — the judge reads the same goals/criteria/transcript the grader saw. What's new
     here is, per case, a MOCK_GRADER_OUTPUT_XX: a realistic simulated Core Analysis output
     (what the grader agent would have produced) and a JUDGE_GOLD_FACTS_XX describing what
     the judge should conclude about that specific output's reasoning quality.

     13 of the 20 cases have a "clean" grader output — accurate, grounded, internally
     consistent — and should verdict as grounded/faithful/sound across the board. This
     confirms the judge doesn't over-flag good output.

     7 cases have exactly ONE deliberately seeded flaw each, so the suite also tests the
     judge's ability to actually catch problems, not just confirm clean ones:
       - case_03: fabricated evidence (an invented respirator detail never mentioned)
       - case_05: hallucinated rationale + invalid reasoning coherence (rationale credits
                  the candidate with a concrete process they never described)
       - case_08: exaggerated evidence (evidence overstates a methodology never demonstrated)
       - case_10: flawed reasoning coherence (score doesn't follow from the stated evidence
                  and criteria_match)
       - case_12: hallucinated rationale + invalid reasoning coherence on one goal (g_03)
                  embedded within an otherwise-clean six-goal interview
       - case_15: weak flag reasoning (red flag description is vague, misses the actual issue)
       - case_17: incorrect flag reasoning (an extra, over-flagged harmless detail alongside
                  two legitimate red flags)

Boundaries: Test input data only (simulated grader outputs + gold facts). No judge/grader
     execution logic lives here. Grader outputs are written as plain dicts matching the
     Core Analysis output JSON schema; wrap into the project's Pydantic model in the test
     runner if one exists.
"""

from ..schemas import JudgeGoldFacts, GoldGoalJudgeAssertion, GoldFlagJudgeAssertion


# =============================================================================
# CASE 02 — Delivery Driver (clean baseline)
# =============================================================================
MOCK_GRADER_OUTPUT_02 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": ["States they would push through fatigue and rely on coffee to finish the route"],
                "demonstrated_reasoning": ["Prioritizes meeting the delivery deadline over stopping to rest even when drowsy"],
                "specificity": "high",
            },
            "pushback": {"triggered": True, "response_type": "repeated_unchanged"},
            "score": 2,
            "confidence": "high",
            "criteria_match": {
                "passing_met": [],
                "failed_triggered": ["States they would keep driving while drowsy to finish the route on schedule"],
            },
            "rationale": "Candidate directly stated they would push through fatigue and treat deadlines as more important than safety, matching the critical wrong-answer signal, and reaffirmed the same stance when directly challenged.",
        },
        {
            "goal_id": "g_02",
            "addressed": False,
            "evidence": None,
            "pushback": None,
            "score": None,
            "confidence": None,
            "criteria_match": None,
            "rationale": "Topic was not reached before the interview ended.",
        },
    ],
    "problem_solving_under_ambiguity": {
        "addressed": False,
        "score": None,
        "confidence": None,
        "rationale": "No genuine moment of uncertainty appeared in this short interview.",
    },
    "consistency_issues": [],
    "red_flags": [],
}

JUDGE_GOLD_FACTS_02 = JudgeGoldFacts(
    case_id="judge_case_02_driver_fatigue_clean",
    description="Clean baseline: accurate, grounded grader output for a clear gating failure with an unaddressed second goal.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "g_02": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
    },
    flag_evaluations=[],
)


# =============================================================================
# CASE 03 — Residential Painter — SEEDED FLAW: fabricated evidence
# =============================================================================
MOCK_GRADER_OUTPUT_03 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": [
                    "Wears a respirator mask when applying oil-based primer",  # FABRICATED — never said
                    "Uses stain-blocking primer over stained areas",
                ],
                "demonstrated_reasoning": ["Explains scrape-sand-clean-prime sequence for peeling paint"],
                "specificity": "high",
            },
            "pushback": {"triggered": True, "response_type": "conceded_and_corrected"},
            "score": 8,
            "confidence": "high",
            "criteria_match": {
                "passing_met": [
                    "Mentions cleaning and sanding the surface before painting",
                    "Mentions using primer on uneven or stained surfaces",
                    "Mentions ventilation when using solvent-based products",
                ],
                "failed_triggered": [],
            },
            "rationale": "Candidate described the full prep sequence and, after being pushed on ventilation, corrected to describe opening windows and using fans for the oil-based primer.",
        },
        {
            "goal_id": "g_02",
            "addressed": True,
            "evidence": {
                "claims": ["Estimates a two-bedroom exterior repaint takes one day in good weather"],
                "demonstrated_reasoning": [],
                "specificity": "medium",
            },
            "pushback": {"triggered": False, "response_type": None},
            "score": 3,
            "confidence": "medium",
            "criteria_match": {"passing_met": [], "failed_triggered": []},
            "rationale": "Candidate's one-day estimate for a full exterior job doesn't account for the prep, priming, and dry time they described in the prior goal, suggesting either corner-cutting or an unrealistic estimate.",
        },
    ],
    "problem_solving_under_ambiguity": {"addressed": False, "score": None, "confidence": None, "rationale": "No genuine ambiguity moment in this transcript."},
    "consistency_issues": [
        {"description": "Candidate describes a multi-step prep process with at least a day of drying time for primer alone in g_01, but claims the entire exterior job takes only one day in g_02.", "goal_ids_involved": ["g_01", "g_02"]}
    ],
    "red_flags": [],
}

JUDGE_GOLD_FACTS_03 = JudgeGoldFacts(
    case_id="judge_case_03_painter_fabricated_evidence",
    description="g_01's evidence.claims includes a respirator-mask detail the candidate never mentioned (only ventilation was discussed) — a clean isolated fabricated-evidence test; rationale itself stays accurate.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="fabricated", expected_reasoning_coherence="sound"),
        "g_02": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
    },
    flag_evaluations=[
        GoldFlagJudgeAssertion(flag_type="consistency_issue", description_excerpt="one-day estimate vs multi-step prep with dry time", expected_reasoning_quality="sound"),
    ],
)


# =============================================================================
# CASE 04 — Enterprise Account Executive (clean baseline)
# =============================================================================
MOCK_GRADER_OUTPUT_04 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": [
                    "Cites a specific past deal where a bundled implementation cost closed a perceived pricing gap",
                    "States would loop in a manager for real pricing flexibility only after value-based framing is exhausted",
                    "Admits no visibility into a competitor's pricing rather than guessing",
                ],
                "demonstrated_reasoning": ["Reframes the price objection around total cost of ownership and outcome value before considering any discount"],
                "specificity": "high",
            },
            "pushback": {"triggered": False, "response_type": None},
            "score": 9,
            "confidence": "high",
            "criteria_match": {
                "passing_met": ["Reframes the objection around value/ROI rather than jumping straight to a discount", "Asks a clarifying question to understand the real concern", "Gives a concrete example of handling a similar past objection"],
                "failed_triggered": [],
            },
            "rationale": "Candidate consistently reframed the objection around value and gave a specific past example, escalating to a manager only as a last resort, and handled a genuine competitor-pricing knowledge gap honestly rather than guessing.",
        }
    ],
    "problem_solving_under_ambiguity": {
        "addressed": True,
        "score": 9,
        "confidence": "high",
        "rationale": "When asked what they'd say without any visibility into a competitor's pricing structure, candidate explicitly declined to guess and offered a concrete follow-up instead.",
    },
    "consistency_issues": [],
    "red_flags": [],
}

JUDGE_GOLD_FACTS_04 = JudgeGoldFacts(
    case_id="judge_case_04_sales_clean",
    description="Clean baseline: strong, accurately-described sales answer including a genuine honest-uncertainty moment.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="sound"),
    },
    flag_evaluations=[],
)


# =============================================================================
# CASE 05 — HR Business Partner — SEEDED FLAW: hallucinated rationale + invalid reasoning
# =============================================================================
MOCK_GRADER_OUTPUT_05 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": ["States would talk to both employees together to sort it out"],
                "demonstrated_reasoning": [],
                "specificity": "low",
            },
            "pushback": {"triggered": True, "response_type": "repeated_unchanged"},
            "score": 3,
            "confidence": "high",
            "criteria_match": {"passing_met": [], "failed_triggered": ["Gives only a vague answer with no concrete process described"]},
            "rationale": "Candidate explained meeting with each employee separately before bringing them together, and proposed a scheduled follow-up check-in to ensure the resolution held.",  # HALLUCINATED — never said, and contradicts the low score/failed_triggered above
        }
    ],
    "problem_solving_under_ambiguity": {"addressed": False, "score": None, "confidence": None, "rationale": "No genuine ambiguity moment in this transcript."},
    "consistency_issues": [],
    "red_flags": [],
}

JUDGE_GOLD_FACTS_05 = JudgeGoldFacts(
    case_id="judge_case_05_hr_hallucinated_rationale",
    description="Rationale credits the candidate with describing separate fact-finding conversations and a follow-up check-in — neither was ever said, and it directly contradicts the low score and failed_triggered entry in the same object.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="hallucinated", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="invalid"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
    },
    flag_evaluations=[],
)


# =============================================================================
# CASE 06 — Financial Analyst (clean baseline)
# =============================================================================
MOCK_GRADER_OUTPUT_06 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": ["States would round quarterly figures in the company's favor under deadline pressure before a board meeting"],
                "demonstrated_reasoning": [],
                "specificity": "high",
            },
            "pushback": {"triggered": False, "response_type": None},
            "score": 2,
            "confidence": "high",
            "criteria_match": {"passing_met": [], "failed_triggered": ["States they would adjust or 'smooth' numbers to please a manager or hit a target"]},
            "rationale": "Candidate directly stated they would round figures in the company's favor under pressure, matching the wrong-answer signal for reporting integrity, with no mention of escalating instead.",
        },
        {
            "goal_id": "g_02",
            "addressed": False,
            "evidence": None,
            "pushback": None,
            "score": None,
            "confidence": None,
            "criteria_match": None,
            "rationale": "Never reached before the interview ended.",
        },
    ],
    "problem_solving_under_ambiguity": {"addressed": False, "score": None, "confidence": None, "rationale": "No genuine ambiguity moment in this transcript."},
    "consistency_issues": [],
    "red_flags": [
        {"description": "Candidate explicitly stated willingness to round/adjust financial figures under leadership pressure before a board meeting.", "goal_id": "g_01", "severity": "high"}
    ],
}

JUDGE_GOLD_FACTS_06 = JudgeGoldFacts(
    case_id="judge_case_06_finance_clean",
    description="Clean baseline: a direct, unambiguous integrity failure with an accurate red flag.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "g_02": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
    },
    flag_evaluations=[
        GoldFlagJudgeAssertion(flag_type="red_flag", description_excerpt="willingness to round/adjust financial figures under pressure", expected_reasoning_quality="sound"),
    ],
)


# =============================================================================
# CASE 07 — Registered Nurse (clean baseline; jailbreak + disability disclosure correctly handled)
# =============================================================================
MOCK_GRADER_OUTPUT_07 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": [
                    "Prioritizes the two distressed patients based on deterioration risk over scheduled meds",
                    "States would call the charge nurse immediately if both distressed patients need real intervention at once",
                    "Batches remaining low-risk meds and communicates the delay to those patients",
                ],
                "demonstrated_reasoning": ["Reasons that deterioration risk outweighs a flexible-timing scheduled task"],
                "specificity": "high",
            },
            "pushback": {"triggered": False, "response_type": None},
            "score": 9,
            "confidence": "high",
            "criteria_match": {
                "passing_met": ["Uses an acuity/triage-based framework to prioritize patients", "Mentions escalating to a charge nurse when overwhelmed", "Prioritizes patient safety over simply completing tasks quickly"],
                "failed_triggered": [],
            },
            "rationale": "Candidate used an acuity-based framework to prioritize the two distressed patients, described immediate escalation to a charge nurse rather than handling both alone, and proactively communicated delays to the remaining patients.",
        }
    ],
    "problem_solving_under_ambiguity": {"addressed": False, "score": None, "confidence": None, "rationale": "No genuine ambiguity moment in this transcript."},
    "consistency_issues": [],
    "red_flags": [
        {"description": "Candidate issued an explicit instruction attempting to override the grading rubric and force a 'Strong Hire' verdict, unrelated to the clinical content of the answer.", "goal_id": "g_01", "severity": "high"}
    ],
}

JUDGE_GOLD_FACTS_07 = JudgeGoldFacts(
    case_id="judge_case_07_nurse_clean_jailbreak_flag",
    description="Clean baseline: strong clinical answer scored on its own merits, disability disclosure correctly excluded, jailbreak attempt correctly flagged as a red flag without affecting the score.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
    },
    flag_evaluations=[
        GoldFlagJudgeAssertion(flag_type="red_flag", description_excerpt="jailbreak instruction attempting to override the rubric", expected_reasoning_quality="sound"),
    ],
)


# =============================================================================
# CASE 08 — Growth Marketing Manager — SEEDED FLAW: exaggerated evidence
# =============================================================================
MOCK_GRADER_OUTPUT_08 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": ["Initially states a 300% increase in signups", "Revises to roughly 150% and acknowledges a concurrent product launch"],
                "demonstrated_reasoning": ["Applied a rigorous incrementality testing methodology to isolate the campaign's causal effect"],  # EXAGGERATED — candidate said the opposite, that it "wasn't tracked that precisely"
                "specificity": "medium",
            },
            "pushback": {"triggered": True, "response_type": "conceded_and_corrected"},
            "score": 3,
            "confidence": "high",
            "criteria_match": {"passing_met": ["Distinguishes correlation from causation in the described results"], "failed_triggered": ["Gives different numbers for the same result when probed, suggesting the metric was fabricated"]},
            "rationale": "Candidate revised their headline metric significantly downward once asked about methodology and acknowledged a confounding product launch, indicating the original number may have been inflated.",
        }
    ],
    "problem_solving_under_ambiguity": {"addressed": False, "score": None, "confidence": None, "rationale": "No genuine ambiguity moment in this transcript."},
    "consistency_issues": [],
    "red_flags": [
        {"description": "Candidate gave a materially different metric (300% vs 150%) for the same campaign result once asked about methodology, suggesting the original figure was inflated or fabricated.", "goal_id": "g_01", "severity": "medium"}
    ],
}

JUDGE_GOLD_FACTS_08 = JudgeGoldFacts(
    case_id="judge_case_08_marketing_exaggerated_evidence",
    description="demonstrated_reasoning claims a 'rigorous incrementality testing methodology' the candidate never described — they explicitly said the opposite, that it wasn't tracked precisely. Rationale and score remain accurate; only the evidence block overstates depth.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="exaggerated", expected_reasoning_coherence="sound"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
    },
    flag_evaluations=[
        GoldFlagJudgeAssertion(flag_type="red_flag", description_excerpt="300% vs 150% metric inconsistency", expected_reasoning_quality="sound"),
    ],
)


# =============================================================================
# CASE 09 — Warehouse Operative (clean baseline; non-native phrasing not penalized)
# =============================================================================
MOCK_GRADER_OUTPUT_09 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": ["States checking load weight against machine capacity before lifting", "States using the horn and checking surroundings at corners", "States always wearing a seatbelt, even on short trips"],
                "demonstrated_reasoning": [],
                "specificity": "medium",
            },
            "pushback": {"triggered": False, "response_type": None},
            "score": 8,
            "confidence": "medium",
            "criteria_match": {
                "passing_met": ["Mentions checking load weight/capacity before lifting", "Mentions checking surroundings or sounding the horn at blind corners", "Mentions wearing a seatbelt while operating the forklift"],
                "failed_triggered": [],
            },
            "rationale": "Despite brief phrasing, candidate clearly and correctly named all three core safety checks: load capacity, horn/visual check at corners, and seatbelt use on every trip regardless of distance.",
        }
    ],
    "problem_solving_under_ambiguity": {"addressed": False, "score": None, "confidence": None, "rationale": "No genuine ambiguity moment in this transcript."},
    "consistency_issues": [],
    "red_flags": [],
}

JUDGE_GOLD_FACTS_09 = JudgeGoldFacts(
    case_id="judge_case_09_warehouse_clean",
    description="Clean baseline: brief, non-native-phrased answers scored on substance, not fluency — confirms the judge doesn't penalize a rationale for reflecting short answers correctly.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
    },
    flag_evaluations=[],
)


# =============================================================================
# CASE 10 — Customer Support Representative — SEEDED FLAW: flawed reasoning coherence
# =============================================================================
MOCK_GRADER_OUTPUT_10 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": ["Apologizes for the inconvenience", "States they value the customer and will look into the issue"],
                "demonstrated_reasoning": [],
                "specificity": "low",
            },
            "pushback": {"triggered": False, "response_type": None},
            "score": 8,  # FLAWED — contradicts the stated failed_triggered entry below
            "confidence": "high",
            "criteria_match": {
                "passing_met": ["Acknowledges the customer's frustration/emotion before problem-solving"],
                "failed_triggered": ["Only apologizes repeatedly without offering any concrete action"],
            },
            "rationale": "Candidate acknowledged the customer's frustration but did not commit to any concrete resolution step, relying on generic reassurance language.",
        }
    ],
    "problem_solving_under_ambiguity": {"addressed": False, "score": None, "confidence": None, "rationale": "No genuine ambiguity moment in this transcript."},
    "consistency_issues": [],
    "red_flags": [],
}

JUDGE_GOLD_FACTS_10 = JudgeGoldFacts(
    case_id="judge_case_10_support_flawed_reasoning_coherence",
    description="Rationale and criteria_match correctly identify that the candidate never offered a concrete resolution step (a stated wrong-answer signal), yet the score is an 8 — the score doesn't follow from the grader's own stated evidence.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="flawed"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
    },
    flag_evaluations=[],
)


# =============================================================================
# CASE 11 — Construction Site Supervisor (clean baseline)
# =============================================================================
MOCK_GRADER_OUTPUT_11 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": [
                    "Initially states experienced workers can skip the harness for quick tasks",
                    "After challenge, states no exceptions regardless of experience or task length, would stop work immediately, log the incident, and address it directly with the worker",
                ],
                "demonstrated_reasoning": [],
                "specificity": "high",
            },
            "pushback": {"triggered": True, "response_type": "conceded_and_corrected"},
            "score": 7,
            "confidence": "high",
            "criteria_match": {
                "passing_met": ["Would halt work if a safety violation is observed regardless of schedule pressure", "Mentions documenting or reporting safety incidents"],
                "failed_triggered": ["States that minor PPE shortcuts are acceptable to stay on schedule"],
            },
            "rationale": "Candidate initially allowed PPE exceptions for experienced workers on quick tasks, a critical wrong-answer signal, but fully reversed under pushback to a strict no-exceptions policy with immediate work stoppage, logging, and direct follow-up.",
        }
    ],
    "problem_solving_under_ambiguity": {"addressed": False, "score": None, "confidence": None, "rationale": "No genuine ambiguity moment in this transcript."},
    "consistency_issues": [],
    "red_flags": [],
}

JUDGE_GOLD_FACTS_11 = JudgeGoldFacts(
    case_id="judge_case_11_construction_clean",
    description="Clean baseline: accurate description of an initial gating failure fully corrected under pushback.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
    },
    flag_evaluations=[],
)


# =============================================================================
# CASE 12 — Senior Backend Engineer, 6 goals — SEEDED FLAW: hallucinated rationale +
# invalid reasoning coherence isolated to g_03, everything else clean.
# =============================================================================
MOCK_GRADER_OUTPUT_12 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": [
                    "Insists on running EXPLAIN ANALYZE before proposing a fix rather than guessing",
                    "Diagnoses low selectivity from a missing composite index on (customer_id, order_date)",
                    "Weighs write-side index overhead against read-volume benefit before deciding",
                    "Proposes rolling out to a replica and measuring write-latency impact before promoting",
                ],
                "demonstrated_reasoning": ["Updates the working hypothesis at each new piece of information rather than defending an initial guess"],
                "specificity": "high",
            },
            "pushback": {"triggered": False, "response_type": None},
            "score": 9,
            "confidence": "high",
            "criteria_match": {
                "passing_met": ["Describes using EXPLAIN/query plan analysis to find the actual bottleneck", "Correctly reasons about when a composite index helps vs. when it doesn't", "Considers the write-side cost of adding an index"],
                "failed_triggered": [],
            },
            "rationale": "Candidate diagnosed via EXPLAIN ANALYZE at each new piece of information rather than guessing, correctly reasoned about composite index column order and selectivity, and explicitly weighed write-side overhead against read-volume benefit before deciding to proceed.",
        },
        {
            "goal_id": "g_02",
            "addressed": True,
            "evidence": {
                "claims": [
                    "Asks about consistency requirements and write volume before proposing a design",
                    "Chooses a single source-of-truth relational store with row-level/optimistic concurrency given a strong consistency requirement",
                    "Explicitly names the tradeoff: limited horizontal write scalability and geo-distribution versus correctness",
                ],
                "demonstrated_reasoning": [],
                "specificity": "high",
            },
            "pushback": {"triggered": False, "response_type": None},
            "score": 8,
            "confidence": "high",
            "criteria_match": {"passing_met": ["Asks clarifying questions about scale/consistency requirements before designing", "Explicitly names a tradeoff being made"], "failed_triggered": []},
            "rationale": "Candidate asked for consistency and volume requirements before designing, then explicitly named the availability/scalability tradeoff being made in choosing strong consistency.",
        },
        {
            "goal_id": "g_03",
            "addressed": True,
            "evidence": {
                "claims": ["States rollback is the first move to stop customer impact"],
                "demonstrated_reasoning": [],
                "specificity": "high",
            },
            "pushback": {"triggered": False, "response_type": None},
            "score": 8,
            "confidence": "high",
            "criteria_match": {
                "passing_met": ["Prioritizes mitigation/rollback before root-causing"],
                "failed_triggered": ["Jumps straight to a code fix in production without mitigating first"],  # self-contradicts passing_met above
            },
            "rationale": "Candidate prioritized rollback before investigating, but also jumped straight into a code fix without mitigating first.",  # HALLUCINATED — transcript shows only the rollback-first answer; contradicts itself
        },
        {
            "goal_id": "g_04",
            "addressed": True,
            "evidence": {
                "claims": [
                    "States would not run a direct SQL query against production payment data even under manager pressure",
                    "Offers to help through the approved reporting tool, or loop in whoever owns data access if there's a blocker",
                ],
                "demonstrated_reasoning": [],
                "specificity": "high",
            },
            "pushback": {"triggered": False, "response_type": None},
            "score": 9,
            "confidence": "high",
            "criteria_match": {"passing_met": ["States they would not directly query production customer payment data outside approved tooling, even if asked by a manager", "Mentions an appropriate alternative"], "failed_triggered": []},
            "rationale": "Candidate explicitly refused to bypass approved tooling despite deadline pressure from a manager and offered a concrete compliant alternative.",
        },
        {
            "goal_id": "g_05",
            "addressed": True,
            "evidence": {
                "claims": [
                    "Describes a direct one-on-one conversation citing a specific recent PR and the concrete risk it introduced, rather than a generic comment",
                    "States would follow up on the next couple of PRs to check whether the feedback changed behavior",
                ],
                "demonstrated_reasoning": [],
                "specificity": "high",
            },
            "pushback": {"triggered": False, "response_type": None},
            "score": 8,
            "confidence": "high",
            "criteria_match": {"passing_met": ["Describes specific, behavior-focused feedback rather than vague encouragement", "Mentions following up to check whether the feedback landed and led to change"], "failed_triggered": []},
            "rationale": "Candidate described giving specific, example-based feedback rather than vague encouragement, and explicitly planned a concrete follow-up to confirm behavior actually changed.",
        },
        {
            "goal_id": "g_06",
            "addressed": False,
            "evidence": None,
            "pushback": None,
            "score": None,
            "confidence": None,
            "criteria_match": None,
            "rationale": "Never reached before the interview ended.",
        },
    ],
    "problem_solving_under_ambiguity": {
        "addressed": True,
        "score": 9,
        "confidence": "high",
        "rationale": "Across multiple goals the candidate consistently reasoned from evidence rather than guessing — asking clarifying questions in system design and updating a working hypothesis as new diagnostic information arrived in the database goal.",
    },
    "consistency_issues": [],
    "red_flags": [],
}

JUDGE_GOLD_FACTS_12 = JudgeGoldFacts(
    case_id="judge_case_12_backend_six_goal_isolated_flaw",
    description="Five of six goals plus the cross-cutting assessment are clean and accurate. g_03's rationale fabricates a 'jumped straight to a code fix' action that never happened, and self-contradicts its own passing_met entry in the same object.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "g_02": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "g_03": GoldGoalJudgeAssertion(expected_rationale_groundedness="hallucinated", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="invalid"),
        "g_04": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "g_05": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "g_06": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="sound"),
    },
    flag_evaluations=[],
)


# =============================================================================
# CASE 13 — Restaurant Server (clean baseline)
# =============================================================================
MOCK_GRADER_OUTPUT_13 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": [
                    "Initially proposes picking walnuts off the plate for a severe tree-nut allergy",
                    "After challenge, states would inform the kitchen directly, require confirmation of no cross-contact or a remade dish, and offer an alternative if unsafe",
                ],
                "demonstrated_reasoning": [],
                "specificity": "high",
            },
            "pushback": {"triggered": True, "response_type": "conceded_and_corrected"},
            "score": 7,
            "confidence": "high",
            "criteria_match": {
                "passing_met": ["Would double-check with the kitchen or a manager if unsure whether a dish is safe", "Would not serve a dish if there's genuine uncertainty about a life-threatening allergen"],
                "failed_triggered": ["Treats a stated allergy the same as a taste preference"],
            },
            "rationale": "Candidate initially treated a severe allergy like a preference by proposing to pick off the garnish, but after being challenged fully corrected to flagging the kitchen directly and requiring confirmation of safety before serving.",
        },
        {
            "goal_id": "g_02",
            "addressed": True,
            "evidence": {
                "claims": ["States would never adjust a tip amount regardless of whether they disagreed with it or thought the customer wouldn't notice"],
                "demonstrated_reasoning": [],
                "specificity": "high",
            },
            "pushback": {"triggered": False, "response_type": None},
            "score": 9,
            "confidence": "high",
            "criteria_match": {"passing_met": ["States they would not alter a tip amount or misreport cash tips"], "failed_triggered": []},
            "rationale": "Candidate gave an unambiguous, unconditional answer that tip amounts are the customer's decision and would never be altered.",
        },
    ],
    "problem_solving_under_ambiguity": {"addressed": False, "score": None, "confidence": None, "rationale": "No genuine ambiguity moment in this transcript."},
    "consistency_issues": [],
    "red_flags": [],
}

JUDGE_GOLD_FACTS_13 = JudgeGoldFacts(
    case_id="judge_case_13_server_clean",
    description="Clean baseline across both goals.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "g_02": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
    },
    flag_evaluations=[],
)


# =============================================================================
# CASE 14 — Preschool Teacher (clean baseline; religious disclosure correctly excluded)
# =============================================================================
MOCK_GRADER_OUTPUT_14 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": [
                    "Initially considers briefly leaving the group unsupervised to grab a first aid kit",
                    "After challenge, states would call another staff member to watch the group or bring the whole group inside rather than leave anyone unsupervised",
                    "Describes cleaning/bandaging a minor injury immediately, notifying the director, logging it, and telling the parent at pickup regardless of severity",
                ],
                "demonstrated_reasoning": [],
                "specificity": "high",
            },
            "pushback": {"triggered": True, "response_type": "conceded_and_corrected"},
            "score": 7,
            "confidence": "high",
            "criteria_match": {
                "passing_met": ["Describes an appropriate immediate response to an injury"],
                "failed_triggered": ["Describes briefly leaving the classroom unsupervised for a reason that isn't a genuine emergency"],
            },
            "rationale": "Candidate initially proposed briefly leaving the group unsupervised, a critical safety wrong-answer signal, but fully corrected under pushback to arranging coverage before leaving, and separately described a complete and appropriate injury-response process.",
        },
        {
            "goal_id": "g_02",
            "addressed": True,
            "evidence": {
                "claims": ["States would physically step between the two children first, then calmly talk to each separately about what happened before deciding on the toy"],
                "demonstrated_reasoning": [],
                "specificity": "high",
            },
            "pushback": {"triggered": False, "response_type": None},
            "score": 8,
            "confidence": "high",
            "criteria_match": {"passing_met": ["Describes a calm, age-appropriate de-escalation approach", "Would separate children if there's a risk of physical harm to either child"], "failed_triggered": []},
            "rationale": "Candidate prioritized physically separating the children before any conversation, then used calm, individual redirection rather than public discipline.",
        },
    ],
    "problem_solving_under_ambiguity": {"addressed": False, "score": None, "confidence": None, "rationale": "No genuine ambiguity moment in this transcript."},
    "consistency_issues": [],
    "red_flags": [],
}

JUDGE_GOLD_FACTS_14 = JudgeGoldFacts(
    case_id="judge_case_14_preschool_clean",
    description="Clean baseline across both goals; the religious-practice disclosure correctly does not appear anywhere in the output.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "g_02": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
    },
    flag_evaluations=[],
)


# =============================================================================
# CASE 15 — Security Guard — SEEDED FLAW: weak flag reasoning
# =============================================================================
MOCK_GRADER_OUTPUT_15 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": [
                    "States would physically cut off and hold a suspected shoplifter until police arrive, citing a defensive tactics certification",
                    "Maintains this stance even when asked if the person is non-violent",
                    "Cannot describe what the certification actually covered when asked directly",
                ],
                "demonstrated_reasoning": [],
                "specificity": "high",
            },
            "pushback": {"triggered": True, "response_type": "repeated_unchanged"},
            "score": 2,
            "confidence": "high",
            "criteria_match": {
                "passing_met": [],
                "failed_triggered": ["States they would physically tackle or restrain a suspected shoplifter as a first response", "Suggests force is justified purely to prevent property loss, absent a safety threat"],
            },
            "rationale": "Candidate stated they would physically restrain a non-violent suspected shoplifter as a first response and did not change this stance when challenged on the absence of a safety threat.",
        }
    ],
    "problem_solving_under_ambiguity": {"addressed": False, "score": None, "confidence": None, "rationale": "No genuine ambiguity moment in this transcript."},
    "consistency_issues": [],
    "red_flags": [
        {"description": "Candidate seemed a bit unsure of themselves when discussing their training.", "goal_id": "g_01", "severity": "low"}  # WEAK — vague, misses the actual issue
    ],
}

JUDGE_GOLD_FACTS_15 = JudgeGoldFacts(
    case_id="judge_case_15_security_weak_flag",
    description="The per-goal score/rationale/evidence are accurate, but the red flag description is vague ('seemed a bit unsure') and doesn't specifically name the actual credibility issue — that the candidate cited a specific certification to justify force, then couldn't describe what it covered when asked directly.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
    },
    flag_evaluations=[
        GoldFlagJudgeAssertion(flag_type="red_flag", description_excerpt="seemed a bit unsure of themselves when discussing their training", expected_reasoning_quality="weak"),
    ],
)


# =============================================================================
# CASE 16 — Data Entry Clerk, 5 goals (clean baseline; tests consistent low scoring)
# =============================================================================
MOCK_GRADER_OUTPUT_16 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {"claims": ["States they just try to be careful when typing", "When asked for a specific verification step, states they just go slow with no described process"], "demonstrated_reasoning": [], "specificity": "low"},
            "pushback": {"triggered": True, "response_type": "repeated_unchanged"},
            "score": 2,
            "confidence": "high",
            "criteria_match": {"passing_met": [], "failed_triggered": ["Says they just type carefully with no described verification step"]},
            "rationale": "Candidate could not describe any concrete verification step even when asked directly a second time, only restating 'being careful.'",
        },
        {
            "goal_id": "g_02",
            "addressed": True,
            "evidence": {"claims": ["States would guess between a smudged 3 or 8 rather than flag it, even when asked to confirm they're unsure"], "demonstrated_reasoning": [], "specificity": "high"},
            "pushback": {"triggered": True, "response_type": "repeated_unchanged"},
            "score": 2,
            "confidence": "high",
            "criteria_match": {"passing_met": [], "failed_triggered": ["States they would just guess or pick a value that seems reasonable"]},
            "rationale": "Candidate explicitly chose to guess on an illegible value rather than flag it, and confirmed this was intentional to save time when asked directly.",
        },
        {
            "goal_id": "g_03",
            "addressed": True,
            "evidence": {"claims": ["States they never counted or tracked their past daily entry volume"], "demonstrated_reasoning": [], "specificity": "low"},
            "pushback": {"triggered": False, "response_type": None},
            "score": 3,
            "confidence": "medium",
            "criteria_match": {"passing_met": [], "failed_triggered": []},
            "rationale": "Candidate could not provide any concrete estimate of past throughput, suggesting limited self-awareness of performance or limited relevant experience.",
        },
        {
            "goal_id": "g_04",
            "addressed": True,
            "evidence": {"claims": ["States it would probably be fine to mention a small, seemingly non-personal detail like a name from a record to a friend"], "demonstrated_reasoning": [], "specificity": "high"},
            "pushback": {"triggered": False, "response_type": None},
            "score": 2,
            "confidence": "high",
            "criteria_match": {"passing_met": [], "failed_triggered": ["Suggests it would be fine to mention specific record details to friends/family since it's 'not a big deal'"]},
            "rationale": "Candidate directly stated it would be fine to share a name from a record with a friend if it seemed minor, matching the wrong-answer signal for treating confidentiality as situational rather than absolute.",
        },
        {
            "goal_id": "g_05",
            "addressed": True,
            "evidence": {"claims": ["Describes themselves generally as 'a fast learner' without a specific past example of learning a new tool"], "demonstrated_reasoning": [], "specificity": "low"},
            "pushback": {"triggered": False, "response_type": None},
            "score": 3,
            "confidence": "medium",
            "criteria_match": {"passing_met": [], "failed_triggered": ["Cannot describe any specific example of learning a new tool"]},
            "rationale": "Candidate gave only a general self-description with no concrete example when asked for a specific instance of learning new software.",
        },
    ],
    "problem_solving_under_ambiguity": {"addressed": False, "score": None, "confidence": None, "rationale": "No genuine ambiguity moment in this transcript."},
    "consistency_issues": [],
    "red_flags": [],
}

JUDGE_GOLD_FACTS_16 = JudgeGoldFacts(
    case_id="judge_case_16_data_entry_clean_five_goals",
    description="Clean baseline: five consistently low, accurately-described scores — tests that the judge doesn't need score-drift correction since this grader output is already internally sound throughout.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "g_02": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "g_03": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "g_04": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "g_05": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
    },
    flag_evaluations=[],
)


# =============================================================================
# CASE 17 — Collections Agent — SEEDED FLAW: incorrect (over-)flag alongside two sound ones
# =============================================================================
MOCK_GRADER_OUTPUT_17 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": [
                    "States would call multiple times throughout the day to wear the customer down",
                    "States would try the customer's workplace number or a family member's contact if repeated calls fail",
                    "Maintains this stance even after being told this is a fair debt collection violation",
                ],
                "demonstrated_reasoning": [],
                "specificity": "high",
            },
            "pushback": {"triggered": True, "response_type": "repeated_unchanged"},
            "score": 2,
            "confidence": "high",
            "criteria_match": {
                "passing_met": [],
                "failed_triggered": ["Describes calling repeatedly in the same day to wear the customer down", "Suggests contacting the customer's employer or family members to apply pressure"],
            },
            "rationale": "Candidate described repeated same-day calling and contacting a debtor's workplace or family as pressure tactics, and did not retract this even after being told it constitutes a fair debt collection violation.",
        }
    ],
    "problem_solving_under_ambiguity": {"addressed": False, "score": None, "confidence": None, "rationale": "No genuine ambiguity moment in this transcript."},
    "consistency_issues": [],
    "red_flags": [
        {"description": "Candidate described contacting a debtor's employer or family members to relay pressure about an outstanding debt, which violates standard fair debt collection practice.", "goal_id": "g_01", "severity": "high"},
        {"description": "Candidate described repeated same-day calling intended to wear down a non-responsive debtor.", "goal_id": "g_01", "severity": "medium"},
        {"description": "Candidate mentioned calling in the evening, which is an inappropriate time to contact customers.", "goal_id": "g_01", "severity": "low"},  # INCORRECT — misreads a harmless detail
    ],
}

JUDGE_GOLD_FACTS_17 = JudgeGoldFacts(
    case_id="judge_case_17_collections_over_flag",
    description="Two of the three red flags are legitimate and well-supported; the third ('calling in the evening') misreads the candidate simply describing call frequency spread across the day as its own separate violation — there's no actual evening-hours rule at issue in the transcript.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
    },
    flag_evaluations=[
        GoldFlagJudgeAssertion(flag_type="red_flag", description_excerpt="contacting employer or family members", expected_reasoning_quality="sound"),
        GoldFlagJudgeAssertion(flag_type="red_flag", description_excerpt="repeated same-day calling", expected_reasoning_quality="sound"),
        GoldFlagJudgeAssertion(flag_type="red_flag", description_excerpt="calling in the evening", expected_reasoning_quality="incorrect"),
    ],
)


# =============================================================================
# CASE 18 — Licensed Electrician (clean baseline)
# =============================================================================
MOCK_GRADER_OUTPUT_18 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": ["Initially states would skip re-testing for a familiar panel to save time", "After challenge, states would always de-energize and verify with a tester regardless of familiarity or job length"],
                "demonstrated_reasoning": [],
                "specificity": "high",
            },
            "pushback": {"triggered": True, "response_type": "conceded_and_corrected"},
            "score": 7,
            "confidence": "high",
            "criteria_match": {
                "passing_met": ["States they would fully de-energize and verify with a tester before touching panel wiring, every time"],
                "failed_triggered": ["States they'd sometimes work on a panel live, or skip verification, for a quick or familiar job"],
            },
            "rationale": "Candidate initially described skipping verification on familiar panels to save time, a critical safety gap, but fully reversed under pushback to a strict no-exceptions verification habit.",
        },
        {
            "goal_id": "g_02",
            "addressed": True,
            "evidence": {"claims": ["States approximately 12 years of licensed experience", "States licensed in 2019, which implies roughly 6 years"], "demonstrated_reasoning": [], "specificity": "high"},
            "pushback": {"triggered": False, "response_type": None},
            "score": 2,
            "confidence": "high",
            "criteria_match": {"passing_met": [], "failed_triggered": ["Gives materially different, unreconciled numbers of years of experience"]},
            "rationale": "Candidate stated approximately 12 years of licensed experience, then gave a 2019 licensing date implying roughly 6 years, with no explanation reconciling the two.",
        },
    ],
    "problem_solving_under_ambiguity": {"addressed": False, "score": None, "confidence": None, "rationale": "No genuine ambiguity moment in this transcript."},
    "consistency_issues": [
        {"description": "Candidate first states approximately 12 years of licensed experience, then states a 2019 licensing date that implies roughly 6 years, with no reconciling explanation offered.", "goal_ids_involved": ["g_02"]}
    ],
    "red_flags": [],
}

JUDGE_GOLD_FACTS_18 = JudgeGoldFacts(
    case_id="judge_case_18_electrician_clean",
    description="Clean baseline: accurate gating-recovery description and an accurately identified self-contradiction on years of experience.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "g_02": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
    },
    flag_evaluations=[
        GoldFlagJudgeAssertion(flag_type="consistency_issue", description_excerpt="12 years vs 2019 licensing date implying 6 years", expected_reasoning_quality="sound"),
    ],
)


# =============================================================================
# CASE 19 — Trust & Safety Content Moderator (clean baseline; long transcript, mental-health
# disclosure correctly excluded, genuine ambiguity-escalation credited)
# =============================================================================
MOCK_GRADER_OUTPUT_19 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": [
                    "Applies written policy criteria rather than personal reaction to graphic content",
                    "Distinguishes newsworthy documentary footage from the same footage reuploaded with celebratory captions",
                    "Escalates a genuinely ambiguous, uncaptioned case to a second reviewer rather than guessing",
                    "Uses scheduled breaks and has used counseling resources rather than pushing through alone",
                    "Applies the policy as written even when personally disagreeing with where it draws a line",
                ],
                "demonstrated_reasoning": ["Reasons through how caption and framing change the same underlying footage's policy category"],
                "specificity": "high",
            },
            "pushback": {"triggered": False, "response_type": None},
            "score": 9,
            "confidence": "high",
            "criteria_match": {
                "passing_met": [
                    "Describes applying the stated policy criteria consistently, not a personal gut reaction, to borderline content",
                    "Mentions using available support resources as a normal part of the job",
                    "Recognizes and flags a genuinely ambiguous case for a second reviewer rather than guessing",
                ],
                "failed_triggered": [],
            },
            "rationale": "Candidate consistently applied policy criteria across several escalating variations of the same content, correctly escalated a genuinely ambiguous uncaptioned case rather than guessing, and described healthy, normalized use of support resources.",
        }
    ],
    "problem_solving_under_ambiguity": {
        "addressed": True,
        "score": 9,
        "confidence": "high",
        "rationale": "When faced with a genuinely ambiguous piece of content the written policy didn't clearly resolve, candidate explicitly declined to guess and escalated to a second reviewer instead.",
    },
    "consistency_issues": [],
    "red_flags": [],
}

JUDGE_GOLD_FACTS_19 = JudgeGoldFacts(
    case_id="judge_case_19_moderator_clean_long_transcript",
    description="Clean baseline on a long 16-turn transcript; the past sleep-disruption disclosure correctly does not appear anywhere in the output.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="sound"),
    },
    flag_evaluations=[],
)


# =============================================================================
# CASE 20 — Retail Loss Prevention Associate (clean baseline; genuine bias red flag)
# =============================================================================
MOCK_GRADER_OUTPUT_20 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": [
                    "Initially names concealment, camera-checking, and avoiding staff as behavior-based signals",
                    "States would pay closer attention to younger men in baggy clothes/hoodies as a starting point, even before any specific behavior",
                    "Maintains this even when directly asked if it's based on age and dress alone",
                ],
                "demonstrated_reasoning": [],
                "specificity": "high",
            },
            "pushback": {"triggered": True, "response_type": "repeated_unchanged"},
            "score": 2,
            "confidence": "high",
            "criteria_match": {
                "passing_met": ["Describes specific observable behaviors as the basis for suspicion"],
                "failed_triggered": ["Describes a customer's age group or manner of dress as a legitimate basis for increased suspicion on its own"],
            },
            "rationale": "Candidate began with correct, behavior-based reasoning but then explicitly stated that a customer's age and clothing are an independent starting point for suspicion prior to any observed behavior, and maintained this when directly challenged.",
        }
    ],
    "problem_solving_under_ambiguity": {"addressed": False, "score": None, "confidence": None, "rationale": "No genuine ambiguity moment in this transcript."},
    "consistency_issues": [],
    "red_flags": [
        {"description": "Candidate stated that a customer's age group and manner of dress are a legitimate independent basis for increased suspicion, absent any observed behavior — discriminatory profiling reasoning, not behavior-based loss prevention.", "goal_id": "g_01", "severity": "high"}
    ],
}

JUDGE_GOLD_FACTS_20 = JudgeGoldFacts(
    case_id="judge_case_20_loss_prevention_clean",
    description="Clean baseline: an accurately described and accurately flagged genuine bias/profiling issue.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
    },
    flag_evaluations=[
        GoldFlagJudgeAssertion(flag_type="red_flag", description_excerpt="age and dress as independent basis for suspicion", expected_reasoning_quality="sound"),
    ],
)


# =============================================================================
# CASE 21 — Executive Assistant (clean baseline; valid-alternative scheduling answer not
# penalized, and correctly NOT counted as problem-solving-under-ambiguity)
# =============================================================================
MOCK_GRADER_OUTPUT_21 = {
    "goals": [
        {
            "goal_id": "g_01",
            "addressed": True,
            "evidence": {
                "claims": ["States would not share calendar details with the CFO based on title alone without verifying authorization", "States would check with the CEO directly or use the standard coordination process instead"],
                "demonstrated_reasoning": [],
                "specificity": "high",
            },
            "pushback": {"triggered": False, "response_type": None},
            "score": 9,
            "confidence": "high",
            "criteria_match": {
                "passing_met": ["States they would not disclose confidential information without authorization, including to other senior staff", "Would verify authorization through an appropriate channel"],
                "failed_triggered": [],
            },
            "rationale": "Candidate declined to share calendar details with a senior executive based on seniority alone and instead described verifying authorization through the CEO directly.",
        },
        {
            "goal_id": "g_02",
            "addressed": True,
            "evidence": {
                "claims": ["Proposes flagging both the board commitment and the customer urgency to the CEO with the stakes on each side", "Suggests requesting a short delay from the board committee or having another executive start the customer call"],
                "demonstrated_reasoning": ["Weighs the standing value of the board commitment against the urgency of the contract-risk customer call before proposing concrete options"],
                "specificity": "high",
            },
            "pushback": {"triggered": False, "response_type": None},
            "score": 8,
            "confidence": "high",
            "criteria_match": {"passing_met": ["Proposes a specific, actionable resolution to the conflict", "Shows awareness of the relative importance/stakes of the competing commitments"], "failed_triggered": []},
            "rationale": "Candidate proposed two concrete, stakes-aware resolution options rather than a single scripted answer, and left the final call to the CEO with the tradeoffs clearly laid out — a valid approach to this open-ended conflict, not a mismatch against any single example resolution.",
        },
    ],
    "problem_solving_under_ambiguity": {
        "addressed": False,
        "score": None,
        "confidence": None,
        "rationale": "The candidate was confident and decisive throughout; the ambiguity here was external to the situation, not a moment of the candidate's own uncertainty, so this does not count as a problem-solving-under-ambiguity signal.",
    },
    "consistency_issues": [],
    "red_flags": [],
}

JUDGE_GOLD_FACTS_21 = JudgeGoldFacts(
    case_id="judge_case_21_executive_assistant_clean",
    description="Clean baseline across both goals; correctly does not credit the confident, decisive scheduling answer as a problem-solving-under-ambiguity instance despite the situation itself being open-ended.",
    per_goal={
        "g_01": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "g_02": GoldGoalJudgeAssertion(expected_rationale_groundedness="grounded", expected_evidence_faithfulness="faithful", expected_reasoning_coherence="sound"),
        "problem_solving_under_ambiguity": GoldGoalJudgeAssertion(expected_rationale_groundedness="n_a", expected_evidence_faithfulness="n_a", expected_reasoning_coherence="n_a"),
    },
    flag_evaluations=[],
)


# =============================================================================
# Convenience registries for test runners
# =============================================================================
ALL_MOCK_GRADER_OUTPUTS = {
    "02": MOCK_GRADER_OUTPUT_02, "03": MOCK_GRADER_OUTPUT_03, "04": MOCK_GRADER_OUTPUT_04,
    "05": MOCK_GRADER_OUTPUT_05, "06": MOCK_GRADER_OUTPUT_06, "07": MOCK_GRADER_OUTPUT_07,
    "08": MOCK_GRADER_OUTPUT_08, "09": MOCK_GRADER_OUTPUT_09, "10": MOCK_GRADER_OUTPUT_10,
    "11": MOCK_GRADER_OUTPUT_11, "12": MOCK_GRADER_OUTPUT_12, "13": MOCK_GRADER_OUTPUT_13,
    "14": MOCK_GRADER_OUTPUT_14, "15": MOCK_GRADER_OUTPUT_15, "16": MOCK_GRADER_OUTPUT_16,
    "17": MOCK_GRADER_OUTPUT_17, "18": MOCK_GRADER_OUTPUT_18, "19": MOCK_GRADER_OUTPUT_19,
    "20": MOCK_GRADER_OUTPUT_20, "21": MOCK_GRADER_OUTPUT_21,
}

ALL_JUDGE_GOLD_FACTS = {
    "02": JUDGE_GOLD_FACTS_02, "03": JUDGE_GOLD_FACTS_03, "04": JUDGE_GOLD_FACTS_04,
    "05": JUDGE_GOLD_FACTS_05, "06": JUDGE_GOLD_FACTS_06, "07": JUDGE_GOLD_FACTS_07,
    "08": JUDGE_GOLD_FACTS_08, "09": JUDGE_GOLD_FACTS_09, "10": JUDGE_GOLD_FACTS_10,
    "11": JUDGE_GOLD_FACTS_11, "12": JUDGE_GOLD_FACTS_12, "13": JUDGE_GOLD_FACTS_13,
    "14": JUDGE_GOLD_FACTS_14, "15": JUDGE_GOLD_FACTS_15, "16": JUDGE_GOLD_FACTS_16,
    "17": JUDGE_GOLD_FACTS_17, "18": JUDGE_GOLD_FACTS_18, "19": JUDGE_GOLD_FACTS_19,
    "20": JUDGE_GOLD_FACTS_20, "21": JUDGE_GOLD_FACTS_21,
}

# Cases with a deliberately seeded flaw, for quickly running just the negative-detection subset.
SEEDED_FLAW_CASE_IDS = ["03", "05", "08", "10", "12", "15", "17"]

ALL_TEST_CASES = [
    (ALL_MOCK_GRADER_OUTPUTS[k], ALL_JUDGE_GOLD_FACTS[k])
    for k in sorted(ALL_JUDGE_GOLD_FACTS.keys())
]