from __future__ import annotations
import os


class Settings:
    ENV: str = os.getenv("ENV", "development")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://localhost/garutvon_dev",
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-to-a-secure-random-value")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    ALGORITHM: str = "HS256"
    PUBLIC_BASE_URL: str = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")
    DOWNLOAD_URL: str | None = os.getenv("DOWNLOAD_URL")
    MAILJET_API_KEY: str | None = os.getenv("MAILJET_API_KEY")
    MAILJET_SECRET_KEY: str | None = os.getenv("MAILJET_SECRET_KEY")
    RESEND_API_KEY: str | None = os.getenv("RESEND_API_KEY")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "onboarding@garutvon.app")
    PASSWORD_RESET_EXPIRY_MINUTES: int = int(os.getenv("PASSWORD_RESET_EXPIRY_MINUTES", "60"))


settings = Settings()
