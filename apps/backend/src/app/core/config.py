"""
What: Defines application environment variables and settings loader using Pydantic BaseSettings.
Why: Centralizes environment configuration parsing and validation for DB, SMTP, JWT, and LiveKit credentials.
Boundaries: Does not create active network clients or database connection pools.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationSettings(BaseSettings):
    """
    Strongly-typed application settings loaded from environment variables or .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5433/autorecruiter"

    # Mailpit / SMTP
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@autorecruiter.local"

    # JWT Security
    SECRET_KEY: str = "super-secret-local-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # LiveKit
    LIVEKIT_URL: str = "ws://localhost:7880"
    LIVEKIT_API_KEY: str = "devkey"
    LIVEKIT_API_SECRET: str = "secret"


# Global singleton instance for settings
application_settings = ApplicationSettings()
