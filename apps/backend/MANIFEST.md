# Backend Service Manifest

| File Path | Purpose | Key Exports / Dependencies |
| :--- | :--- | :--- |
| `src/app/main.py` | FastAPI app entrypoint & DB connection check lifespan | `app` |
| `src/app/core/config.py` | Strongly-typed environment configuration loader | `application_settings`, `ApplicationSettings` |
| `src/app/core/db.py` | Async SQLAlchemy 2.0 engine & session factory | `async_database_engine`, `async_session_factory`, `get_async_database_session` |
| `src/app/models/base.py` | SQLAlchemy Declarative Base | `Base` |
| `src/app/models/user.py` | User entity schema | `User` |
| `src/app/models/interview.py` | Interview entity schema | `Interview` |
| `src/app/models/candidate.py` | Candidate entity schema with high-level evaluation stats | `Candidate` |
| `src/app/models/goal.py` | Interview evaluation Goal entity schema | `Goal` |
| `src/app/models/transcript.py` | Candidate turn transcript & internal interviewer reasoning | `Transcript` |
| `src/app/models/report.py` | Granular CandidateReport grading payload schema | `CandidateReport` |
| `src/app/models/job.py` | Postgres-backed async background Job task queue entity | `Job` |
