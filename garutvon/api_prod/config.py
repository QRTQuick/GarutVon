from __future__ import annotations
import os
from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    ENV: str = os.getenv("ENV", "development")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/garutvon_dev")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-to-a-secure-random-value")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    ALGORITHM: str = "HS256"
    PUBLIC_BASE_URL: str = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")
    DOWNLOAD_URL: str | None = os.getenv("DOWNLOAD_URL")
    RESEND_API_KEY: str | None = os.getenv("RESEND_API_KEY")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "onboarding@garutvon.app")
    PASSWORD_RESET_EXPIRY_MINUTES: int = int(os.getenv("PASSWORD_RESET_EXPIRY_MINUTES", "60"))

    class Config:
        env_file = ["local.env", ".env.local", ".env"]


settings = Settings()
