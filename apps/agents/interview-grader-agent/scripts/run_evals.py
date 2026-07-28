"""
What: CLI entrypoint for running the Core Analysis evaluation framework.
Why: Allows running deterministic checks and LLM-as-judge prompt evaluations across all test cases.
Boundaries: CLI wrapper script only.
"""

import sys
import os
import argparse
from dotenv import load_dotenv

# Setup paths for monorepo structure so importlib can find the packages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

def main():
    # Load .env
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
    load_dotenv(env_path)

    # Map user's specific key names to the standard LangChain expected names
    if "GEMINI_API_KEY1" in os.environ and "GEMINI_API_KEY" not in os.environ:
        os.environ["GEMINI_API_KEY"] = os.environ["GEMINI_API_KEY1"]
    if "LANGSMITH_API_KEY" in os.environ and "LANGCHAIN_API_KEY" not in os.environ:
        os.environ["LANGCHAIN_API_KEY"] = os.environ["LANGSMITH_API_KEY"]

    parser = argparse.ArgumentParser(description="Core Analysis Evaluation Runner")
    parser.add_argument("--case", type=str, default=None, help="Filter by specific case_id substring")
    parser.add_argument("--no-judge", action="store_true", help="Skip LLM Judge evaluation (run deterministic checks only)")

    args = parser.parse_args()

    # Import runner after path setup and env loading
    from evals.runner import run_evaluation_suite

    run_evaluation_suite(
        filter_case_id=args.case,
        include_judge=not args.no_judge,
        verbose=True,
    )

if __name__ == "__main__":
    main()
