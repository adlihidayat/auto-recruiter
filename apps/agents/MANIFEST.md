# Agents Service Manifest

| File Path | Purpose | Key Exports / Dependencies |
| :--- | :--- | :--- |
| `main.py` | FastAPI Microservice Entrypoint for Agent Execution | `app` |
| `question-maker-agent/` | Technical question generator agent | LangGraph workflow |
| `interviewer-agent/` | Live interview participant agent | LiveKit worker logic |
| `interview-grader-agent/` | Post-interview grading agent | Evaluation workflow |
| `shared/` | Shared clients & utilities across agents | `gemini_flash_lite`, `gemini_flash`, `gemini_pro` |
