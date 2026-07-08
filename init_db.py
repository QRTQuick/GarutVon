"""Initialize database tables for GarutVON (both Flask and FastAPI)."""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
load_dotenv(".env")
load_dotenv(".env.local", override=True)
load_dotenv("local.env", override=True)

async def init_fastapi_db():
    """Initialize FastAPI Async SQLAlchemy tables."""
    from sqlalchemy.ext.asyncio import create_async_engine
    from garutvon.api_prod.config import settings
    from garutvon.api_prod.db import Base
    
    print("🔧 Initializing FastAPI database...")
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("✅ FastAPI database tables created.")

def init_flask_db():
    """Initialize Flask SQLAlchemy tables."""
    from garutvon.database import init_db
    
    print("🔧 Initializing Flask database...")
    try:
        init_db()
        print("✅ Flask database tables created.")
    except Exception as e:
        print(f"⚠️  Flask DB init warning: {e}")

if __name__ == "__main__":
    print("🚀 Initializing GarutVON databases...\n")
    
    # Initialize Flask
    try:
        init_flask_db()
    except Exception as e:
        print(f"❌ Flask DB init failed: {e}")
    
    # Initialize FastAPI
    try:
        asyncio.run(init_fastapi_db())
    except Exception as e:
        print(f"❌ FastAPI DB init failed: {e}")
    
    print("\n✨ Database initialization complete!")
