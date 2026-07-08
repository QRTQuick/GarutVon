import os
import requests
from urllib.parse import urljoin

MAILJET_API_KEY = os.getenv('MAILJET_API_KEY')
MAILJET_SECRET_KEY = os.getenv('MAILJET_SECRET_KEY')
EMAIL_FROM = os.getenv('EMAIL_FROM', 'onboarding@garutvon.app')

def send_password_reset(email: str, reset_url: str) -> bool:
    """Send a simple password reset email using Mailjet (HTTP API)."""
    if not MAILJET_API_KEY or not MAILJET_SECRET_KEY:
        return False
    url = 'https://api.mailjet.com/v3.1/send'
    payload = {
        'Messages': [
            {
                'From': {'Email': EMAIL_FROM, 'Name': 'GarutVON'},
                'To': [{'Email': email}],
                'Subject': 'GarutVON password reset',
                'TextPart': f'Use this link to reset your password: {reset_url}',
                'HTMLPart': f'<p>Use this link to reset your password:</p><p><a href="{reset_url}">{reset_url}</a></p>',
            }
        ]
    }
    try:
        r = requests.post(url, json=payload, auth=(MAILJET_API_KEY, MAILJET_SECRET_KEY), timeout=10)
        return r.status_code == 200
    except Exception:
        return False
