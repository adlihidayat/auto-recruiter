"""
What: Configuration settings for the realtime worker.
Why: Centralizes environment variable loading and validation.
Boundaries: Contains only configuration constants, no business logic.
"""

import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    livekit_url: str = Field(default=os.getenv("LIVEKIT_URL", "ws://localhost:7880"))
    livekit_api_key: str = Field(default=os.getenv("LIVEKIT_API_KEY", "devkey"))
    livekit_api_secret: str = Field(default=os.getenv("LIVEKIT_API_SECRET", "secret"))
    backend_url: str = Field(default=os.getenv("BACKEND_URL", "http://localhost:8000"))
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
