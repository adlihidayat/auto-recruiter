# Backend Service Manifest

| File Path | Purpose | Key Exports / Dependencies |
| :--- | :--- | :--- |
| `src/app/main.py` | FastAPI app entrypoint & DB connection check lifespan | `app` |
| `src/app/core/config.py` | Strongly-typed environment configuration loader | `application_settings`, `ApplicationSettings` |
| `src/app/core/db.py` | Async SQLAlchemy 2.0 engine & session factory | `async_database_engine`, `async_session_factory`, `get_async_database_session` |
