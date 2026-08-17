"""
What: Authentication API routes.
Why: Exposes login endpoint for the frontend to exchange credentials for a JWT access token.
Boundaries: Implements FastAPI OAuth2 spec but offloads cryptographic functions to core.security.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.api.deps import SessionDep, CurrentUser
from app.core.security import verify_password, create_access_token
from app.models.user import User

router = APIRouter()

@router.post("/login")
async def login_access_token(
    session: SessionDep, 
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> dict[str, str]:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Find user by email
    result = await session.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
        
    access_token = create_access_token(subject=str(user.id))
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me")
async def test_current_user(current_user: CurrentUser) -> dict[str, str]:
    """
    Test endpoint to verify the current JWT works and returns the logged in user's email.
    """
    return {"email": current_user.email}
