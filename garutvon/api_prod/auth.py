from datetime import datetime, timedelta
from typing import Optional
import secrets
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .config import settings
from .db import get_db
from .models import ApiKey, User


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub: str = payload.get("sub")
        if sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    q = await db.execute(select(User).where(User.email == sub))
    user = q.scalars().first()
    if not user:
        raise credentials_exception
    return user


async def get_api_key(x_api_key: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)) -> Optional[ApiKey]:
    if not x_api_key:
        return None
    q = await db.execute(select(ApiKey).where(ApiKey.key == x_api_key, ApiKey.revoked == False))
    key = q.scalars().first()
    return key


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    q = await db.execute(select(User).where(User.email == email))
    user = q.scalars().first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

