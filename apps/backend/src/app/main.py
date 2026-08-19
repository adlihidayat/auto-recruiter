"""
What: FastAPI application factory and lifespan manager.
Why: Serves as the HTTP entrypoint and verifies infrastructure dependencies (DB connection) on startup.
Boundaries: Does not contain direct database queries or domain business logic.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.db import async_database_engine, async_session_factory
from app.api.auth import router as auth_router
from app.api.interviews import router as interviews_router
from app.api.candidates import router as candidates_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def application_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manages application startup and shutdown lifecycle events.
    Verifies database connectivity on startup.
    """
    logger.info("Initializing Backend Service...")
    
    # Test database connectivity
    try:
        async with async_session_factory() as session:
            result = await session.execute(text("SELECT 1"))
            value = result.scalar()
            if value == 1:
                logger.info("✅ Database connection established successfully!")
            else:
                logger.error("❌ Unexpected database response during startup check.")
    except Exception as exc:
        logger.error(f"❌ Failed to connect to the database: {exc}")
        raise exc

    yield

    # Clean shutdown of DB engine connection pool
    logger.info("Shutting down database engine connection pool...")
    await async_database_engine.dispose()
    logger.info("Backend Service shutdown complete.")


app = FastAPI(
    title="Auto Recruiter Backend",
    version="1.0.0",
    lifespan=application_lifespan,
)

# Configure CORS so the Next.js frontend (localhost:3000) can talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(interviews_router, prefix="/api/interviews", tags=["Interviews"])
app.include_router(candidates_router, prefix="/api/candidates", tags=["Candidates"])

@app.get("/health")
async def check_health_status() -> dict[str, str]:
    """
    Public health check endpoint.
    """
    return {"status": "ok", "service": "backend"}
