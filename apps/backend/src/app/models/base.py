"""
What: Defines the SQLAlchemy declarative base.
Why: All ORM models inherit from this base so Alembic can discover them in a unified metadata registry.
Boundaries: Contains no actual database models.
"""

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base class for all models.
    """
    pass
