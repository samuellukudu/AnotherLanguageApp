import aiosqlite
import json
import os
from typing import Optional, Dict, Any, Callable, Union, List
import logging
import hashlib

logger = logging.getLogger(__name__)
DB_PATH = os.getenv("DATABASE_PATH", "./ai_tutor.db")

class ApiCache:
    """Generic caching service using a dedicated database table."""
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def _generate_hash(self, text: str) -> str:
        """Generate a SHA256 hash for a given text."""
        return hashlib.sha256(text.encode()).hexdigest()

    async def get_or_set(
        self,
        category: str,
        key_text: str,
        coro: Callable,
        *args,
        **kwargs
    ) -> Union[Dict[str, Any], List[Any], str]:
        """
        Get data from cache or execute a coroutine to generate and cache it.
        
        Args:
            category: The category of the cached item (e.g., 'metadata', 'flashcards').
            key_text: The text to use for generating the cache key.
            coro: The async function to call if the item is not in the cache.
            *args: Positional arguments for the coroutine.
            **kwargs: Keyword arguments for the coroutine.
            
        Returns:
            The cached or newly generated content.
        """
        cache_key = self._generate_hash(key_text)
        
        # 1. Check cache
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT content_json FROM api_cache WHERE cache_key = ? AND category = ?",
                (cache_key, category)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    logger.info(f"Cache hit for {category} with key: {key_text[:50]}...")
                    return json.loads(row['content_json'])

        # 2. If miss, generate content
        logger.info(f"Cache miss for {category}: {key_text[:50]}... Generating new content")
        generated_content = await coro(*args, **kwargs)
        
        # Ensure content is a JSON-serializable string
        if isinstance(generated_content, (dict, list)):
            content_to_cache = json.dumps(generated_content)
        elif isinstance(generated_content, str):
            # Try to parse string to ensure it's valid JSON, then dump it back
            try:
                parsed_json = json.loads(generated_content)
                content_to_cache = json.dumps(parsed_json)
            except json.JSONDecodeError:
                # If it's not a JSON string, we can't cache it in this system.
                # Depending on requirements, we might raise an error or just return it without caching.
                logger.warning(f"Content for {category} is not valid JSON, returning without caching.")
                return generated_content
        else:
            raise TypeError("Cached content must be a JSON string, dict, or list.")

        # 3. Store in cache
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO api_cache (cache_key, category, content_json) VALUES (?, ?, ?)",
                (cache_key, category, content_to_cache)
            )
            await db.commit()
            logger.info(f"Cached new content for {category} with key: {key_text[:50]}...")

        return json.loads(content_to_cache)

# Global API cache instance
api_cache = ApiCache()