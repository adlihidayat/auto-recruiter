# Interview Grader Agent Manifest

| File / Folder Name | Purpose | Key Exports / Dependencies |
| :--- | :--- | :--- |
| `state.py` | State schemas & Pydantic contracts | `GraderState`, `CoreAnalysisOutput`, `CommunicationOutput`, `EvidenceTally`, `CitationsOutput`, `FinalReport` |
| `graph.py` | StateGraph initialization & orchestration | `create_grader_graph()` |
| `edges.py` | Conditional routing functions | `route_after_core`, `route_after_comm` |
| `nodes/core_analysis.py` | Call 1 Core Analysis node execution | `run_core_analysis()` |
| `nodes/communication.py` | Call 2 Communication node execution | `run_communication()` |
| `nodes/citations.py` | Call 3 Citations node execution | `run_citations()` |
| `nodes/aggregation.py` | Aggregation pure code node | `run_aggregation()` |
| `prompts/core_analysis_prompt.py` | System & user prompts for Call 1 | `CORE_ANALYSIS_SYSTEM_PROMPT`, `CORE_ANALYSIS_USER_PROMPT` |
| `prompts/communication_prompt.py` | System & user prompts for Call 2 Communication node | `COMMUNICATION_SYSTEM_PROMPT`, `COMMUNICATION_USER_PROMPT` |
| `prompts/citations_prompt.py` | System & user prompts for Call 3 Citation node | `CITATIONS_SYSTEM_PROMPT`, `CITATIONS_USER_PROMPT` |
| `evals/schemas.py` | Evaluation & Meta-Judge Pydantic contracts | `ExpectedCoreAnalysisTruth`, `ExpectedCommunicationTruth`, `CommunicationJudgeEvalResult` |
| `evals/deterministic_eval.py` | Layer 1 Core Analysis Deterministic evaluator | `evaluate_deterministic()`, `scan_for_protected_characteristics()` |
| `evals/communication_deterministic_eval.py` | Layer 1 Communication Deterministic evaluator | `evaluate_communication_deterministic()` |
| `evals/prompts/core_analysis_judge_prompts.py` | Core Analysis LLM-as-a-Judge system & user prompts | `CORE_ANALYSIS_JUDGE_SYSTEM_PROMPT`, `CORE_ANALYSIS_JUDGE_USER_PROMPT` |
| `evals/prompts/communication_judge_prompts.py` | Communication LLM-as-a-Judge system & user prompts | `COMMUNICATION_JUDGE_SYSTEM_PROMPT`, `COMMUNICATION_JUDGE_USER_PROMPT` |
| `evals/core_analysis_judge_benchmark.py` | Meta-Judge evaluator for Core Analysis Judge | `evaluate_meta_judge()` |
| `evals/communication_judge_benchmark.py` | Meta-Judge evaluator for Communication Judge | `evaluate_communication_meta_judge()` |
| `evals/datasets/communication_judge_cases.py` | Human-calibrated 20 benchmark cases for Communication Judge | `ALL_COMMUNICATION_JUDGE_BENCHMARK_TEST_CASES` |
| `evals/run_eval.py` | CLI runner for Core Analysis node evals | `run_evaluation()` |
| `evals/run_communication_judge_benchmark.py` | CLI runner for Communication Meta-Judge calibration | `run_communication_judge_calibration()` |
| `scripts/debug_run_communication.py` | Terminal runner for testing Call 2 Communication node | `run_communication_test_case()` |
| `scripts/debug_run_citations.py` | Terminal runner for testing Call 3 Citation node | `run_citations_test()` |
| `scripts/test_communication_experiment.py` | LangSmith dataset & experiment runner for Communication | `main()` |
| `GEMINI.md` | Local constitution and rubric specifications | Local domain rules |
