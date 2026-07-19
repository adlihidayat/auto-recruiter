# Question-Maker Agent Manifest

This directory manages the Question-Maker Agent LangGraph workflow.

| File Name | Purpose | Key Exports/Dependencies |
| --- | --- | --- |
| `state.py` | State TypedDict and output Pydantic schemas | `QuestionMakerState`, `QuestionSuite`, `QuestionItem` |
| `nodes/planner.py` | Main planner node extracting goals and metadata | `plan_node` |
| `nodes/retriever.py` | Retriever ReAct subgraph for gathering theory via Tavily search | `retriever_generator_subgraph` |
| `nodes/generator.py` | Generator node for mapping theories and goals into QuestionItems | `generateQuestionItemFromGoal` |
| `nodes/validate.py` | Validator node acting as Layer 1 and Layer 2 quality control | `validateQuestionSuite` |
| `graph.py` | LangGraph topology and routing definitions | `graph` (compiled StateGraph object) |
| `GEMINI.md` | Persona, constitution, security protocols, and target schemas | (None) |
| `prompts/planner_prompt.py` | Prompt templates and instructions for the main planner LLM | `PLANNER_SYSTEM_INSTRUCTION`, `PLANNER_USER_TEMPLATE` |
| `prompts/retriever_prompt.py` | Prompt templates and instructions for the Retriever ReAct agent | `RETRIEVER_SYSTEM_INSTRUCTION`, `FORCED_GENERATION_INSTRUCTION` |
| `prompts/generator_prompt.py` | Prompt templates and instructions for the Generator LLM | `GENERATOR_SYSTEM_INSTRUCTION` |
| `prompts/planner_eval_prompt.py` | Prompt templates and scoring anchors for qualitative judge | `PLANNER_EVAL_SYSTEM_INSTRUCTION`, `PLANNER_EVAL_USER_TEMPLATE` |
| `prompts/retriever_eval_prompt.py` | Prompt templates and 0-5 scoring rubric for the Retriever LLM Judge | `RETRIEVER_EVAL_SYSTEM_INSTRUCTION`, `RETRIEVER_EVAL_USER_TEMPLATE` |
| `scripts/test_judge.py` | Local script to run the Planner LLM Judge against mock scenarios | (None) |
| `scripts/test_retriever_judge.py` | Local script to run the Retriever LLM Judge against mock scenarios | (None) |
| `scripts/run_planner_experiment.py` | Script to run experiments and evaluators on LangSmith | `evaluate_planner_target`, `evaluate_planner_algorithmic`, `evaluate_planner_llm_judge` |
