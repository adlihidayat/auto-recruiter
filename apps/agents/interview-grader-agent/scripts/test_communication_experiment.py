"""
What: CLI & LangSmith experiment runner for Communication Extraction prompt evaluations.
Why: Runs benchmark test cases against the LLM, verifies evidence, and measures precision, recall, and hallucination rate.
Boundaries: Local test runner and LangSmith evaluator integration.
"""
import os
import json
import asyncio
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client, traceable

from ..evals.datasets.communication_cases import ALL_COMMUNICATION_TEST_CASES
from ..evals.communication_eval import evaluate_communication
from ..nodes.communication import COMMUNICATION_RUBRIC
from ..state import CommunicationExtraction
from apps.agents.shared.clients import gemini_flash_lite

DATASET_NAME = "communication_prompt_eval_dataset"

structured_llm_client = gemini_flash_lite.with_structured_output(CommunicationExtraction)

@traceable(name="CommunicationExtractionEvaluator")
def run_llm_extraction(transcript: list) -> CommunicationExtraction:
    """Executes the Communication LLM Extraction chain on a given transcript."""
    from ..prompts.communication_prompt import (
        COMMUNICATION_SYSTEM_PROMPT,
        COMMUNICATION_USER_PROMPT
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", COMMUNICATION_SYSTEM_PROMPT),
        ("user", COMMUNICATION_USER_PROMPT)
    ])

    chain = prompt | structured_llm_client

    transcript_json = json.dumps(transcript, indent=2)
    rubric_json = json.dumps(COMMUNICATION_RUBRIC, indent=2)

    return chain.invoke({
        "job_context": "Role: Senior Backend Engineer\nDescription: Microservice architecture over gRPC and Go.",
        "plan_meta": "Difficulty: senior\nCommunication Weight: medium",
        "transcript": transcript_json,
        "rubric": rubric_json
    })


def run_experiment():
    """Runs the benchmark suite locally and logs metrics."""
    print("=" * 80)
    print("STARTING COMMUNICATION EXTRACTION EXPERIMENT")
    print("=" * 80)

    # Sync to LangSmith if API key is present
    ls_client = None
    if os.environ.get("LANGCHAIN_API_KEY"):
        try:
            ls_client = Client()
            print(f"Connected to LangSmith. Syncing dataset: '{DATASET_NAME}'...")
            if not ls_client.has_dataset(dataset_name=DATASET_NAME):
                dataset = ls_client.create_dataset(
                    dataset_name=DATASET_NAME,
                    description="Ground truth benchmark dataset for Communication Extraction evaluation"
                )
                for case in ALL_COMMUNICATION_TEST_CASES:
                    ls_client.create_example(
                        inputs={"transcript": case["transcript"]},
                        outputs={"answer_key": case["answer_key"]},
                        metadata={"case_id": case["case_id"], "notes": case["notes"]},
                        dataset_id=dataset.id
                    )
                print(f"Created dataset '{DATASET_NAME}' with {len(ALL_COMMUNICATION_TEST_CASES)} examples.")
            else:
                print(f"Dataset '{DATASET_NAME}' already exists on LangSmith.")
        except Exception as e:
            print(f"Warning: Could not sync with LangSmith: {e}")

    results = []
    
    total_precisions = []
    total_recalls = []
    total_hallucinations = []

    for case in ALL_COMMUNICATION_TEST_CASES:
        case_id = case["case_id"]
        transcript = case["transcript"]
        answer_key = case["answer_key"]

        print(f"\nEvaluating Case: '{case_id}'...")
        
        # 1. Run LLM Extraction
        extraction = run_llm_extraction(transcript)
        
        # 2. Evaluate & Filter
        eval_res = evaluate_communication(transcript, extraction, answer_key)
        results.append((case_id, eval_res))

        total_precisions.append(eval_res["overall_precision"])
        total_recalls.append(eval_res["overall_recall"])
        total_hallucinations.append(eval_res["hallucination_rate"])

        print(f"  -> Precision: {eval_res['overall_precision']:.2%}")
        print(f"  -> Recall:    {eval_res['overall_recall']:.2%}")
        print(f"  -> Hallucination Rate (Dropped Quotes): {eval_res['hallucination_rate']:.2%} ({eval_res['total_dropped']}/{eval_res['total_extracted']})")

    # Print Summary Table
    avg_precision = sum(total_precisions) / len(total_precisions) if total_precisions else 0.0
    avg_recall = sum(total_recalls) / len(total_recalls) if total_recalls else 0.0
    avg_hallucination = sum(total_hallucinations) / len(total_hallucinations) if total_hallucinations else 0.0

    print("\n" + "=" * 80)
    print("COMMUNICATION EXPERIMENT SUMMARY REPORT")
    print("=" * 80)
    print(f"Total Benchmark Cases: {len(ALL_COMMUNICATION_TEST_CASES)}")
    print(f"Average Precision:          {avg_precision:.2%}")
    print(f"Average Recall:             {avg_recall:.2%}")
    print(f"Average Hallucination Rate: {avg_hallucination:.2%}")
    print("=" * 80)

if __name__ == "__main__":
    run_experiment()
