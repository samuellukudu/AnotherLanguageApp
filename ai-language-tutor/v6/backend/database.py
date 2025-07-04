from sqlalchemy import Column, String, Text, DateTime, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import hashlib
import json
from typing import Optional

# Use SQLite database - much simpler setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./ai_tutor.db")

# Create async engine for SQLite
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models
Base = declarative_base()


class SavedContent(Base):
    """Table for storing generated AI content"""
    __tablename__ = "saved_content"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String(64), unique=True, index=True)  # Unique identifier for content
    content_type = Column(String(50), index=True)  # metadata, curriculum, flashcards, exercises, simulation
    user_id = Column(Integer, index=True, nullable=True)
    query = Column(Text)
    generated_content = Column(Text)  # JSON string of the actual content
    native_language = Column(String(50), nullable=True)
    target_language = Column(String(50), nullable=True)
    proficiency = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserMetadata(Base):
    """Table specifically for storing user language learning metadata"""
    __tablename__ = "user_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)  # Can be null for anonymous extractions
    query = Column(Text)  # Original query that was analyzed
    native_language = Column(String(50))
    target_language = Column(String(50))
    proficiency = Column(String(20))  # beginner, intermediate, advanced
    title = Column(String(200))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


def generate_content_id(query: str, content_type: str, user_id: Optional[int] = None) -> str:
    """Generate a unique content ID"""
    combined = f"{query}|{content_type}|{user_id or 'anonymous'}"
    return hashlib.sha256(combined.encode()).hexdigest()


async def get_db_session():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Drop all tables (for testing)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) 