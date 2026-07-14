import os
from dotenv import load_dotenv

# Load environment variables from .env at repository root when running locally
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
dotenv_path = os.path.join(project_root, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


def _resolve_database_url():
    raw_url = os.getenv("DATABASE_URL", "").strip()
    if not raw_url:
        return f"sqlite:///{os.path.join(project_root, 'garutvon.db')}"

    placeholder_keys = [
        "<host>",
        "<username>",
        "<password>",
        "<database>",
        "postgresql://<",
        "postgres://<",
    ]
    if any(token in raw_url for token in placeholder_keys):
        return f"sqlite:///{os.path.join(project_root, 'garutvon.db')}"

    if raw_url.startswith("postgres://"):
        raw_url = raw_url.replace("postgres://", "postgresql://", 1)
    return raw_url


class Config:
    # General Config
    SECRET_KEY = os.getenv("SECRET_KEY", "garutvon-super-secret-dev-key-123456")
    JWT_SECRET = os.getenv("JWT_SECRET", "garutvon-jwt-secret-key-987654")

    # Environment
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # Database
    DATABASE_URL = _resolve_database_url()
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads & Outputs
    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads"),
    )
    OUTPUT_FOLDER = os.getenv(
        "OUTPUT_FOLDER",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs"),
    )
    MAX_CONTENT_LENGTH = int(
        os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024)
    )  # 16MB limit

    # Mailjet Config
    MAILJET_API_KEY = os.getenv("MAILJET_API_KEY", "")
    MAILJET_SECRET_KEY = os.getenv("MAILJET_SECRET_KEY", "")
    MAIL_FROM_EMAIL = os.getenv("MAIL_FROM_EMAIL", "noreply@garutvon.com")
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "GarutVON")
    SITE_URL = os.getenv("SITE_URL", "https://garutvon.vercel.app").rstrip("/")

    # Rate Limiting & Allowances
    FREE_CONVERSION_LIMIT = int(
        os.getenv("FREE_CONVERSION_LIMIT", 10)
    )  # conversions per week

    # Happer Integration Config
    HAPPER_DONATION_EMBED = "https://myhappr.com/embed/chisomlifeeugsh?text=Make+garutvon+smile&color=%235EB5FF&title=Support+GarutVon+donate+as+much+smiles+as+u+want+"
    HAPPER_WEBHOOK_SECRET = os.getenv("HAPPER_WEBHOOK_SECRET", "happer_secret_123")
