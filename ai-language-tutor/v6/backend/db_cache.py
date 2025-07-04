import asyncio
import json
from typing import Any, Callable, Optional
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from backend.database import AsyncSessionLocal, GeneratedContent, generate_cache_key
import logging

logger = logging.getLogger(__name__)


class DatabaseCache:
    def __init__(self):
        self.lock = asyncio.Lock()

    async def get_or_set(
        self, 
        key_params: tuple, 
        coro: Callable, 
        content_type: str = "unknown",
        user_id: Optional[int] = None,
        native_language: Optional[str] = None,
        target_language: Optional[str] = None,
        proficiency: Optional[str] = None,
        *args, 
        **kwargs
    ) -> str:
        """
        Get cached content from database or generate and cache new content
        
        Args:
            key_params: Tuple of (query, instructions) for cache key generation
            coro: Async function to call if cache miss
            content_type: Type of content (curriculum, flashcards, etc.)
            user_id: Optional user ID for analytics
            native_language: User's native language
            target_language: Language being learned
            proficiency: User's proficiency level
            *args, **kwargs: Arguments to pass to coro
        """
        query, instructions = key_params
        cache_key = generate_cache_key(query, instructions, content_type)
        
        # Try to get from database first
        async with AsyncSessionLocal() as session:
            stmt = select(GeneratedContent).where(GeneratedContent.cache_key == cache_key)
            result = await session.execute(stmt)
            cached_item = result.scalar_one_or_none()
            
            if cached_item:
                # Update access statistics
                await session.execute(
                    update(GeneratedContent)
                    .where(GeneratedContent.cache_key == cache_key)
                    .values(
                        last_accessed=datetime.utcnow(),
                        access_count=GeneratedContent.access_count + 1
                    )
                )
                await session.commit()
                logger.info(f"Cache hit for key: {cache_key[:12]}...")
                return cached_item.generated_content
        
        # Cache miss - generate new content
        logger.info(f"Cache miss for key: {cache_key[:12]}... Generating new content")
        async with self.lock:
            # Double-check pattern - check again after acquiring lock
            async with AsyncSessionLocal() as session:
                stmt = select(GeneratedContent).where(GeneratedContent.cache_key == cache_key)
                result = await session.execute(stmt)
                cached_item = result.scalar_one_or_none()
                
                if cached_item:
                    # Another request already generated this
                    return cached_item.generated_content
                
                # Generate new content
                generated_content = await coro(*args, **kwargs)
                
                # Store in database
                new_item = GeneratedContent(
                    cache_key=cache_key,
                    content_type=content_type,
                    user_id=user_id,
                    query=query,
                    instructions=instructions,
                    generated_content=generated_content,
                    native_language=native_language,
                    target_language=target_language,
                    proficiency=proficiency,
                    created_at=datetime.utcnow(),
                    last_accessed=datetime.utcnow(),
                    access_count=1
                )
                
                try:
                    session.add(new_item)
                    await session.commit()
                    logger.info(f"Cached new content with key: {cache_key[:12]}...")
                except IntegrityError:
                    # Handle race condition where another request inserted the same key
                    await session.rollback()
                    stmt = select(GeneratedContent).where(GeneratedContent.cache_key == cache_key)
                    result = await session.execute(stmt)
                    cached_item = result.scalar_one_or_none()
                    if cached_item:
                        return cached_item.generated_content
                
                return generated_content

    async def get_by_cache_key(self, cache_key: str) -> Optional[dict]:
        """Get cached content by cache key"""
        async with AsyncSessionLocal() as session:
            stmt = select(GeneratedContent).where(GeneratedContent.cache_key == cache_key)
            result = await session.execute(stmt)
            cached_item = result.scalar_one_or_none()
            
            if cached_item:
                # Update access statistics
                await session.execute(
                    update(GeneratedContent)
                    .where(GeneratedContent.cache_key == cache_key)
                    .values(
                        last_accessed=datetime.utcnow(),
                        access_count=GeneratedContent.access_count + 1
                    )
                )
                await session.commit()
                
                return {
                    "content": cached_item.generated_content,
                    "content_type": cached_item.content_type,
                    "query": cached_item.query,
                    "native_language": cached_item.native_language,
                    "target_language": cached_item.target_language,
                    "proficiency": cached_item.proficiency,
                    "created_at": cached_item.created_at.isoformat(),
                    "access_count": cached_item.access_count
                }
        return None

    async def get_user_content(
        self, 
        user_id: int, 
        content_type: Optional[str] = None,
        limit: int = 50
    ) -> list:
        """Get all cached content for a user"""
        async with AsyncSessionLocal() as session:
            stmt = select(GeneratedContent).where(GeneratedContent.user_id == user_id)
            
            if content_type:
                stmt = stmt.where(GeneratedContent.content_type == content_type)
            
            stmt = stmt.order_by(GeneratedContent.created_at.desc()).limit(limit)
            
            result = await session.execute(stmt)
            items = result.scalars().all()
            
            return [
                {
                    "cache_key": item.cache_key,
                    "content_type": item.content_type,
                    "query": item.query,
                    "content": item.generated_content,
                    "native_language": item.native_language,
                    "target_language": item.target_language,
                    "proficiency": item.proficiency,
                    "created_at": item.created_at.isoformat(),
                    "access_count": item.access_count
                }
                for item in items
            ]

    async def delete_by_cache_key(self, cache_key: str) -> bool:
        """Delete cached content by cache key"""
        async with AsyncSessionLocal() as session:
            stmt = select(GeneratedContent).where(GeneratedContent.cache_key == cache_key)
            result = await session.execute(stmt)
            item = result.scalar_one_or_none()
            
            if item:
                await session.delete(item)
                await session.commit()
                return True
            return False


# Initialize the database cache
db_cache = DatabaseCache() 