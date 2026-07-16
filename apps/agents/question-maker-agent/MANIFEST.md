# Question-Maker Agent Manifest

This directory manages the Question-Maker Agent LangGraph workflow.

| File Name | Purpose | Key Exports/Dependencies |
| --- | --- | --- |
| `state.py` | State TypedDict and output Pydantic schemas | `QuestionMakerState`, `QuestionSuite`, `QuestionItem` |
| `graph.py` | LangGraph topology and routing definitions | `graph` (compiled StateGraph object) |
| `GEMINI.md` | Persona, constitution, security protocols, and target schemas | (None) |
| `prompts/planner_eval_prompt.py` | Prompt templates and scoring anchors for qualitative judge | `PLANNER_EVAL_SYSTEM_INSTRUCTION`, `PLANNER_EVAL_USER_TEMPLATE` |
| `scripts/test_judge.py` | Local script to run the LLM Judge against mock scenarios | (None) |
| `scripts/run_planner_experiment.py` | Script to run experiments and evaluators on LangSmith | `evaluate_planner_target`, `evaluate_planner_algorithmic`, `evaluate_planner_llm_judge` |
