# AI Agent Service Architecture & Execution Protocol

## 0. Rule Cascade (Mid-Level Override)

This file extends the root `/GEMINI.md` with Python-specific and AI-specific behavioral rules.

- **Inheritance**: Apply all global rules (naming, docstrings, manifests, 3-strike verification) alongside these rules.
- **Child Overrides**: Subdirectories (e.g., `interview-grader-agent/`) contain domain-specific `GEMINI.md` files that govern their specific prompts, rubrics, and workflows. Those local rules override general instructions found here.

---

## 1. Tech Stack & Architectural Boundaries

This application is a standalone Python microservice responsible for orchestrating agentic AI workflows. It exposes endpoints to be consumed **solely** by `apps/backend`. Never attempt to communicate directly with `apps/frontend`.

- **Language**: Python 3.12+ (Strict type hinting required on all functions and variables).
- **Agent Framework**: `langgraph` (Stateful, cyclical, multi-actor workflows).
- **Observability & Tracing**: `langsmith` (Mandatory step-by-step tracing).
- **Serving Layer**: `fastapi` + `uvicorn` (For exposing agent execution endpoints to the core backend).
- **Data Validation**: `pydantic` v2 (For all payload schemas, LLM structured outputs, and environment variables).

---

## 2. Code Style & LangGraph Behavior

When building or modifying agent workflows, adhere strictly to the following framework best practices:

### LangGraph Best Practices

- **Strict State Schemas**: Never use untyped `dict` objects for LangGraph state. All graph states must be explicitly defined using `TypedDict` or Pydantic models with clear field annotations.
- **Node Purity**: Graph nodes must be written as modular, isolated functions that accept a `State` object and return a state update dictionary. Do not mutate global variables inside nodes.
- **Conditional Edges**: Keep routing logic clean. If a node requires dynamic routing (e.g., determining if a candidate passed or failed), extract the routing logic into a dedicated, well-named routing function.

### LangSmith Observability & Tracing

- **Trace Everything**: Ensure LangSmith tracing is active by default. Every LangGraph compilation and execution must automatically report traces to the workspace project.
- **Node-Level Metadata**: When creating custom tools or complex helper functions inside an agent, wrap them with LangChain's `@traceable` decorator so inputs, outputs, and latency are logged in LangSmith.
- **No Silent LLM Failures**: Wrap LLM invocations in try/except blocks with fallback logic or explicit error bubbling. Never let an API rate limit or context-length error crash the FastAPI server silently.

---

## 3. Directory Tree & Shared Infrastructure

```text
apps/agents/
├── shared/                   # Core utilities shared across all agents
│   ├── clients.py            # Initialized LLM clients (OpenAI, Gemini, etc.)
│   ├── tracing.py            # LangSmith configuration and wrappers
│   └── tools/                # Reusable agent tools (e.g., resume_parser, db_reader)
├── api/                      # FastAPI server setup and route definitions
│   └── server.py             # Main entrypoint exposing agent endpoints
├── interview-grader-agent/   # Evaluates transcripts against job rubrics
│   ├── graph.py              # LangGraph state machine definition
│   ├── nodes.py              # Individual execution steps
│   └── GEMINI.md             # Local domain rules & scoring schemas
├── interviewer-agent/        # Real-time/async conversational interviewer
│   └── GEMINI.md             # Local domain rules & persona instructions
├── question-maker-agent/     # Generates tailored technical questions
│   └── GEMINI.md             # Local domain rules & difficulty scaling
├── pyproject.toml            # Python dependency management (Poetry/uv/pip)
├── .env                      # environment variable
└── GEMINI.md                 # This file (AI Service middleware rules)
```

### Standard Agent Sub-Directory Structure

Every individual agent inside `apps/agents/` must strictly follow this modular LangGraph file architecture to prevent file bloat:

```
<agent-name>/
├── state.py          # Pydantic schemas & TypedDicts for Graph State
├── graph.py          # StateGraph initialization, node wiring, and compilation
├── edges.py          # Conditional routing functions
├── nodes/            # Directory for discrete execution steps
├── prompts/          # Directory for system prompts and templates
├── tools/            # Localized tools (ONLY if unique to this agent)
├── scripts/          # Standalone CLI runners and LangSmith eval scripts
│   └── debug_run.py  # Quick terminal script to test graph execution
├── tests/            # Localized pytest suites for this specific graph
│   └── test_graph.py # Unit tests for node schemas and routing logic
└── GEMINI.md         # Localized agent constitution and schemas
```
