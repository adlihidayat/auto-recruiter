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
| `evals/communication_eval.py` | Verification & Precision/Recall/Hallucination evaluator | `evaluate_communication()`, `verify_and_filter_extraction()` |
| `evals/datasets/communication_cases.py` | Ground truth test cases for Communication extraction evaluation | `ALL_COMMUNICATION_TEST_CASES` |
| `scripts/debug_run_citations.py` | Terminal runner for testing Call 3 Citation node | `run_citations_test()` |
| `scripts/test_communication_experiment.py` | LangSmith experiment runner for Communication Extraction | `run_experiment()` |
| `GEMINI.md` | Local constitution and rubric specifications | Local domain rules |
