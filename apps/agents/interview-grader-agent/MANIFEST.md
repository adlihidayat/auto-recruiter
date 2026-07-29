# Interview Grader Agent Manifest

| File / Folder Name | Purpose | Key Exports / Dependencies |
| :--- | :--- | :--- |
| `state.py` | State schemas & Pydantic contracts | `GraderState`, `CoreAnalysisOutput`, `CommunicationOutput`, `CitationsOutput`, `FinalReport` |
| `graph.py` | StateGraph initialization & orchestration | `create_grader_graph()` |
| `edges.py` | Conditional routing functions | `route_after_core`, `route_after_comm` |
| `nodes/core_analysis.py` | Call 1 Core Analysis node execution | `run_core_analysis()` |
| `nodes/communication.py` | Call 2 Communication node execution | `run_communication()` |
| `nodes/citations.py` | Call 3 Citations node execution | `run_citations()` |
| `nodes/aggregation.py` | Aggregation pure code node | `run_aggregation()` |
| `prompts/core_analysis_prompt.py` | System & user prompts for Call 1 | `CORE_ANALYSIS_SYSTEM_PROMPT`, `CORE_ANALYSIS_USER_PROMPT` |
| `evals/schemas.py` | Evaluation & Meta-Judge Pydantic contracts | `ExpectedCoreAnalysisTruth`, `DeterministicEvalResult`, `LLMJudgeEvalResult`, `ExpectedJudgeTruth` |
| `evals/deterministic_eval.py` | Layer 1 Deterministic evaluator (pure code) | `evaluate_deterministic()`, `scan_for_protected_characteristics()` |
| `evals/prompts/judge_prompts.py` | LLM-as-a-Judge system & user prompts | `CORE_ANALYSIS_JUDGE_SYSTEM_PROMPT`, `CORE_ANALYSIS_JUDGE_USER_PROMPT` |
| `evals/llm_judge_eval.py` | Layer 2 LLM-as-a-Judge evaluator | `evaluate_llm_judge()` |
| `evals/judge_benchmark.py` | Meta-Judge evaluator for calibrating Judge | `evaluate_meta_judge()` |
| `evals/datasets/core_analysis_cases.py` | Test cases with ground truth labels | `ALL_CORE_ANALYSIS_TEST_CASES` |
| `evals/datasets/judge_benchmark_cases.py` | Human-calibrated test cases for Judge | `ALL_JUDGE_BENCHMARK_TEST_CASES` |
| `evals/run_eval.py` | CLI runner for Core Analysis node evals | `run_evaluation()` |
| `evals/run_judge_benchmark.py` | CLI runner for Meta-Judge calibration | `run_judge_calibration()` |
| `scripts/debug_run.py` | Terminal runner for testing graph execution | `main()` |
| `scripts/test_core_analysis_experiment.py` | LangSmith dataset & experiment runner for Core Analysis | `main()` |
| `GEMINI.md` | Local constitution and rubric specifications | Local domain rules |
