"""
What: FastAPI Dependencies.
Why: Centralizes reusable dependencies like database sessions and JWT authentication extraction.
Boundaries: Contains dependency injection logic, no raw route handlers.
"""

from typing import Annotated
import uuid
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import application_settings
from app.core.db import get_async_database_session
from app.models.user import User

# OAuth2 scheme configures Swagger UI to send tokens to the right endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Type alias for cleaner route definitions
SessionDep = Annotated[AsyncSession, Depends(get_async_database_session)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]

import logging
logger = logging.getLogger(__name__)

async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """
    Dependency to extract and validate the JWT, returning the current User.
    """
    try:
        payload = jwt.decode(
            token, 
            application_settings.SECRET_KEY, 
            algorithms=[application_settings.ALGORITHM]
        )
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            logger.error("❌ JWT token missing 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing subject claim",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = uuid.UUID(user_id_str)
    except jwt.ExpiredSignatureError:
        logger.error("❌ JWT token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.InvalidTokenError, ValueError) as err:
        logger.error(f"❌ Invalid JWT token: {err}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {err}",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Fetch user from DB
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        logger.error(f"❌ User with ID {user_id} not found in database")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]
