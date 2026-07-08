from .session import SessionLocal, engine
from .models import Base

def init_db():
    # create tables if they don't exist
    Base.metadata.create_all(bind=engine)
