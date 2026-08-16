# Backend Service — Architecture & Execution Protocol

## 0. Rule Cascade (Mid-Level Override)

This file extends the root `/GEMINI.md` with backend-specific behavioral rules.

- **Inheritance**: Apply all global rules (naming, docstrings, manifests, 3-strike verification) alongside these rules.
- **Scope**: Governs `apps/backend/` only. This is the hub of the system — it is the _only_ service `apps/frontend` talks to, the _only_ service that calls `question-maker-agent` and `interview-grader-agent`, and the only service with a general-purpose connection to Postgres. `apps/realtime-worker` also calls back into this service, but only for the narrow, non-hot-path actions defined in §1.

---

## 1. Tech Stack & Architectural Boundaries

- **Language**: Python 3.12+, strict type hints on all functions and variables.
- **Framework**: FastAPI + `uvicorn`, fully async (`async def` all the way down — no blocking DB or HTTP calls on the event loop).
- **Database**: PostgreSQL, self-hosted via Docker (no Supabase, no managed service assumed). Accessed through SQLAlchemy 2.0 (async engine, `asyncpg` driver) with Alembic migrations. Never hand-write raw SQL migrations outside Alembic; never mutate schema by hand against a running container.
- **Validation / schemas**: `pydantic` v2. Payload shapes that cross a service boundary (`Goal`, `QuestionSuite`, `InterviewSession`, grader report models, guard verdict models) come from `packages/shared-schemas` — never redefined locally. Models that are purely internal to this service's own persistence (ORM row shapes, internal job records) stay local to `apps/backend`.
- **Auth (HR users)**: self-rolled, no third-party provider. Argon2 password hashing, short-lived JWT access token + longer-lived refresh token, both delivered as httpOnly, `SameSite=Strict` cookies. No Google/OAuth — the goal is that cloning the repo and running `docker compose up` never requires registering an OAuth app.
- **Auth (candidates)**: no accounts. A candidate's meeting link embeds an HMAC-signed token (`interview_id` + `candidate_id` + `exp`, signed with a server-side secret) generated when the plan finishes. Verifying this token is this service's job, not the worker's — the worker asks this service "is this session allowed to start," it never validates the signature itself.
- **Email**: SMTP via `aiosmtplib`, configured entirely through env vars (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`). In local/dev `docker-compose`, these point at the bundled **Mailpit** container by default, so candidate invite emails are visible in Mailpit's web UI without any real credentials. Production just overrides the env vars — same code path, no SDK swap.
- **Background jobs — Postgres-backed, no Redis/Celery/arq.** Anything that must survive the triggering HTTP request (plan generation, grading) is written as a row in a `jobs` table (`status: pending | processing | done | failed`, `job_type`, `payload`, `attempts`, `last_error`) inside the same transaction that creates the parent record. A job is picked up two ways: (1) an in-process `asyncio.create_task` fired immediately after commit, for the common case of "start it right now"; (2) a periodic reconciliation sweep (every N seconds, one query) that requeues anything stuck in `processing` past a timeout — this is what makes it safe across a crash or restart without needing a separate broker.
- **HTTP clients to agents**: a thin typed client per agent (`clients/question_maker_client.py`, `clients/grader_client.py`) wrapping `httpx.AsyncClient`, calling `apps/agents`' FastAPI serving layer. This service never calls `interviewer-agent` — that agent is exclusively invoked in-process by `apps/realtime-worker` per the agents' own architecture doc.
- **LiveKit**: this service is the only one holding LiveKit server API credentials. It issues short-lived room-join tokens to `apps/frontend` (HR observing/joining) and to the room itself (or to the worker's dispatch mechanism) — never leaks the server API secret past this boundary.

### Dependency Boundaries (restated for this service)

- `apps/frontend` → `apps/backend` only, over HTTP/JSON.
- `apps/backend` → `apps/agents` (`question-maker-agent`, `interview-grader-agent`) only, over HTTP, via the FastAPI serving layer those agents expose. Never `interviewer-agent` — that's the worker's in-process dependency, not this service's.
- `apps/realtime-worker` → `apps/backend`, but **only** for: (a) fetching the interview plan / candidate session validity at call start, (b) persisting a checkpoint when a goal completes, (c) reporting final interview state when the call ends. Live, turn-by-turn decisions never round-trip through this service — that would reintroduce the latency the worker's in-process agent call is specifically designed to avoid.
- This service → Postgres directly. No other service touches the database.

---

## 2. Code Style & Domain Behavior

### Layering

- **`api/` (routers)** — HTTP concerns only: parse request, call a service, return a response. No business logic, no direct DB queries here.
- **`services/`** — business logic and orchestration (`interview_service.py`, `plan_service.py`, `grading_service.py`, `email_service.py`). This is where "create interview → 202 → background plan job" and "goal checkpoint → persist → check if all goals done → maybe trigger grading job" live.
- **`repositories/`** — the only layer allowed to write SQLAlchemy queries, one repository per aggregate (`interview_repo.py`, `candidate_repo.py`, `goal_repo.py`, `job_repo.py`). Services depend on repositories, never on the ORM session directly.
- **`jobs/`** — background job bodies (`generate_plan_job.py`, `grade_interview_job.py`) and the runner/dispatcher. A job body is a plain async function; it must be safe to re-run if it crashes partway (idempotent writes, or a status check at the top before doing expensive work again).

### The Pre-Interview Flow (create → plan → notify)

This is the flow the frontend's "New Interview" form triggers, and it must never make the HR user wait on an LLM call:

1. `POST /interviews` validates the form payload (interview info, date, candidate list), writes the `interview` row plus one `candidate` row per invitee with status `pending_plan`, enqueues a `generate_plan` job row in the same transaction, commits, and returns `202` with the new `interview_id` immediately. The frontend closes the form and shows the interview in the dashboard list with a "Generating plan…" status — it does not poll-block or spinner-wait on this endpoint.
2. The `generate_plan` job (fired via `asyncio.create_task` right after the commit) calls `question-maker-agent` through `clients/question_maker_client.py`, passing the raw interview info. This is where the raw JD/interview-info text becomes untrusted input the moment it crosses into the agent call — this service does not need to sanitize it itself (the agent's own injection defenses handle that), but it must not trust the agent's `references` field blindly either: if the agent's contract says empty array on no verified retrieval, treat a non-empty array as data to store, not as something this service re-validates.
3. On success: persist the returned `QuestionSuite` (goals, each with its own `passing_criteria`/`pushback_triggers`/`wrong_answer_signals`/`grounding_theory`), flip the interview to `scheduled`, generate each candidate's signed room-link token, and enqueue (or directly send, given it's cheap) the invite email via `email_service.py`.
4. On failure (including exhausting the agent's own 3-retry limit and erroring back to this service): mark the interview `failed_plan_generation` with `last_error` populated, and surface that clearly in the dashboard — never leave an interview silently stuck in `generating_plan`.
5. **`weight`, `gating`, and `communication_weight` are set here, not by any agent.** Per the grader agent's own boundary doc, these are a human judgment call. If the create-interview form doesn't yet collect them, default every goal to `weight: 1, gating: false` and the plan to `communication_weight: "low"` — but treat this as a placeholder to build real UI for, not a permanent decision.

### Room Access Gating

- The LiveKit token endpoint (`api/v1/livekit.py`) must reject a join attempt if the current time is before the interview's scheduled date, or if the candidate's signed token is expired/invalid/already used to complete an interview. "The room opens on the date" is enforced here, server-side — never trust a client-side countdown as the actual gate.

### Worker Callback Endpoints

- `POST /internal/sessions/{candidate_id}/checkpoint` — called by the worker when a goal finishes (`action: advance`). Body includes the goal's clean interaction history (`role` + `content` only) for grading, plus the raw per-turn interviewer-agent decisions (`action`, `reasoning`, `trigger_matched`, `flag_for_human_review`) for audit/alerting. **Persist both, but keep them in separate tables/columns** — the clean transcript is what `interview-grader-agent` reads later; the raw log is for HR audit and for reacting to `flag_for_human_review: true` (e.g. surfacing a live alert). Never let the raw log leak into what the grader receives — that agent's contract explicitly assumes it never sees the interviewer's internal fields.
- `POST /internal/sessions/{candidate_id}/complete` — called by the worker when the interview ends (`action: stop_interview`, no more goals). Marks the candidate `interview_completed`, and this is the trigger point for grading — enqueue a `grade_interview` job here. The worker's responsibility ends at reporting completion; it does not call the grader itself.
- These endpoints are internal (worker-to-backend), not part of the public API surface the frontend uses — protect them with a service-level credential (e.g. a shared secret header), not the HR JWT scheme.

### The Grading Flow

- The `grade_interview` job assembles the `interview-grader-agent` input contract exactly as documented in that agent's spec: job context, plan-level metadata, and the full per-goal `interaction_history` already segmented by `goal_id` (which this service produced incrementally via the checkpoint endpoint above — no last-minute stitching needed).
- On success, persist the `FinalReport` (composite score, recommendation, reasoning, `red_flags`, audit metadata) against the candidate, and flip candidate status to `graded`. This is what powers the candidate-report popup on the frontend.
- On failure after the agent's own retry budget: mark `failed_grading`, keep the raw transcript intact, and make it visible to HR as needing manual review rather than silently dropping the candidate from the report list.

### Status Model (drives the dashboard)

- **Interview-level**: `generating_plan → scheduled → failed_plan_generation`. (Interview-level status only tracks the plan pipeline — it does not try to represent "in progress," since that's inherently per-candidate.)
- **Candidate-level**: `pending_plan → invited → ready → in_progress → interview_completed → grading → graded → failed_grading`. The dashboard's list/detail popup reads candidate-level status for its per-candidate badges, and rolls them up for the interview's summary badge (e.g. "3/5 graded").

---

## 3. Directory Tree & Structure

```text
apps/backend/
├── src/
│   └── app/
│       ├── main.py                    # FastAPI app factory, lifespan (DB pool, http clients, job sweep)
│       ├── core/
│       │   ├── config.py              # pydantic-settings; all env vars, incl. SMTP/DB/JWT/LiveKit secrets
│       │   ├── security.py            # JWT issue/verify, password hashing, candidate signed-URL HMAC
│       │   └── db.py                  # async SQLAlchemy engine + session factory
│       ├── api/
│       │   ├── deps.py                # current_user dep, internal-service-auth dep
│       │   └── v1/
│       │       ├── auth.py            # login, refresh, logout
│       │       ├── interviews.py      # create/list/detail
│       │       ├── candidates.py      # candidate report retrieval
│       │       ├── livekit.py         # token issuance, room-access gating
│       │       └── internal/
│       │           └── sessions.py    # worker callback endpoints (checkpoint, complete)
│       ├── models/                    # SQLAlchemy ORM models (local persistence shape)
│       ├── schemas/                   # request/response pydantic models; re-exports shared-schemas where applicable
│       ├── services/
│       │   ├── interview_service.py
│       │   ├── plan_service.py
│       │   ├── grading_service.py
│       │   └── email_service.py
│       ├── repositories/
│       │   ├── interview_repo.py
│       │   ├── candidate_repo.py
│       │   ├── goal_repo.py
│       │   └── job_repo.py
│       ├── jobs/
│       │   ├── runner.py              # asyncio dispatch + reconciliation sweep
│       │   ├── generate_plan_job.py
│       │   └── grade_interview_job.py
│       └── clients/
│           ├── question_maker_client.py
│           ├── grader_client.py
│           └── livekit_client.py
├── migrations/                        # Alembic
├── tests/
├── pyproject.toml
├── Dockerfile
├── .env.example                       # documents every required var; only GOOGLE_API_KEY has no local default
└── GEMINI.md                          # this file
```
