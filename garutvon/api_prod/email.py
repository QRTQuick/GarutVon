from typing import Optional

import requests

from .config import settings

try:
    from resend import Resend
except ImportError:
    Resend = None


def build_reset_link(token: str) -> str:
    return f"{settings.PUBLIC_BASE_URL}/reset-password?token={token}"


def _mailjet_auth() -> Optional[tuple[str, str]]:
    if settings.MAILJET_API_KEY and settings.MAILJET_SECRET_KEY:
        return settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY
    return None


def _resend_client() -> Optional[Resend]:
    if settings.RESEND_API_KEY:
        return Resend(settings.RESEND_API_KEY)
    return None


def send_password_reset_email(email: str, token: str) -> dict:
    reset_link = build_reset_link(token)
    message_html = (
        f"<p>Hello,</p>"
        f"<p>You requested a password reset for your GarutVON account.</p>"
        f"<p><a href=\"{reset_link}\">Reset your password</a></p>"
        f"<p>If you did not request this, you can safely ignore this message.</p>"
    )

    mailjet_auth = _mailjet_auth()
    if mailjet_auth:
        api_key, secret_key = mailjet_auth
        payload = {
            "Messages": [
                {
                    "From": {"Email": settings.EMAIL_FROM, "Name": "GarutVON"},
                    "To": [{"Email": email}],
                    "Subject": "GarutVON Password Reset",
                    "HTMLPart": message_html,
                }
            ]
        }
        response = requests.post(
            "https://api.mailjet.com/v3.1/send",
            json=payload,
            auth=(api_key, secret_key),
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    resend_client = _resend_client()
    if resend_client:
        params = {
            "from": settings.EMAIL_FROM,
            "to": [email],
            "subject": "GarutVON Password Reset",
            "html": message_html,
        }
        return resend_client.emails.send(params)

    raise RuntimeError(
        "Mail service is not configured. Set MAILJET_API_KEY/MAILJET_SECRET_KEY or RESEND_API_KEY."
    )
