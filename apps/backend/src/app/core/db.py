"""
What: Configures the SQLAlchemy 2.0 async engine and session factory.
Why: Serves as the central database connection manager for asynchronous database access.
Boundaries: Does not contain ORM table models, repository queries, or migration logic.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import application_settings

# Initialize async engine with connection pooling
async_database_engine: AsyncEngine = create_async_engine(
    application_settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Async session factory for dependency injection & repository scopes
async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_database_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_async_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency yielding an async database session per request context.
    """
    async with async_session_factory() as session:
        yield session
