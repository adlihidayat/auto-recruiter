"""
What: Provides security utilities for password hashing and JWT token generation.
Why: Centralizes cryptographic operations required for user authentication.
Boundaries: Does not contain FastAPI request/response handling or database queries.
"""

from datetime import datetime, timedelta, UTC
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import application_settings

ph = PasswordHasher()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against an Argon2 hashed password.
    """
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a plain password using Argon2.
    """
    return ph.hash(password)

def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=application_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, 
        application_settings.SECRET_KEY, 
        algorithm=application_settings.ALGORITHM
    )
    return encoded_jwt
