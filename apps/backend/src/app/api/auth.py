"""
What: Authentication API routes.
Why: Exposes login endpoint for the frontend to exchange credentials for a JWT access token.
Boundaries: Implements FastAPI OAuth2 spec but offloads cryptographic functions to core.security.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, or_

from app.api.deps import SessionDep, CurrentUser
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.user import User
from app.schemas.user import UserRegister, UserResponse, RegisterResponse, UsernameCheckResponse

router = APIRouter()

@router.get("/check-username", response_model=UsernameCheckResponse)
async def check_username_availability(
    session: SessionDep,
    username: str = Query(..., min_length=1, description="Username to check")
):
    """
    Check if a username is available.
    """
    result = await session.execute(
        select(User).where(User.username == username)
    )
    existing_user = result.scalar_one_or_none()
    return UsernameCheckResponse(
        username=username,
        available=existing_user is None
    )

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    session: SessionDep,
    payload: UserRegister
):
    """
    Create a new user account with username, country, born date, email, and password.
    """
    # 1. Check email uniqueness
    result_email = await session.execute(select(User).where(User.email == payload.email))
    if result_email.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    # 2. Check username uniqueness
    if payload.username:
        result_user = await session.execute(select(User).where(User.username == payload.username))
        if result_user.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is already taken"
            )

    # 3. Create user
    new_user = User(
        email=payload.email,
        username=payload.username,
        country=payload.country,
        born_date=payload.born_date,
        hashed_password=get_password_hash(payload.password)
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # 4. Generate JWT access token
    access_token = create_access_token(subject=str(new_user.id))

    return RegisterResponse(
        user=UserResponse.model_validate(new_user),
        access_token=access_token,
        token_type="bearer"
    )

@router.post("/login")
async def login_access_token(
    session: SessionDep, 
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> dict[str, str]:
    """
    OAuth2 compatible token login. Supports logging in by email or username.
    """
    # Find user by email or username
    result = await session.execute(
        select(User).where(
            or_(User.email == form_data.username, User.username == form_data.username)
        )
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username/email or password"
        )
        
    access_token = create_access_token(subject=str(user.id))
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
async def test_current_user(current_user: CurrentUser):
    """
    Get current logged in user details.
    """
    return current_user
