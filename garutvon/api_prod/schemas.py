from __future__ import annotations
from pydantic import BaseModel, EmailStr
from typing import List, Optional


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str]


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        orm_mode = True


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class MessageOut(BaseModel):
    message: str


class SummarizeIn(BaseModel):
    text: str


class SummarizeOut(BaseModel):
    summary: str
    sentence_count: int
