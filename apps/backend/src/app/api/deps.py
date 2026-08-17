"""
What: FastAPI Dependencies.
Why: Centralizes reusable dependencies like database sessions and JWT authentication extraction.
Boundaries: Contains dependency injection logic, no raw route handlers.
"""

from typing import Annotated
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

async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """
    Dependency to extract and validate the JWT, returning the current User.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            application_settings.SECRET_KEY, 
            algorithms=[application_settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
        
    # Fetch user from DB
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]
