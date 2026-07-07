from typing import Optional

from resend import Resend

from .config import settings


client: Optional[Resend] = None
if settings.RESEND_API_KEY:
    client = Resend(settings.RESEND_API_KEY)


def build_reset_link(token: str) -> str:
    return f"{settings.PUBLIC_BASE_URL}/reset-password?token={token}"


def send_password_reset_email(email: str, token: str) -> dict:
    if client is None:
        raise RuntimeError("RESEND_API_KEY is not configured")

    reset_link = build_reset_link(token)
    params = {
        "from": settings.EMAIL_FROM,
        "to": [email],
        "subject": "GarutVON Password Reset",
        "html": (
            f"<p>Hello,</p>"
            f"<p>You requested a password reset for your GarutVON account.</p>"
            f"<p><a href=\"{reset_link}\">Reset your password</a></p>"
            f"<p>If you did not request this, you can safely ignore this message.</p>"
        ),
    }
    response = client.emails.send(params)
    return response
