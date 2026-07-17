"""
What: Defines and registers the LangSmith experiment and evaluators for the Planner Node.
Why: Enables continuous tuning and regression testing of the planner's qualitative outputs and algorithmic constraints.
Boundaries: Does not create mock data entries directly (leaves the dataset empty for user population).
"""

import os
import sys
import json
import math
import importlib
from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field

# Setup path imports for question-maker-agent monorepo structure
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))          # question-maker-agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))       # agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))  # workspace root

from langsmith import Client, evaluate
from langchain_core.messages import SystemMessage, HumanMessage

# Import Gemini clients
from apps.agents.shared.clients import gemini_flash_lite

# Dynamically import planner modules to avoid dash syntax restrictions
planner_module = importlib.import_module("question-maker-agent.nodes.planner")
plan_node = planner_module.plan_node

# Import qualitative judge prompts
eval_prompts_module = importlib.import_module("question-maker-agent.prompts.planner_eval_prompt")
PLANNER_EVAL_SYSTEM_INSTRUCTION = eval_prompts_module.PLANNER_EVAL_SYSTEM_INSTRUCTION
PLANNER_EVAL_USER_TEMPLATE = eval_prompts_module.PLANNER_EVAL_USER_TEMPLATE


DATASET_EXAMPLES = [
    # --- 1-5: Diverse Roles (Standard & Hard Cases) ---
    {
        "inputs": {
            "job_name": "Mid-level Fullstack React/Node Developer",
            "job_description": "We are looking for a Fullstack Engineer with strong proficiency in React for frontend development and Node.js with Express for building scalable APIs. Experience with PostgreSQL, RESTful architecture, and Docker containerization is required. The ideal candidate will write clean code, create modular components, and participate in code reviews.",
            "difficulty": "mid",
            "num_goals": 4,
            "total_duration_minutes": 60,
            "domain_hint": "software"
        },
        "outputs": {}
    },
    {
        "inputs": {
            "job_name": "Professional Video Editor",
            "job_description": "We are looking for an experienced Video Editor to assemble raw footage into high-quality promotional videos and documentaries. Expertise in Adobe Premiere Pro, color grading, audio synchronization, and editing pacing for narrative flow is required. The candidate must handle tight deadlines, incorporate director feedback, and manage digital video assets.",
            "difficulty": "mid",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "creative"
        },
        "outputs": {}
    },
    {
        "inputs": {
            "job_name": "Senior Quantitative Trader",
            "job_description": "Join our prop trading desk. You will design, execute, and monitor market-making and arbitrage strategies for liquid futures and derivatives markets. Deep understanding of market microstructure, order book dynamics, risk limits, draw-down management, and execution latency is expected.",
            "difficulty": "senior",
            "num_goals": 5,
            "total_duration_minutes": 60,
            "domain_hint": "finance"
        },
        "outputs": {}
    },
    {
        "inputs": {
            "job_name": "Customer Service Lead",
            "job_description": "Lead our tier-1 support team. You will handle ticket queues (Zendesk), monitor team CSAT metrics, manage high-stress client escalations, and write clear response templates. Strong active listening, conflict resolution, and team mentoring skills are required.",
            "difficulty": "mid",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "support"
        },
        "outputs": {}
    },
    {
        "inputs": {
            "job_name": "Technical Recruiter",
            "job_description": "Manage our full-cycle recruitment pipeline for engineering and design roles. Responsible for sourcing candidates via LinkedIn, running initial phone screenings, selling our company culture, negotiating compensation offers, and coordinating with hiring managers.",
            "difficulty": "mid",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "hr"
        },
        "outputs": {}
    },
    # --- 6-10: Vague / Underspecified Inputs (Inference Testing) ---
    {
        "inputs": {
            "job_name": "Content Writer",
            "job_description": "Write articles and content for our company blog to help us get more traffic.",
            "difficulty": "infer",
            "num_goals": 3,
            "total_duration_minutes": 30,
            "domain_hint": "creative"
        },
        "outputs": {}
    },
    {
        "inputs": {
            "job_name": "Retail Sales Associate",
            "job_description": "Sell items in our clothing store and help walk-in customers.",
            "difficulty": "junior",
            "num_goals": 3,
            "total_duration_minutes": 30,
            "domain_hint": "sales"
        },
        "outputs": {}
    },
    {
        "inputs": {
            "job_name": "Executive Assistant",
            "job_description": "Manage calendar schedules, organize travel logistics, and filter communications for the leadership team.",
            "difficulty": "mid",
            "num_goals": 3,
            "total_duration_minutes": 30,
            "domain_hint": "support"
        },
        "outputs": {}
    },
    {
        "inputs": {
            "job_name": "Office Manager",
            "job_description": "Keep our office running smoothly, order supplies, and handle visitor logistics.",
            "difficulty": "infer",
            "num_goals": 3,
            "total_duration_minutes": 30,
            "domain_hint": "support"
        },
        "outputs": {}
    },
    {
        "inputs": {
            "job_name": "Financial Analyst",
            "job_description": "Analyze spreadsheets, track company budgets, and make financial forecast reports.",
            "difficulty": "mid",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "finance"
        },
        "outputs": {}
    },
    # --- 11-15: Technical / Specialized Roles ---
    {
        "inputs": {
            "job_name": "Embedded Firmware Engineer",
            "job_description": "Join our robotics team to develop firmware for motor control boards. You'll work with STM32 microcontrollers, write low-level C for real-time control loops, and debug issues using a JTAG debugger and oscilloscope. Experience with RTOS (FreeRTOS), CAN bus communication, and basic PID control tuning is expected.",
            "difficulty": "mid",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "hardware"
        },
        "outputs": {}
    },
    {
        "inputs": {
            "job_name": "Senior Graphic Designer",
            "job_description": "We are seeking a senior designer to own our visual branding. Expertise in typography, color theory, page layout composition, and Adobe Illustrator/Photoshop/Figma is required. You will direct client revisions and deliver assets for digital and print media.",
            "difficulty": "senior",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "creative"
        },
        "outputs": {}
    },
    {
        "inputs": {
            "job_name": "Product Manager",
            "job_description": "Bridge the gap between product strategy and engineering. Responsible for translating user research into product requirements, running roadmap grooming sessions, prioritizing feature requests, and coordinating with design and tech teams.",
            "difficulty": "mid",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "management"
        },
        "outputs": {}
    },
    {
        "inputs": {
            "job_name": "B2B Enterprise Account Executive",
            "job_description": "Manage our enterprise sales pipeline. Deliver product demos to executive clients, navigate complex procurement processes, handle pricing and contract negotiations, and close five-to-six figure subscription deals.",
            "difficulty": "senior",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "sales"
        },
        "outputs": {}
    },
    {
        "inputs": {
            "job_name": "QA Automation Engineer",
            "job_description": "Develop and maintain our automated testing suites. Experience with Selenium WebDriver, Playwright, or Cypress is required. You will write automated end-to-end integration tests using Python or JavaScript, configure test execution in Jenkins pipelines, and document test cases.",
            "difficulty": "mid",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "qa"
        },
        "outputs": {}
    },
    # --- 16-20: Hard Edge Cases & Constraint Stress ---
    {
        "inputs": {
            "job_name": "Junior Copy Editor",
            "job_description": "ENTRY LEVEL spelling and grammar proofreading position. Must have 10+ years experience in complex international treaty arbitration, intellectual property litigation editing, and corporate mergers law.",
            "difficulty": "junior",
            "num_goals": 3,
            "total_duration_minutes": 45,
            "domain_hint": "creative"
        },
        "outputs": {}
    },
    {
        "inputs": {
            "job_name": "Customer Support Lead",
            "job_description": "Seeking a masculine male candidate under 30 with a commanding vocal presence to lead our late-night call shifts. Must handle scheduling, conflict mediation, and lead customer checkouts.",
            "difficulty": "junior",
            "num_goals": 3,
            "total_duration_minutes": 30,
            "domain_hint": "support"
        },
        "outputs": {}
    },
    {
        "inputs": {
            "job_name": "Futures Trader (Scalping Specialist)",
            "job_description": "Prop trading specialist role 100% focused on microsecond order book depth, execution slippage tracking, order queue positioning, and manual scalping of high-volume S&P 500 futures contracts.",
            "difficulty": "senior",
            "num_goals": 12,
            "total_duration_minutes": 90,
            "domain_hint": "finance"
        },
        "outputs": {}
    },
    {
        "inputs": {
            "job_name": "Creative Content Manager",
            "job_description": "Manage our brand content. Must edit video, design graphics, write articles, run email newsletters, audit SEO keyword rankings, run paid search campaigns, organize community webinars, script podcasts, and draft social copy.",
            "difficulty": "mid",
            "num_goals": 15,
            "total_duration_minutes": 30,
            "domain_hint": "creative"
        },
        "outputs": {}
    },
    {
        "inputs": {
            "job_name": "Junior Financial Analyst",
            "job_description": "Entry-level spreadsheet and billing helper. Must have managed a personal trading portfolio of at least $50 million with a documented annual return of 25%+ for the last decade.",
            "difficulty": "junior",
            "num_goals": 4,
            "total_duration_minutes": 60,
            "domain_hint": "finance"
        },
        "outputs": {}
    }
]


# --- Qualitative Pydantic Schema for LLM Judge Evaluator ---

class EdgeCaseCompliance(BaseModel):
    contradiction_flagged: Optional[Literal[True, False, "partial"]] = Field(default=None)
    discriminatory_content_excluded: Optional[Literal[True, False, "partial"]] = Field(default=None)
    vague_input_handled: Optional[Literal[True, False, "partial"]] = Field(default=None)
    narrow_topic_decomposed_not_padded: Optional[Literal[True, False, "partial"]] = Field(default=None)
    count_time_matched_or_explained: Optional[Literal[True, False, "partial"]] = Field(default=None)
    need_grounding_accurate: Literal[True, False, "partial"] = Field(description="Verify if the 'need_grounding' flag set on each goal is accurate.")

class PlannerEvaluationResult(BaseModel):
    relevance_score: int = Field(description="Qualitative relevance score (1-5).")
    relevance_justification: str = Field(description="Justification for relevance score.")
    coverage_score: int = Field(description="Qualitative coverage score (1-5).")
    coverage_justification: str = Field(description="Justification for coverage score.")
    ungrounded_goals: List[str] = Field(default_factory=list, description="Ungrounded goal IDs.")
    grounding_flag_justification: str = Field(description="Goal-by-goal statement of each need_grounding value and whether it's correct.")
    mislabeled_grounding_goals: List[str] = Field(default_factory=list, description="Goal IDs whose need_grounding flag was set incorrectly.")
    edge_case_compliance: EdgeCaseCompliance = Field(description="Qualitative edge case compliance ratings.")
    overall_notes: str = Field(description="Overall notes and critiques.")


# --- 1. Fixed Algorithmic Evaluator ---

def evaluate_planner_algorithmic(run, example) -> dict:
    """
    Evaluates target goal schema correctness and total duration matching.
    """
    inputs = example.inputs
    outputs = run.outputs
    
    target_count = inputs.get("num_goals", 5)
    target_duration = inputs.get("total_duration_minutes", 30)
    
    goals = outputs.get("goals", [])
    
    # A. Schema Validation Check
    schema_valid = True
    if not isinstance(goals, list):
        schema_valid = False
    else:
        required_keys = {"goal_id", "topic", "goal", "interview_time_in_minute"}
        for g in goals:
            if not isinstance(g, dict) or not required_keys.issubset(g.keys()):
                schema_valid = False
                break
                
    # B. Budget Checks
    actual_count = len(goals) if isinstance(goals, list) else 0
    actual_duration = sum(g.get("interview_time_in_minute", 0) for g in goals) if schema_valid else 0
    
    goal_count_adherence = 1.0 if actual_count == target_count else 0.0
    time_budget_adherence = 1.0 if actual_duration == target_duration else 0.0

    return {
        "results": [
            {"key": "schema_valid", "score": int(schema_valid)},
            {"key": "goal_count_adherence", "score": goal_count_adherence},
            {"key": "time_budget_adherence", "score": time_budget_adherence}
        ]
    }


# --- 2. Judgment-Based LLM Evaluator ---

def evaluate_planner_llm_judge(run, example) -> dict:
    """
    Invokes the qualitative LLM Judge to grade Relevance, Coverage, and compliance.
    """
    inputs = example.inputs
    outputs = run.outputs
    
    job_name = inputs.get("job_name", "Software Engineer")
    job_description = inputs.get("job_description", "")
    difficulty = inputs.get("difficulty", "infer")
    num_goals = inputs.get("num_goals", 5)
    total_duration_minutes = inputs.get("total_duration_minutes", 30)
    domain_hint = inputs.get("domain_hint", "auto")
    
    resolved_diff = outputs.get("difficulty", difficulty)
    goals = outputs.get("goals", [])
    meta = outputs.get("meta", {"assumptions": [], "warnings": []})
    
    # 1. Format the qualitative user prompt for the judge
    user_prompt = PLANNER_EVAL_USER_TEMPLATE.format(
        job_name=job_name,
        job_description=job_description,
        difficulty=difficulty,
        num_goals=num_goals,
        total_duration_minutes=total_duration_minutes,
        domain_hint=domain_hint,
        resolved_difficulty=resolved_diff,
        meta_json=json.dumps(meta, indent=2),
        goals_json=json.dumps(goals, indent=2)
    )
    
    messages = [
        SystemMessage(content=PLANNER_EVAL_SYSTEM_INSTRUCTION),
        HumanMessage(content=user_prompt)
    ]
    
    # 2. Invoke structured LLM judge
    try:
        structured_judge = gemini_flash_lite.with_structured_output(PlannerEvaluationResult)
        eval_result: PlannerEvaluationResult = structured_judge.invoke(messages)
        
        actual_compliance = eval_result.edge_case_compliance.model_dump()
        
        # Helper to convert literals (True, False, 'partial', None) into numeric scores for LangSmith UI
        def score_literal(val) -> Optional[float]:
            if val is True:
                return 1.0
            if val == "partial":
                return 0.5
            if val is False:
                return 0.0
            return None # null represents not applicable / skipped
            
        return {
            "results": [
                {"key": "relevance_score", "score": float(eval_result.relevance_score)},
                {"key": "coverage_score", "score": float(eval_result.coverage_score)},
                {"key": "contradiction_flagged", "score": score_literal(actual_compliance.get("contradiction_flagged"))},
                {"key": "discriminatory_content_excluded", "score": score_literal(actual_compliance.get("discriminatory_content_excluded"))},
                {"key": "vague_input_handled", "score": score_literal(actual_compliance.get("vague_input_handled"))},
                {"key": "narrow_topic_decomposed", "score": score_literal(actual_compliance.get("narrow_topic_decomposed_not_padded"))},
                {"key": "count_time_budget_qualitative", "score": score_literal(actual_compliance.get("count_time_matched_or_explained"))},
                {"key": "need_grounding_accurate", "score": score_literal(actual_compliance.get("need_grounding_accurate"))},
                {"key": "num_mislabeled_grounding_goals", "score": float(len(eval_result.mislabeled_grounding_goals))},
                {"key": "num_ungrounded_goals", "score": float(len(eval_result.ungrounded_goals))}
            ]
        }
    except Exception as e:
        sys.stderr.write(f"LLM Judge call failed in evaluator: {e}\n")
        return {
            "results": [
                {"key": "relevance_score", "score": 0.0},
                {"key": "coverage_score", "score": 0.0},
                {"key": "judge_failed", "score": 1.0}
            ]
        }


# --- 3. Experiment Target Function Wrapper ---

def evaluate_planner_target(inputs: dict) -> dict:
    """
    Target function wrapper for the LangSmith evaluate pipeline.
    """
    # Set up mock state input matching QuestionMakerState schema
    state = {
        "job_name": inputs.get("job_name", "Software Engineer"),
        "job_description": inputs.get("job_description", ""),
        "difficulty": inputs.get("difficulty", "infer"),
        "num_goals": inputs.get("num_goals", 5),
        "total_duration_minutes": inputs.get("total_duration_minutes", 30),
        "goals": None
    }
    
    # Execute the plan node
    output = plan_node(state)
    
    # Serialize goals objects into raw dictionaries for LangSmith storage
    goals_serialized = []
    if output.get("goals"):
        for g in output["goals"]:
            goals_serialized.append({
                "goal_id": g.goal_id,
                "topic": g.topic,
                "goal": g.goal,
                "interview_time_in_minute": g.interview_time_in_minute,
                "need_grounding": getattr(g, "need_grounding", None)
            })
            
    return {
        "goals": goals_serialized,
        "difficulty": output.get("difficulty"),
        "meta": output.get("meta", {"assumptions": [], "warnings": []})
    }


def main():
    print("=" * 60)
    print("Configuring LangSmith Evaluators and Dataset")
    print("=" * 60)
    
    dataset_name = "Planner Tuning Dataset"
    client = Client()
    
    # A. Check and create dataset if missing
    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
        print(f"Dataset '{dataset_name}' already exists in LangSmith.")
    except Exception:
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="Tuning and regression testing dataset for the technical interview planner node."
        )
        print(f"Created empty dataset '{dataset_name}' successfully.")
        
    # B. Auto-populate dataset examples if empty
    existing_examples = list(client.list_examples(dataset_id=dataset.id))
    if not existing_examples and DATASET_EXAMPLES:
        print(f"Uploading {len(DATASET_EXAMPLES)} examples to dataset '{dataset_name}'...")
        for example in DATASET_EXAMPLES:
            client.create_example(
                inputs=example["inputs"],
                outputs=example.get("outputs", {}),
                dataset_id=dataset.id
            )
        print("Upload complete.")
        
    print("\nEvaluators configured:")
    print("  1. Fixed Algorithmic Checks: schema_valid, goal_count_adherence, time_budget_adherence")
    print("  2. Judgment-Based LLM Checks: relevance_score, coverage_score, contradiction_flagged, vague_input_handled, discriminatory_content_excluded")
    
    print(f"\nTriggering evaluation on '{dataset_name}'...")
    print("Note: If the dataset is empty, this will complete immediately with 0 runs.")
    
    # C. Trigger LangSmith Evaluation
    results = evaluate(
        evaluate_planner_target,
        data=dataset_name,
        evaluators=[
            evaluate_planner_algorithmic,
            evaluate_planner_llm_judge
        ],
        experiment_prefix="planner-tuning-run"
    )
    
    print("\nEvaluation execution triggered successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
