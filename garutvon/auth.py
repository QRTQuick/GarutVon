from itsdangerous import URLSafeTimedSerializer
import os

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
SECURITY_SALT = 'garutvon-password-reset'

def generate_reset_token(email: str) -> str:
    s = URLSafeTimedSerializer(SECRET_KEY)
    return s.dumps(email, salt=SECURITY_SALT)

def confirm_reset_token(token: str, expiration=3600) -> str | None:
    s = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = s.loads(token, salt=SECURITY_SALT, max_age=expiration)
    except Exception:
        return None
    return email
