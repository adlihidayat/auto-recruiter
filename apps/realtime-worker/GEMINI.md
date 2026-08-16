# Realtime Worker — Architecture & Execution Protocol

## 0. Rule Cascade (Mid-Level Override)

This file extends the root `/GEMINI.md` with worker-specific behavioral rules.

- **Inheritance**: Apply all global rules (naming, docstrings, manifests, 3-strike verification) alongside these rules.
- **Scope**: Governs `apps/realtime-worker/` only. This service owns the live portion of an interview end to end: joining the LiveKit room, running STT/TTS, calling `interviewer-agent` turn by turn, enforcing its own guardrails over that agent's recommendations, and reporting outcomes back to `apps/backend`. It does not grade, does not generate the interview plan, and does not talk to the frontend directly.

---

## 1. Tech Stack & Architectural Boundaries

- **Language**: Python 3.12+, strict type hints on all functions and variables.
- **Framework**: `livekit-agents` (LiveKit Agents SDK). This is a long-running worker process (`livekit-agents` CLI entrypoint), not a request/response server — there is no FastAPI here, and there must not be one on the hot path (see the exception below).
- **Voice pipeline**: Silero VAD (local, no API key) for turn-taking; Google STT + Google TTS as the default plugin pair, reusing the same `GOOGLE_API_KEY` already required for the LLM calls, so this service does not introduce a new required credential. The plugin choice is swappable via LiveKit's plugin architecture if that default changes later — treat it as configuration, not a hardcoded assumption baked into business logic.
- **The one in-process, non-HTTP dependency**: this service imports `interviewer-agent` (and `shared/clients.py`, `shared/tracing.py`, `shared/safety/regex_denylist.py`, `shared/safety/injection_classifier.py`) directly from `apps/agents` as a plain Python package — invoked in-process, never over HTTP. This is the documented exception in the agents' own architecture doc, and it exists because this worker is on the hot path of a live voice call; an HTTP hop per turn would add latency that breaks real-time conversation.
  - **This requires workspace-aware Python dependency management.** A plain `pip install -r requirements.txt` cannot express "depend on a sibling package by local path." Use a `uv` workspace (root `pyproject.toml` with `[tool.uv.workspace] members = ["apps/agents", "apps/realtime-worker", ...]`) so `apps/realtime-worker`'s `pyproject.toml` can declare `apps-agents` as a workspace path dependency and get live, non-published code.
  - Because of this import, this service inherits `interviewer-agent`'s constraint: the agent package's core logic has zero dependency on `fastapi`/`uvicorn`. Never route a live-turn call through `apps/agents`' `api/server.py` — that FastAPI wrapper is explicitly for non-realtime manual testing only.
- **Data validation**: `pydantic` v2, using the same shared payload shapes as everywhere else. The interviewer-agent's input/output contracts (`goal`, `next_goal`, `goal_history`, etc.) come from `packages/shared-schemas` or the agent package itself — never redefined locally with slightly different field names.
- **Observability**: `langsmith` tracing carries through from the in-process agent call, per the agent's own "trace everything, including retries and terminal failures" rule. This service must not swallow or short-circuit that tracing just because it's not the one making the LLM call directly.

### Dependency Boundaries (restated for this service)

- `apps/realtime-worker` → `apps/agents` (`interviewer-agent` package only, plus its `shared/` utilities): **in-process import**, not HTTP.
- `apps/realtime-worker` → `apps/backend`: HTTP, and **only** for the three non-hot-path actions in §2 (fetch session context at start, checkpoint on goal completion, report final state on call end). Every other decision this service makes during the call is made locally, with no round-trip.
- `apps/realtime-worker` ↔ `apps/frontend`: never direct. The frontend connects to LiveKit media infrastructure itself using a token `apps/backend` issued; this service and the frontend never call each other's APIs.
- This service does not touch Postgres directly. All persistence goes through `apps/backend`'s callback endpoints.

---

## 2. Code Style & Session Behavior

### Ownership: Timers, Turn Counts, Persistence

Per `interviewer-agent`'s own contract, it holds no memory and has no authority over timing or persistence — that authority belongs entirely to this service. Concretely:

- **`InterviewSessionState`** (in `session/interview_session.py`) is the single source of truth for the live call: current `goal_id`, `goal_history` for the active goal, `prior_goals_summary`, `turn_count_this_goal`, `time_elapsed_seconds_this_goal`, `global_time_elapsed_seconds`, and the full ordered goal list fetched at session start. It lives in memory for the duration of the call and is what gets serialized into each `interviewer-agent` call's input contract.
- **The agent's output is a recommendation, not a command.** Before executing `action: advance` or `action: stop_interview`, this service validates it against its own guardrails — e.g. a minimum number of turns asked for the current goal, a maximum call duration — in `session/guardrails.py`. If the agent recommends advancing before the guardrail's minimum is met, override it (e.g. force one more `next_question`/`pushback`-equivalent turn) rather than blindly executing the recommendation.

### Session Lifecycle

1. **Room join / dispatch**: when a candidate joins the LiveKit room, this service is dispatched (or already present as an agent participant) and detects the join event.
2. **Fetch context** (the one backend call at start): call `apps/backend` with the room/candidate identity to fetch the full goal list, job context, and confirm the session is actually authorized to start (this doubles as the room-access check — the worker does not re-validate the candidate's signed token itself; it trusts the backend's answer). If the backend says not authorized (expired token, wrong date, already completed), the worker must not proceed to open the mic — it should play a neutral "this interview session is not currently available" message and end the connection.
3. **Opening statement**: on confirmed join, speak an opening statement, then ask goal #1's `suggested_opening` — this is a scripted worker action, not an agent decision (there's no prior turn to call the agent with yet).
4. **Per-turn loop** (`session/turn_handler.py`), for every candidate utterance after that:
   a. Transcribe via STT.
   b. Run the transcript through `shared/safety/regex_denylist.py`, then `shared/safety/injection_classifier.py` (Layer 1 / Layer 2 from the agent's own defense-in-depth model). **If flagged, do not call `interviewer-agent` at all this turn** — take a canned, deterministic action instead (e.g. a neutral clarifying prompt) and record the flag.
   c. If clean, build the input contract from `InterviewSessionState` and invoke `interviewer-agent` in-process.
   d. Validate the response against guardrails (see above). Update `InterviewSessionState` (append to `goal_history`, increment turn count, add elapsed time).
   e. Speak `message_to_candidate` via TTS.
   f. If `flag_for_human_review: true` came back (e.g. suspected injection that slipped past Layers 1–2, distress disclosure, abusive input), fire an async, non-blocking notification to `apps/backend` — this must never block the live turn loop; log-and-continue if the call fails, don't retry synchronously mid-conversation.
5. **On `action: advance`** (goal genuinely finished, guardrail-approved): checkpoint to `apps/backend` — clean `role`/`content` interaction history for the finished goal, plus the raw per-turn decisions for audit (backend decides how to split/store these; the worker just sends both, see the backend doc). Advance `InterviewSessionState` to `next_goal`. If there is no `next_goal`, treat this as the interview-end path instead of advancing.
6. **On interview end** (no more goals, or a guardrail-forced early stop — e.g. max duration hit): speak the closing statement (from the final `message_to_candidate`, or a scripted fallback if the last agent call already errored out), then call `apps/backend`'s "complete" endpoint with final session state. This service's job ends here — it does not call `interview-grader-agent` itself; grading is `apps/backend`'s responsibility to enqueue.
7. **Disconnect handling**: a dropped candidate connection is not a silent hang — treat it the same as a guardrail-forced stop (report whatever partial state exists to `apps/backend`'s "complete" endpoint, flagged as an incomplete session) rather than leaving the interview stuck in `in_progress` forever.

### Execution Limits (inherited, enforced locally)

- `interviewer-agent`'s own 3-retry schema-validation limit is internal to that package. If it still raises after 3 attempts, this service must have a deterministic fallback turn ready (a pre-written neutral clarifying question) — a live call cannot hang waiting on a retry loop it doesn't own. Never let an unhandled exception from the agent call take down the room connection.
- Every agent invocation is traced via LangSmith by the agent package itself; this service does not need to duplicate tracing, but must not catch-and-discard exceptions in a way that would prevent the trace from completing.

---

## 3. Directory Tree & Structure

```text
apps/realtime-worker/
├── src/
│   └── worker/
│       ├── main.py                    # livekit-agents entrypoint: worker registration, dispatch handling
│       ├── core/
│       │   ├── config.py              # env vars: LiveKit URL/keys, backend base URL/service secret, Google creds
│       │   └── backend_client.py      # typed httpx client for the 3 allowed backend calls
│       ├── session/
│       │   ├── interview_session.py   # InterviewSessionState: goals, history, timers, turn counts
│       │   ├── turn_handler.py        # per-turn orchestration (§2, step 4)
│       │   └── guardrails.py          # min-turns / max-duration validation over agent recommendations
│       ├── pipeline/
│       │   ├── stt.py                 # Google STT plugin wiring
│       │   ├── tts.py                 # Google TTS plugin wiring
│       │   └── vad.py                 # Silero VAD wiring
│       └── lifecycle/
│           ├── opening.py             # scripted opening statement + first goal prompt
│           └── closing.py             # closing statement + disconnect/early-stop handling
├── tests/
│   └── test_turn_handler.py           # guardrail override cases, safety-flag short-circuit cases
├── pyproject.toml                     # uv workspace member; path dependency on apps/agents
├── Dockerfile
└── GEMINI.md                          # this file
```
