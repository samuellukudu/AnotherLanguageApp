from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment from root .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Database configuration
DB_NAME = os.getenv("POSTGRES_DB", "linguaai")
DB_USER = os.getenv("POSTGRES_USER", "linguaai_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "LinguaAI1008")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
# Build async database URL strictly from env vars
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# Optional SSL mode for managed Postgres (e.g. 'require')
DB_SSLMODE = os.getenv("DB_SSLMODE")

# Create async engine without SSL args (asyncpg defaults to no TLS)
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session
