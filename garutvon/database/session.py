from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os
from garutvon.backend.config import Config

DATABASE_URL = Config.DATABASE_URL

# sync engine for Flask-side usage
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = scoped_session(
    sessionmaker(bind=engine, autocommit=False, autoflush=False)
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
