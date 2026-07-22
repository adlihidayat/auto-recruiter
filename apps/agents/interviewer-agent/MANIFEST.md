# Interviewer Agent Manifest

This directory manages the live, real-time Interviewer Agent LangGraph workflow and its LLM-as-a-Judge evaluation infrastructure.

| File Name | Purpose | Key Exports/Dependencies |
| --- | --- | --- |
| `state.py` | State TypedDict and decision output Pydantic schemas | `InterviewerState`, `InterviewerDecision`, `Goal`, `PushbackTrigger` |
| `nodes/decide.py` | Core node deciding the turn-by-turn conversational action | `decideNextConversationalTurn` |
| `edges.py` | Conditional routing logic for 3-strike self-correction retries | `routeTurnDecisionOrRetry` |
| `graph.py` | LangGraph topology and node wiring | `graph` (compiled StateGraph object) |
| `GEMINI.md` | Persona, constitution, security protocols, and domain constraints | (None) |
| `prompts/system.py` | System prompt instructions and layer-2 security rules | `INTERVIEWER_SYSTEM_PROMPT` |
| `prompts/interviewer_eval_prompt.py` | Rubric and prompts for the LLM Judge (1-5 scoring) | `INTERVIEWER_EVAL_SYSTEM_INSTRUCTION`, `INTERVIEWER_EVAL_USER_TEMPLATE` |
| `scripts/debug_run.py` | Local CLI script for testing execution and LangSmith tracing | `debugInterviewerWorkflow` |
| `scripts/tune_interviewer_judge.py` | Calibration script comparing LLM Judge vs human expected scores | `executeJudgeCalibrationBenchmark`, `InterviewerEvaluationResult` |
| `scripts/test_interviewer_judge.py` | LangSmith Dataset & Experiment evaluation runner driving real graph decisions against 3D Judge | `Client`, `evaluate`, `EXTENDED_LIVE_TEST_CASES` |
| `tests/test_graph.py` | Pytest suite verifying graph compilation and state models | `test_graph_compiles`, `test_state_schema_validation` |
