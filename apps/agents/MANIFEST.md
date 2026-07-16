# Agents Service Manifest

This directory manages the AI agent service.

| File Name | Purpose | Key Exports/Dependencies |
| --- | --- | --- |
| `requirements.txt` | Python service package dependencies | `langgraph`, `langsmith`, `fastapi`, `pydantic`, etc. |
| `shared/clients.py` | Central initialization for Gemini LLM models | `gemini_flash_lite`, `gemini_flash`, `gemini_pro` |
| `shared/tracing.py` | Observability configurations for LangSmith | `traceable`, `verify_tracing_setup` |
| `interview-grader-agent/` | Grader agent logic & rules | (Internal package) |
| `interviewer-agent/` | Live conversational agent | (Internal package) |
| `question-maker-agent/` | Technical question generator agent | (Internal package) |
