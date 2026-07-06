import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_NAME = os.getenv("APP_NAME", "GarutVON")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-garutvon-secret")
    JWT_SECRET = os.getenv("JWT_SECRET", SECRET_KEY)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///garutvon_dev.db")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    DONATION_URL = os.getenv("DONATION_URL", "https://myhappr.com/chisomlifeeugsh")
    DOWNLOAD_URL = os.getenv("DOWNLOAD_URL", "/download/garutvon-latest.exe")
    LATEST_VERSION = os.getenv("LATEST_VERSION", "1.0.0")
    LATEST_CHECKSUM = os.getenv("LATEST_CHECKSUM", "sha256:local-development-build")
    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "200 per day;50 per hour")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
