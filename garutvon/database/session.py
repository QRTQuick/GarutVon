from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from garutvon.backend.config import Config

engine = create_engine(Config.DATABASE_URL, pool_pre_ping=True, future=True)
db_session = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True))


def init_db() -> None:
    from .models import Base

    Base.metadata.create_all(bind=engine)
