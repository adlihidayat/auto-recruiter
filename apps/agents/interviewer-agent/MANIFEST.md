# Interviewer Agent Manifest

This directory manages the live, real-time Interviewer Agent LangGraph workflow.

| File Name | Purpose | Key Exports/Dependencies |
| --- | --- | --- |
| `state.py` | State TypedDict and decision output Pydantic schemas | `InterviewerState`, `InterviewerDecision`, `Goal`, `PushbackTrigger` |
| `nodes/decide.py` | Core node deciding the turn-by-turn conversational action | `decideNextConversationalTurn` |
| `edges.py` | Conditional routing logic for 3-strike self-correction retries | `routeTurnDecisionOrRetry` |
| `graph.py` | LangGraph topology and node wiring | `graph` (compiled StateGraph object) |
| `GEMINI.md` | Persona, constitution, security protocols, and domain constraints | (None) |
| `prompts/system.py` | System prompt instructions and layer-2 security rules | `INTERVIEWER_SYSTEM_PROMPT` |
| `scripts/debug_run.py` | Local CLI script for testing execution and LangSmith tracing | `debugInterviewerWorkflow` |
| `tests/test_graph.py` | Pytest suite verifying graph compilation and state models | `test_graph_compiles`, `test_state_schema_validation` |
