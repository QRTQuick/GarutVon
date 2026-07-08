from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from passlib.context import CryptContext
import secrets
from flask_login import UserMixin

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
Base = declarative_base()


class User(UserMixin, Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(320), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    name = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    def get_id(self):
        return str(self.id)

    def set_password(self, password: str):
        self.password_hash = pwd_ctx.hash(password)

    def check_password(self, password: str) -> bool:
        return pwd_ctx.verify(password, self.password_hash)


class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String(64), unique=True, nullable=False, default=lambda: secrets.token_hex(32))
    label = Column(String(120), default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Download(Base):
    __tablename__ = "downloads"
    id = Column(Integer, primary_key=True)
    filename = Column(String(400))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SupportTicket(Base):
    __tablename__ = "support_tickets"
    id = Column(Integer, primary_key=True)
    user_email = Column(String(320))
    subject = Column(String(200))
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class ApiLog(Base):
    __tablename__ = "api_logs"
    id = Column(Integer, primary_key=True)
    endpoint = Column(String(200))
    status = Column(String(50))
    detail = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
