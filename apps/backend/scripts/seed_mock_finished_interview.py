"""
What: Seed script for a finished interview with candidate transcripts and a grading report.
Why: Provides realistic end-to-end data for testing the frontend candidate report and transcript views.
Boundaries: Standalone script, not imported by the main application.
"""

import asyncio
import sys
import os
from datetime import datetime, UTC, timedelta

# Ensure src/ is in the path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from sqlalchemy import select, text
from app.core.db import async_session_factory
from app.models.user import User
from app.models.interview import Interview
from app.models.goal import Goal
from app.models.candidate import Candidate
from app.models.transcript import Transcript
from app.models.report import CandidateReport

MOCK_INTERVIEW_DATA = {
    "job_name": "Senior Quantitative Trader",
    "job_description": "We are looking for a Senior Quantitative Trader to join our proprietary trading desk, responsible for designing, deploying, and actively managing market-making and statistical arbitrage strategies across liquid futures, options, and derivatives markets. You will monitor live positions throughout the trading day, adjust quoting parameters in response to changing market microstructure and order book depth, and manage risk limits and drawdown thresholds in real time. You'll analyze execution quality (slippage, fill rates, latency) and work with quant researchers and engineers to refine signal generation and execution logic. Strong programming skills in Python or C++ for backtesting and strategy prototyping are expected.",
    "difficulty": "senior",
    "num_goals": 3,
    "total_duration_minutes": 30,
    "goals": [
        {
            "goal_ref": "g_01",
            "topic": "Market Making Microstructure & Order Book Dynamics",
            "goal": "Assess the candidate's understanding of order book depth, bid-ask spread dynamics, and how they dynamically adjust quoting parameters during high-volatility regime shifts.",
            "passing_criteria": [
                "Explains bid-ask spread adjustments based on order imbalance",
                "Demonstrates awareness of adverse selection risks during news events",
                "Understands depth-weighted micro-price calculations"
            ],
            "pushback_triggers": [{"trigger": "overconfidence_in_static_spreads", "action": "challenge_with_flash_crash_scenario"}],
            "wrong_answer_signals": ["suggesting fixed spread quoting during earnings releases"],
            "grounding_theory": "Order book dynamics require real-time pricing using micro-price (volume-weighted mid price) rather than simple mid-price, accounting for adverse selection.",
            "weight": 1.2
        },
        {
            "goal_ref": "g_02",
            "topic": "Risk Management & Drawdown Controls",
            "goal": "Evaluate the candidate's real-time risk mitigation techniques, including hard drawdown limits, max position limits, and delta/gamma hedging in options.",
            "passing_criteria": [
                "Defines hard cut-off rules for intraday max drawdown",
                "Explains dynamic delta hedging frequency vs transaction cost tradeoff"
            ],
            "pushback_triggers": [{"trigger": "ignoring_transaction_costs", "action": "pushback_on_infinite_rebalancing"}],
            "wrong_answer_signals": ["doubling down on losing positions without risk approval"],
            "grounding_theory": "Intraday risk controls must enforce automated kill switches when trailing drawdowns breach 2% of allocated capital.",
            "weight": 1.0
        },
        {
            "goal_ref": "g_03",
            "topic": "Execution Quality & Algorithmic Strategy Prototyping",
            "goal": "Verify the candidate's ability to prototype statistical arbitrage signals in Python/C++ and optimize execution algorithms (TWAP/VWAP/Implementation Shortfall).",
            "passing_criteria": [
                "Articulates difference between VWAP and Implementation Shortfall",
                "Demonstrates vectorization techniques in Python/C++ to eliminate backtest latency"
            ],
            "pushback_triggers": [],
            "wrong_answer_signals": ["using unvectorized Python loops for tick-by-tick simulation"],
            "grounding_theory": "Implementation Shortfall measures total execution cost against decision price, factoring in market impact and delay risk.",
            "weight": 0.8
        }
    ]
}

MOCK_CANDIDATE = {
    "first_name": "Marcus",
    "last_name": "Vance",
    "email": "marcus.vance@example.com",
    "status": "finished",
    "composite_score": 8.8,
    "recommendation": "Advance"
}

RAW_GRADING_REPORT = {
    "candidate_name": "Marcus Vance",
    "overall_score": 8.8,
    "recommendation": "Advance",
    "confidence_level": "high",
    "executive_summary": "Marcus demonstrated exceptional technical expertise in quantitative market-making and real-time risk controls. He displayed deep mastery of order book microstructure, accurately explaining micro-price volume weighting and adverse selection mitigation during regime shifts. His Python workflow emphasizes vectorization and low-latency backtesting.",
    "goal_breakdown": [
        {
            "goal_id": "g_01",
            "topic": "Market Making Microstructure & Order Book Dynamics",
            "score": 9.2,
            "status": "passed",
            "key_observations": "Accurately calculated depth-weighted micro-price and explained dynamic spread widening under order imbalance.",
            "matched_criteria": [
                "Explains bid-ask spread adjustments based on order imbalance",
                "Demonstrates awareness of adverse selection risks during news events",
                "Understands depth-weighted micro-price calculations"
            ]
        },
        {
            "goal_id": "g_02",
            "topic": "Risk Management & Drawdown Controls",
            "score": 8.5,
            "status": "passed",
            "key_observations": "Strong risk discipline. Explicitly highlighted hard automated kill-switches at 2% intraday drawdown.",
            "matched_criteria": [
                "Defines hard cut-off rules for intraday max drawdown",
                "Explains dynamic delta hedging frequency vs transaction cost tradeoff"
            ]
        },
        {
            "goal_id": "g_03",
            "topic": "Execution Quality & Algorithmic Strategy Prototyping",
            "score": 8.7,
            "status": "passed",
            "key_observations": "Clear understanding of Implementation Shortfall vs VWAP. Provided clean C++ and vectorized Python optimization examples.",
            "matched_criteria": [
                "Articulates difference between VWAP and Implementation Shortfall",
                "Demonstrates vectorization techniques in Python/C++ to eliminate backtest latency"
            ]
        }
    ],
    "communication": {
        "overall": {
            "is_passed": True,
            "confidence": "high",
            "traits_passed": 4,
            "traits_failed": 0,
            "traits_not_addressed": 0,
            "rule_applied": "majority_pass",
            "rationale": "Candidate exhibited clear, structured communication across all traits."
        },
        "traits": {
            "clarity": {
                "addressed": True,
                "is_passed": True,
                "score": 9.5,
                "confidence": "high",
                "evidence": ["Direct and clear explanations during technical market microstructure questions."],
                "rationale": "Explanations were clear and easy to follow."
            },
            "structure": {
                "addressed": True,
                "is_passed": True,
                "score": 9.0,
                "confidence": "high",
                "evidence": ["Structured response sequentially from order book micro-price to risk limits."],
                "rationale": "Logical breakdown of complex quantitative concepts."
            },
            "assertiveness": {
                "addressed": True,
                "is_passed": True,
                "score": 8.5,
                "confidence": "high",
                "evidence": ["Defended dynamic spread skewing under adverse selection."],
                "rationale": "Confident tone when discussing risk cut-offs."
            },
            "active_listening": {
                "addressed": True,
                "is_passed": True,
                "score": 9.0,
                "confidence": "high",
                "evidence": ["Directly addressed latency and vectorization questions."],
                "rationale": "Acknowledged interviewer prompts without interrupting."
            }
        }
    },
    "injection_findings": {
        "prompt_injection_detected": False,
        "risk_flags": []
    }
}

async def seed_finished_interview():
    async with async_session_factory() as session:
        # Fetch admin user
        result = await session.execute(select(User).where(User.email == "admin@example.com"))
        admin = result.scalar_one_or_none()
        
        if not admin:
            print("Error: admin@example.com not found. Run seed_mock_user.py first.")
            return

        # Delete existing Senior Quantitative Trader interview if present (along with child records)
        existing_interviews = await session.execute(
            select(Interview).where(
                Interview.creator_id == admin.id, 
                Interview.job_name == MOCK_INTERVIEW_DATA["job_name"]
            )
        )
        for old_int in existing_interviews.scalars().all():
            # Delete candidates and their reports/transcripts
            cands = (await session.execute(select(Candidate).where(Candidate.interview_id == old_int.id))).scalars().all()
            for c in cands:
                await session.execute(select(CandidateReport).where(CandidateReport.candidate_id == c.id))
                # Delete reports and transcripts
                await session.execute(text("DELETE FROM candidate_reports WHERE candidate_id = :cid"), {"cid": c.id})
                await session.execute(text("DELETE FROM transcripts WHERE candidate_id = :cid"), {"cid": c.id})
                await session.delete(c)
            # Delete goals
            await session.execute(text("DELETE FROM goals WHERE interview_id = :iid"), {"iid": old_int.id})
            await session.delete(old_int)
        await session.flush()

        print("Creating 2nd mock interview ('Senior Quantitative Trader')...")
        interview = Interview(
            creator_id=admin.id,
            job_name=MOCK_INTERVIEW_DATA["job_name"],
            job_description=MOCK_INTERVIEW_DATA["job_description"],
            difficulty=MOCK_INTERVIEW_DATA["difficulty"],
            num_goals=MOCK_INTERVIEW_DATA["num_goals"],
            total_duration_minutes=MOCK_INTERVIEW_DATA["total_duration_minutes"],
            status="scheduled"
        )
        session.add(interview)
        await session.flush()

        # Add Goals
        goals_db = {}
        for g_data in MOCK_INTERVIEW_DATA["goals"]:
            goal = Goal(
                goal_ref=g_data["goal_ref"],
                interview_id=interview.id,
                topic=g_data["topic"],
                goal=g_data["goal"],
                passing_criteria=g_data["passing_criteria"],
                pushback_triggers=g_data["pushback_triggers"],
                wrong_answer_signals=g_data["wrong_answer_signals"],
                grounding_theory=g_data["grounding_theory"],
                weight=g_data["weight"],
                references=[]
            )
            session.add(goal)
            await session.flush()
            goals_db[g_data["goal_ref"]] = goal

        # Add Finished Candidate
        print("Creating finished candidate (Marcus Vance)...")
        candidate = Candidate(
            interview_id=interview.id,
            first_name=MOCK_CANDIDATE["first_name"],
            last_name=MOCK_CANDIDATE["last_name"],
            email=MOCK_CANDIDATE["email"],
            status=MOCK_CANDIDATE["status"],
            composite_score=MOCK_CANDIDATE["composite_score"],
            recommendation=MOCK_CANDIDATE["recommendation"]
        )
        session.add(candidate)
        await session.flush()

        # Add Transcripts
        print("Inserting conversation transcripts...")
        now = datetime.now(UTC) - timedelta(minutes=30)
        
        # Goal 1 Turns
        t1_q = Transcript(
            candidate_id=candidate.id,
            goal_id=goals_db["g_01"].id,
            role="interviewer",
            content="Welcome Marcus. Let's start with market making. How do you adjust your quoting spread when you observe a severe order book imbalance?",
            action="evaluate_goal",
            reasoning="Opening goal g_01 to assess order book dynamics.",
            created_at=now
        )
        t1_a = Transcript(
            candidate_id=candidate.id,
            goal_id=goals_db["g_01"].id,
            role="candidate",
            content="When order book imbalance favors aggressive buys, holding a neutral mid-price exposes us to adverse selection. I shift the micro-price using a volume-weighted formula across the top 5 bids and asks, and skew the quoting spread outward on the ask side to discourage toxic flow.",
            created_at=now + timedelta(seconds=45)
        )
        session.add_all([t1_q, t1_a])

        # Goal 2 Turns
        t2_q = Transcript(
            candidate_id=candidate.id,
            goal_id=goals_db["g_02"].id,
            role="interviewer",
            content="That makes sense. Moving on to risk control—what is your exact protocol when an automated strategy breaches its intraday drawdown threshold?",
            action="advance",
            reasoning="Candidate passed g_01 criteria cleanly. Moving to risk management g_02.",
            created_at=now + timedelta(minutes=10)
        )
        t2_a = Transcript(
            candidate_id=candidate.id,
            goal_id=goals_db["g_02"].id,
            role="candidate",
            content="We enforce a hard, unbypassable circuit breaker at 2% capital drawdown. The system immediately cancels all active limit orders and routes market orders to flatten net delta. No manual override is allowed without risk committee sign-off.",
            created_at=now + timedelta(minutes=10, seconds=50)
        )
        session.add_all([t2_q, t2_a])

        # Goal 3 Turns
        t3_q = Transcript(
            candidate_id=candidate.id,
            goal_id=goals_db["g_03"].id,
            role="interviewer",
            content="Great. Lastly, how do you minimize latency when backtesting tick-level statistical arbitrage strategies in Python?",
            action="advance",
            reasoning="Advancing to technical execution g_03.",
            created_at=now + timedelta(minutes=20)
        )
        t3_a = Transcript(
            candidate_id=candidate.id,
            goal_id=goals_db["g_03"].id,
            role="candidate",
            content="I eliminate all Python level loops by using vectorized NumPy operations and Polars/PyArrow tables. For execution logic, I write core matching routines in C++ with Python bindings via pybind11 to handle millions of tick events per second.",
            created_at=now + timedelta(minutes=20, seconds=40)
        )
        session.add_all([t3_q, t3_a])

        # Add Grading Report
        print("Inserting CandidateReport...")
        report = CandidateReport(
            candidate_id=candidate.id,
            overall_confidence="high",
            reasoning=RAW_GRADING_REPORT["executive_summary"],
            raw_report=RAW_GRADING_REPORT,
            grader_version="v1.0.0"
        )
        session.add(report)

        await session.commit()
        print("Successfully seeded 2nd interview, goals, finished candidate, transcripts, and report!")

if __name__ == "__main__":
    asyncio.run(seed_finished_interview())
