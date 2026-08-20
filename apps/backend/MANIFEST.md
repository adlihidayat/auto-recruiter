# Backend Service Manifest

| File Path | Purpose | Key Exports / Dependencies |
| :--- | :--- | :--- |
| `src/app/main.py` | FastAPI app entrypoint & DB connection check lifespan | `app` |
| `src/app/core/config.py` | Strongly-typed environment configuration loader | `application_settings`, `ApplicationSettings` |
| `src/app/core/db.py` | Async SQLAlchemy 2.0 engine & session factory | `async_database_engine`, `async_session_factory`, `get_async_database_session` |
| `src/app/core/security.py` | Cryptographic utilities (Argon2 hashes, JWT encoding) | `verify_password`, `get_password_hash`, `create_access_token` |
| `src/app/api/deps.py` | FastAPI reusable dependencies (DB sessions, auth JWT parsing) | `SessionDep`, `CurrentUser` |
| `src/app/api/auth.py` | API Router handling OAuth2 login and token exchange | `router` |
| `src/app/api/interviews.py` | API Router handling interview creation, interview listing, and candidate listing | `router` |
| `src/app/api/candidates.py` | API Router handling candidate reports and turn-by-turn transcripts | `router` |
| `src/app/services/agent_client.py` | HTTP Client communicating over network with Agents Service (`:8001`) | `request_question_suite_from_agent` |
| `src/app/services/plan_service.py` | Background task orchestration service for agent execution & DB goal persistence | `process_interview_plan_generation` |
| `src/app/schemas/interview.py` | Pydantic request/response schemas for interviews (`InterviewCreate`, `InterviewResponse`) | `InterviewCreate`, `InterviewResponse` |
| `src/app/schemas/candidate.py` | Pydantic response schemas for candidates | `CandidateResponse` |
| `src/app/schemas/report.py` | Pydantic response schema for candidate grading reports | `CandidateReportResponse` |
| `src/app/schemas/transcript.py` | Pydantic response schema for interaction transcripts | `TranscriptResponse` |
| `src/app/models/base.py` | SQLAlchemy Declarative Base | `Base` |
| `src/app/models/user.py` | User entity schema | `User` |
| `src/app/models/interview.py` | Interview entity schema | `Interview` |
| `src/app/models/candidate.py` | Candidate entity schema with high-level evaluation stats | `Candidate` |
| `src/app/models/goal.py` | Interview evaluation Goal entity schema | `Goal` |
| `src/app/models/transcript.py` | Candidate turn transcript & internal interviewer reasoning | `Transcript` |
| `src/app/models/report.py` | Granular CandidateReport grading payload schema | `CandidateReport` |
| `src/app/models/job.py` | Postgres-backed async background Job task queue entity | `Job` |
