from datetime import datetime, timedelta
import secrets
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..db import get_db
from ..email import send_password_reset_email
from ..models import User, ApiKey, PasswordResetToken
from ..schemas import (
    UserCreate,
    UserOut,
    Token,
    PasswordResetRequest,
    PasswordResetConfirm,
    MessageOut,
)
from ..auth import (
    create_access_token,
    authenticate_user,
    hash_password,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(User).where(User.email == payload.email))
    existing = q.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/token", response_model=Token)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=60 * 24)
    token = create_access_token({"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/forgot-password", response_model=MessageOut)
async def forgot_password(
    payload: PasswordResetRequest, db: AsyncSession = Depends(get_db)
):
    q = await db.execute(select(User).where(User.email == payload.email))
    user = q.scalars().first()
    if user:
        token_value = secrets.token_urlsafe(48)
        expires_at = datetime.utcnow() + timedelta(minutes=60)
        reset_token = PasswordResetToken(
            token=token_value,
            user_id=user.id,
            expires_at=expires_at,
            used=False,
        )
        db.add(reset_token)
        await db.commit()
        try:
            send_password_reset_email(user.email, token_value)
        except Exception:
            # if email fails, still return generic response to prevent account enumeration
            pass
    return {"message": "If an account exists, a password reset email has been sent."}


@router.post("/reset-password", response_model=MessageOut)
async def reset_password(
    payload: PasswordResetConfirm, db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == payload.token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at >= datetime.utcnow(),
        )
    )
    reset_token = q.scalars().first()
    if not reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    user_q = await db.execute(select(User).where(User.id == reset_token.user_id))
    user = user_q.scalars().first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    user.hashed_password = hash_password(payload.new_password)
    reset_token.used = True
    db.add(user)
    db.add(reset_token)
    await db.commit()
    return {"message": "Your password has been reset successfully."}


class ApiKeyOut:
    id: int
    key: str
    name: str | None


@router.post("/keys", response_model=dict)
async def create_api_key(
    name: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    key_value = secrets.token_urlsafe(32)
    api_key = ApiKey(key=key_value, owner_id=current_user.id, name=name)
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    return {"id": api_key.id, "key": api_key.key, "name": api_key.name}


@router.get("/keys", response_model=List[dict])
async def list_keys(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    q = await db.execute(select(ApiKey).where(ApiKey.owner_id == current_user.id))
    keys = q.scalars().all()
    return [
        {
            "id": k.id,
            "key": (k.key if not k.revoked else None),
            "name": k.name,
            "revoked": k.revoked,
        }
        for k in keys
    ]


@router.post("/keys/revoke", response_model=dict)
async def revoke_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.owner_id == current_user.id)
    )
    key = q.scalars().first()
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    key.revoked = True
    db.add(key)
    await db.commit()
    return {"id": key.id, "revoked": True}
