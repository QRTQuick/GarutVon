import os
import requests
from backend.config import Config


class EmailService:
    @staticmethod
    def _get_site_url():
        return Config.SITE_URL.rstrip("/")

    @staticmethod
    def _send_mailjet_email(to_email, to_name, subject, text_content, html_content):
        if not Config.MAILJET_API_KEY or not Config.MAILJET_SECRET_KEY:
            print(f"[SIMULATED EMAIL TO {to_email}]")
            print(f"Subject: {subject}")
            print(f"Content: {text_content}\n" + "-" * 50)
            return (
                True,
                "Simulated email sent successfully (Mailjet keys not configured).",
            )

        url = "https://api.mailjet.com/v3.1/send"
        auth = (Config.MAILJET_API_KEY, Config.MAILJET_SECRET_KEY)

        data = {
            "Messages": [
                {
                    "From": {
                        "Email": Config.MAIL_FROM_EMAIL,
                        "Name": Config.MAIL_FROM_NAME,
                    },
                    "To": [{"Email": to_email, "Name": to_name}],
                    "Subject": subject,
                    "TextPart": text_content,
                    "HTMLPart": html_content,
                }
            ]
        }

        try:
            response = requests.post(url, auth=auth, json=data, timeout=10)
            if response.status_code == 200 or response.status_code == 201:
                return True, "Email sent successfully via Mailjet."
            else:
                print(
                    f"Mailjet failed with status code {response.status_code}: {response.text}"
                )
                return (
                    False,
                    f"Mailjet returned {response.status_code}: {response.text}",
                )
        except Exception as e:
            print(f"Mailjet request exception: {str(e)}")
            return False, f"Mailjet request failed: {str(e)}"

    @classmethod
    def send_welcome_email(cls, to_email, to_name):
        subject = "Welcome to GarutVON - Unleash Your File Productivity"
        text = f"Hello {to_name or 'there'},\n\nWelcome to GarutVON! We are thrilled to have you join our premium universal file productivity platform. You are now equipped with ultra-fast file conversion and developer-grade cloud tools.\n\nEnjoy converting files!\n\nBest regards,\nThe GarutVON Team"
        site_url = cls._get_site_url()
        html = f"""
        <div style="font-family: Arial, sans-serif; background-color: #050505; color: #ffffff; padding: 40px; border-radius: 8px; max-width: 600px; margin: auto; border: 1px solid #222;">
            <h1 style="color: #ffffff; border-bottom: 1px solid #222; padding-bottom: 20px;">Welcome to GarutVON</h1>
            <p style="color: #ccc; line-height: 1.6;">Hello <strong>{to_name or 'User'}</strong>,</p>
            <p style="color: #ccc; line-height: 1.6;">Thank you for registering on <strong>GarutVON</strong>. We're on a mission to build the world's most premium, high-speed file utility suite.</p>
            <p style="color: #ccc; line-height: 1.6;">As a member, you get <strong>10 free image conversions per week</strong>. You can also generate developer API keys from your user dashboard to build custom applications.</p>
            <div style="margin: 30px 0; text-align: center;">
                <a href="{site_url}/dashboard" style="background-color: #ffffff; color: #000000; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 4px; display: inline-block;">Go to Dashboard</a>
            </div>
            <p style="color: #666; font-size: 12px; margin-top: 40px; border-top: 1px solid #222; padding-top: 20px; text-align: center;">&copy; 2026 GarutVON Inc. All rights reserved.</p>
        </div>
        """
        return cls._send_mailjet_email(to_email, to_name, subject, text, html)

    @classmethod
    def send_verify_email(cls, to_email, to_name, token):
        verify_url = f"{cls._get_site_url()}/verify-email?token={token}"
        subject = "Verify Your GarutVON Account"
        text = f"Hello {to_name or 'there'},\n\nPlease verify your email by opening the following link: {verify_url}\n\nThis verification link expires in 24 hours.\n\nThanks,\nGarutVON Team"
        html = f"""
        <div style="font-family: Arial, sans-serif; background-color: #050505; color: #ffffff; padding: 40px; border-radius: 8px; max-width: 600px; margin: auto; border: 1px solid #222;">
            <h1 style="color: #ffffff; border-bottom: 1px solid #222; padding-bottom: 20px;">Verify Your Email Address</h1>
            <p style="color: #ccc; line-height: 1.6;">Hello <strong>{to_name or 'User'}</strong>,</p>
            <p style="color: #ccc; line-height: 1.6;">Please confirm your registration on GarutVON by clicking the link below. This secure verification link will expire in 24 hours.</p>
            <div style="margin: 30px 0; text-align: center;">
                <a href="{verify_url}" style="background-color: #ffffff; color: #000000; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 4px; display: inline-block;">Verify Email Address</a>
            </div>
            <p style="color: #555; font-size: 12px; word-wrap: break-word;">If that button doesn't work, copy and paste this URL into your browser:<br>{verify_url}</p>
            <p style="color: #666; font-size: 12px; margin-top: 40px; border-top: 1px solid #222; padding-top: 20px; text-align: center;">&copy; 2026 GarutVON Inc. All rights reserved.</p>
        </div>
        """
        return cls._send_mailjet_email(to_email, to_name, subject, text, html)

    @classmethod
    def send_password_reset(cls, to_email, to_name, token):
        reset_url = f"{cls._get_site_url()}/reset-password?token={token}"
        subject = "Reset Your GarutVON Password"
        text = f"Hello {to_name or 'there'},\n\nWe received a request to reset your password. Open this link to complete the reset: {reset_url}\n\nIf you did not make this request, please disregard this email. This link will expire in 1 hour.\n\nThanks,\nGarutVON Team"
        html = f"""
        <div style="font-family: Arial, sans-serif; background-color: #050505; color: #ffffff; padding: 40px; border-radius: 8px; max-width: 600px; margin: auto; border: 1px solid #222;">
            <h1 style="color: #ffffff; border-bottom: 1px solid #222; padding-bottom: 20px;">Password Reset Request</h1>
            <p style="color: #ccc; line-height: 1.6;">Hello <strong>{to_name or 'User'}</strong>,</p>
            <p style="color: #ccc; line-height: 1.6;">We received a request to reset your GarutVON password. To set up a new password, click the secure link below. This link expires in 1 hour.</p>
            <div style="margin: 30px 0; text-align: center;">
                <a href="{reset_url}" style="background-color: #ffffff; color: #000000; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 4px; display: inline-block;">Reset Password</a>
            </div>
            <p style="color: #555; font-size: 12px; word-wrap: break-word;">If that button doesn't work, copy and paste this URL into your browser:<br>{reset_url}</p>
            <p style="color: #666; font-size: 12px; margin-top: 40px; border-top: 1px solid #222; padding-top: 20px; text-align: center;">&copy; 2026 GarutVON Inc. All rights reserved.</p>
        </div>
        """
        return cls._send_mailjet_email(to_email, to_name, subject, text, html)

    @classmethod
    def send_login_alert(cls, to_email, to_name, ip_address, user_agent):
        subject = "Security Alert: New Login for GarutVON"
        text = f"Hello {to_name or 'there'},\n\nA new login was registered on your GarutVON account.\n\nDate: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\nIP Address: {ip_address}\nBrowser/Device: {user_agent}\n\nIf this was not you, please reset your password immediately.\n\nThanks,\nGarutVON Team"
        html = f"""
        <div style="font-family: Arial, sans-serif; background-color: #050505; color: #ffffff; padding: 40px; border-radius: 8px; max-width: 600px; margin: auto; border: 1px solid #222;">
            <h1 style="color: #ff3333; border-bottom: 1px solid #222; padding-bottom: 20px;">Security Alert: New Login</h1>
            <p style="color: #ccc; line-height: 1.6;">Hello <strong>{to_name or 'User'}</strong>,</p>
            <p style="color: #ccc; line-height: 1.6;">We noticed a successful login to your GarutVON account from a new location or device.</p>
            <div style="background-color: #111; border: 1px solid #333; padding: 15px; border-radius: 4px; margin: 20px 0; color: #fff; font-family: monospace;">
                <strong>IP Address:</strong> {ip_address}<br>
                <strong>Device/Agent:</strong> {user_agent}<br>
                <strong>Time:</strong> {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
            </div>
            <p style="color: #ccc; line-height: 1.6;">If this login was authorized by you, no action is needed. If you do not recognize this login, please change your password instantly in your security dashboard.</p>
            <p style="color: #666; font-size: 12px; margin-top: 40px; border-top: 1px solid #222; padding-top: 20px; text-align: center;">&copy; 2026 GarutVON Inc. All rights reserved.</p>
        </div>
        """
        return cls._send_mailjet_email(to_email, to_name, subject, text, html)

    @classmethod
    def send_api_key_created(cls, to_email, to_name, key_name):
        subject = "GarutVON Notification: New Developer API Key Created"
        text = f"Hello {to_name or 'there'},\n\nA new developer API Key named '{key_name}' has been successfully created in your developer portal. Always keep this key secure. If you did not create this key, please revoke it immediately inside the Developer Portal.\n\nThanks,\nGarutVON Team"
        html = f"""
        <div style="font-family: Arial, sans-serif; background-color: #050505; color: #ffffff; padding: 40px; border-radius: 8px; max-width: 600px; margin: auto; border: 1px solid #222;">
            <h1 style="color: #ffffff; border-bottom: 1px solid #222; padding-bottom: 20px;">Developer API Key Created</h1>
            <p style="color: #ccc; line-height: 1.6;">Hello <strong>{to_name or 'User'}</strong>,</p>
            <p style="color: #ccc; line-height: 1.6;">A new developer API Key has been generated under your account credentials.</p>
            <div style="background-color: #111; border: 1px solid #333; padding: 15px; border-radius: 4px; margin: 20px 0; color: #fff;">
                <strong>Key Name:</strong> {key_name}<br>
                <strong>Status:</strong> Active<br>
                <strong>Date Created:</strong> {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
            </div>
            <p style="color: #ccc; line-height: 1.6;">Please keep this key secure. Do not share it or check it into client-side codebases or public Git repositories.</p>
            <p style="color: #666; font-size: 12px; margin-top: 40px; border-top: 1px solid #222; padding-top: 20px; text-align: center;">&copy; 2026 GarutVON Inc. All rights reserved.</p>
        </div>
        """
        return cls._send_mailjet_email(to_email, to_name, subject, text, html)

    @classmethod
    def send_password_changed(cls, to_email, to_name):
        subject = "GarutVON Security Notice: Password Changed Successfully"
        text = f"Hello {to_name or 'there'},\n\nYour GarutVON password has been changed successfully. If you did not authorize this change, please contact support and reset your password immediately to protect your account.\n\nThanks,\nGarutVON Team"
        html = f"""
        <div style="font-family: Arial, sans-serif; background-color: #050505; color: #ffffff; padding: 40px; border-radius: 8px; max-width: 600px; margin: auto; border: 1px solid #222;">
            <h1 style="color: #ffffff; border-bottom: 1px solid #222; padding-bottom: 20px;">Security Alert: Password Changed</h1>
            <p style="color: #ccc; line-height: 1.6;">Hello <strong>{to_name or 'User'}</strong>,</p>
            <p style="color: #ccc; line-height: 1.6;">This email confirms that the password for your GarutVON account was recently modified.</p>
            <p style="color: #ccc; line-height: 1.6;">If you authorized this change, you can safely ignore this warning. If you did not make this change, please trigger a Password Reset request immediately and contact our Security Response team.</p>
            <p style="color: #666; font-size: 12px; margin-top: 40px; border-top: 1px solid #222; padding-top: 20px; text-align: center;">&copy; 2026 GarutVON Inc. All rights reserved.</p>
        </div>
        """
        return cls._send_mailjet_email(to_email, to_name, subject, text, html)


import datetime
