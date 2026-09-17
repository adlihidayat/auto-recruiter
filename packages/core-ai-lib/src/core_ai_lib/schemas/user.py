from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    country: str | None = None
    born_date: str | None = None

class UsernameCheckResponse(BaseModel):
    username: str
    available: bool

class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str | None = None
    country: str | None = None
    born_date: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RegisterResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
