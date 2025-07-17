import aiosqlite
import json
import os
from typing import Optional, Dict, Any, Callable
import logging
from backend import config

logger = logging.getLogger(__name__)
DB_PATH = os.getenv("DATABASE_PATH", "./ai_tutor.db")

class DatabaseCache:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    async def initialize_cache_table(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS cached_metadata (
                    query_hash TEXT PRIMARY KEY,
                    metadata_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def get_or_set_metadata(
        self, 
        query: str, 
        coro: Callable,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        query_hash = self._generate_hash(query)
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT metadata_json FROM cached_metadata WHERE query_hash = ?", (query_hash,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    logger.info(f"Cache hit for query: {query[:50]}...")
                    return json.loads(row['metadata_json'])

        logger.info(f"Cache miss for query: {query[:50]}... Generating new content")
        generated_content = await coro(*args, **kwargs)
        metadata_dict = json.loads(generated_content)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO cached_metadata (query_hash, metadata_json) VALUES (?, ?)",
                (query_hash, json.dumps(metadata_dict))
            )
            await db.commit()
            logger.info(f"Cached new metadata for query: {query[:50]}...")

        return metadata_dict

    def _generate_hash(self, query: str) -> str:
        import hashlib
        return hashlib.sha256(query.encode()).hexdigest()

# Initialize the database cache
db_cache = DatabaseCache()