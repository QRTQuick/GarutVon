import datetime
import jwt
import uuid
import hashlib
from backend.config import Config
from database.models import SessionLocal, User, Session, EmailToken, PasswordResetToken

class AuthService:
    JWT_ALGORITHM = "HS256"

    # --- JWT Token Handlers (For APIs) ---
    @classmethod
    def generate_jwt(cls, user_id, api_key_id=None, expires_in_days=30):
        payload = {
            "sub": str(user_id),
            "api_key_id": str(api_key_id) if api_key_id else None,
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=expires_in_days)
        }
        return jwt.encode(payload, Config.JWT_SECRET, algorithm=cls.JWT_ALGORITHM)

    @classmethod
    def verify_jwt(cls, token):
        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=[cls.JWT_ALGORITHM])
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, "Token has expired."
        except jwt.InvalidTokenError as e:
            return False, f"Invalid token: {str(e)}"

    # --- Session Management (For Website/Dashboard Web Authentication) ---
    @classmethod
    def create_web_session(cls, user_id, ip_address=None, user_agent=None, remember_me=False):
        db = SessionLocal()
        try:
            session_token = uuid.uuid4().hex + uuid.uuid4().hex
            expires_days = 30 if remember_me else 1
            expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=expires_days)
            
            new_session = Session(
                session_token=session_token,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at,
                created_at=datetime.datetime.utcnow()
            )
            db.add(new_session)
            db.commit()
            return session_token
        except Exception as e:
            db.rollback()
            print(f"Error creating session: {e}")
            return None
        finally:
            db.close()

    @classmethod
    def verify_web_session(cls, session_token):
        if not session_token:
            return None
        db = SessionLocal()
        try:
            session = db.query(Session).filter_by(session_token=session_token).first()
            if not session:
                return None
            if session.expires_at < datetime.datetime.utcnow():
                db.delete(session)
                db.commit()
                return None
            return session.user_id
        except Exception as e:
            print(f"Error verifying web session: {e}")
            return None
        finally:
            db.close()

    @classmethod
    def destroy_web_session(cls, session_token):
        if not session_token:
            return True
        db = SessionLocal()
        try:
            session = db.query(Session).filter_by(session_token=session_token).first()
            if session:
                db.delete(session)
                db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error destroying session: {e}")
            return False
        finally:
            db.close()

    # --- Security Token Generators (Email Verification / Password Resets) ---
    @classmethod
    def create_email_verification_token(cls, user_id):
        db = SessionLocal()
        try:
            token = uuid.uuid4().hex + uuid.uuid4().hex
            # Set email tokens table entry
            email_token = EmailToken(
                token=token,
                user_id=user_id,
                purpose="VERIFY_EMAIL",
                expires_at=datetime.datetime.utcnow() + datetime.timedelta(hours=24),
                is_used=False
            )
            db.add(email_token)
            db.commit()
            return token
        except Exception as e:
            db.rollback()
            print(f"Error creating email token: {e}")
            return None
        finally:
            db.close()

    @classmethod
    def verify_email_token(cls, token_str):
        db = SessionLocal()
        try:
            token_record = db.query(EmailToken).filter_by(token=token_str, purpose="VERIFY_EMAIL", is_used=False).first()
            if not token_record:
                return False, "Token not found or already verified."
            if token_record.expires_at < datetime.datetime.utcnow():
                return False, "Token has expired."
                
            # Verify user
            user = db.query(User).filter_by(id=token_record.user_id).first()
            if user:
                user.is_verified = True
                token_record.is_used = True
                db.commit()
                return True, "Email verified successfully."
            return False, "User not found."
        except Exception as e:
            db.rollback()
            print(f"Error verifying email token: {e}")
            return False, str(e)
        finally:
            db.close()

    @classmethod
    def create_password_reset_token(cls, user_id):
        db = SessionLocal()
        try:
            token = uuid.uuid4().hex + uuid.uuid4().hex
            reset_token = PasswordResetToken(
                token=token,
                user_id=user_id,
                expires_at=datetime.datetime.utcnow() + datetime.timedelta(hours=1),
                is_used=False
            )
            db.add(reset_token)
            db.commit()
            return token
        except Exception as e:
            db.rollback()
            print(f"Error creating reset token: {e}")
            return None
        finally:
            db.close()

    @classmethod
    def verify_password_reset_token(cls, token_str):
        db = SessionLocal()
        try:
            token_record = db.query(PasswordResetToken).filter_by(token=token_str, is_used=False).first()
            if not token_record:
                return None, "Token not found or already used."
            if token_record.expires_at < datetime.datetime.utcnow():
                return None, "Token has expired."
            return token_record.user_id, ""
        except Exception as e:
            print(f"Error checking password reset token: {e}")
            return None, str(e)
        finally:
            db.close()

    @classmethod
    def use_password_reset_token(cls, token_str, new_password):
        db = SessionLocal()
        try:
            token_record = db.query(PasswordResetToken).filter_by(token=token_str, is_used=False).first()
            if not token_record:
                return False, "Token not found or already used."
            if token_record.expires_at < datetime.datetime.utcnow():
                return False, "Token has expired."
                
            user = db.query(User).filter_by(id=token_record.user_id).first()
            if user:
                user.set_password(new_password)
                token_record.is_used = True
                db.commit()
                return True, "Password updated successfully."
            return False, "User not found."
        except Exception as e:
            db.rollback()
            print(f"Error resetting password: {e}")
            return False, str(e)
        finally:
            db.close()

    # --- CSRF Protection helper ---
    @classmethod
    def generate_csrf_token(cls, session_token):
        if not session_token:
            return None
        # Standard robust signature using shared SECRET_KEY
        return hashlib.sha256((session_token + Config.SECRET_KEY).encode()).hexdigest()

    @classmethod
    def validate_csrf_token(cls, session_token, csrf_token_to_check):
        if not session_token or not csrf_token_to_check:
            return False
        expected = cls.generate_csrf_token(session_token)
        return expected == csrf_token_to_check
