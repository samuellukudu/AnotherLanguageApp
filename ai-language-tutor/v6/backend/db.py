import aiosqlite
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

# Database file path
DB_PATH = os.getenv("DATABASE_PATH", "./ai_tutor.db")


class Database:
    """Pure SQLite database handler for AI Language Tutor"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
    
    async def initialize(self):
        """Initialize database with schema"""
        async with aiosqlite.connect(self.db_path) as db:
            # Read and execute schema - look for it in parent directory
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path, 'r') as f:
                schema = f.read()
            await db.executescript(schema)
            await db.commit()
            logger.info("Database initialized successfully")
    
    async def find_existing_curriculum(
        self,
        query: str,
        native_language: str,
        target_language: str,
        proficiency: str,
        user_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Find existing curriculum for similar query and metadata"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            if user_id is not None:
                # User-specific search: First try to find exact query match for the user
                async with db.execute("""
                    SELECT c.*, m.native_language, m.target_language, m.proficiency, m.title, m.query
                    FROM curricula c
                    JOIN metadata_extractions m ON c.metadata_extraction_id = m.id
                    WHERE m.user_id = ? AND m.query = ? AND m.native_language = ? 
                    AND m.target_language = ? AND m.proficiency = ?
                    ORDER BY c.created_at DESC
                    LIMIT 1
                """, (user_id, query, native_language, target_language, proficiency)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return dict(row)
                
                # Then try to find similar curriculum with same metadata (any user)
                async with db.execute("""
                    SELECT c.*, m.native_language, m.target_language, m.proficiency, m.title, m.query
                    FROM curricula c
                    JOIN metadata_extractions m ON c.metadata_extraction_id = m.id
                    WHERE m.native_language = ? AND m.target_language = ? AND m.proficiency = ?
                    AND c.is_content_generated = 1
                    ORDER BY c.created_at DESC
                    LIMIT 1
                """, (native_language, target_language, proficiency)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return dict(row)
            else:
                # User-independent search: Find exact query match regardless of user
                async with db.execute("""
                    SELECT c.*, m.native_language, m.target_language, m.proficiency, m.title, m.query
                    FROM curricula c
                    JOIN metadata_extractions m ON c.metadata_extraction_id = m.id
                    WHERE m.query = ? AND m.native_language = ? AND m.target_language = ? AND m.proficiency = ?
                    ORDER BY c.created_at DESC
                    LIMIT 1
                """, (query, native_language, target_language, proficiency)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return dict(row)
        
        return None

    async def save_metadata_extraction(
        self,
        query: str,
        metadata: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> str:
        """Save extracted metadata and return extraction ID"""
        extraction_id = str(uuid.uuid4())
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO metadata_extractions 
                (id, user_id, query, native_language, target_language, proficiency, title, description, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                extraction_id,
                user_id,
                query,
                metadata.get('native_language'),
                metadata.get('target_language'),
                metadata.get('proficiency'),
                metadata.get('title'),
                metadata.get('description'),
                json.dumps(metadata)
            ))
            await db.commit()
        
        logger.info(f"Saved metadata extraction: {extraction_id}")
        return extraction_id
    
    async def save_curriculum(
        self,
        metadata_extraction_id: str,
        curriculum: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> str:
        """Save generated curriculum and return curriculum ID"""
        curriculum_id = str(uuid.uuid4())
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO curricula 
                (id, metadata_extraction_id, user_id, lesson_topic, curriculum_json)
                VALUES (?, ?, ?, ?, ?)
            """, (
                curriculum_id,
                metadata_extraction_id,
                user_id,
                curriculum.get('lesson_topic', ''),
                json.dumps(curriculum)
            ))
            await db.commit()
        
        logger.info(f"Saved curriculum: {curriculum_id}")
        return curriculum_id
    
    async def copy_curriculum_for_user(
        self,
        source_curriculum_id: str,
        metadata_extraction_id: str,
        user_id: Optional[int] = None
    ) -> str:
        """Copy an existing curriculum for a new user"""
        new_curriculum_id = str(uuid.uuid4())
        
        async with aiosqlite.connect(self.db_path) as db:
            # Get source curriculum
            async with db.execute("""
                SELECT lesson_topic, curriculum_json FROM curricula WHERE id = ?
            """, (source_curriculum_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise ValueError(f"Source curriculum {source_curriculum_id} not found")
                
                lesson_topic, curriculum_json = row
            
            # Create new curriculum
            await db.execute("""
                INSERT INTO curricula 
                (id, metadata_extraction_id, user_id, lesson_topic, curriculum_json, is_content_generated)
                VALUES (?, ?, ?, ?, ?, 0)
            """, (
                new_curriculum_id,
                metadata_extraction_id,
                user_id,
                lesson_topic,
                curriculum_json
            ))
            
            # Copy all learning content
            await db.execute("""
                INSERT INTO learning_content 
                (id, curriculum_id, content_type, lesson_index, lesson_topic, content_json)
                SELECT 
                    lower(hex(randomblob(16))),
                    ?,
                    content_type,
                    lesson_index,
                    lesson_topic,
                    content_json
                FROM learning_content 
                WHERE curriculum_id = ?
            """, (new_curriculum_id, source_curriculum_id))
            
            # Mark as content generated
            await db.execute("""
                UPDATE curricula 
                SET is_content_generated = 1 
                WHERE id = ?
            """, (new_curriculum_id,))
            
            await db.commit()
        
        logger.info(f"Copied curriculum {source_curriculum_id} to {new_curriculum_id} for user {user_id}")
        return new_curriculum_id
    
    async def save_learning_content(
        self,
        curriculum_id: str,
        content_type: str,
        lesson_index: int,
        lesson_topic: str,
        content: Any
    ) -> str:
        """Save learning content (flashcards, exercises, or simulation)"""
        content_id = str(uuid.uuid4())
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO learning_content 
                (id, curriculum_id, content_type, lesson_index, lesson_topic, content_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                content_id,
                curriculum_id,
                content_type,
                lesson_index,
                lesson_topic,
                json.dumps(content) if isinstance(content, (dict, list)) else content
            ))
            await db.commit()
        
        logger.info(f"Saved {content_type} for lesson {lesson_index}")
        return content_id
    
    async def mark_curriculum_content_generated(self, curriculum_id: str):
        """Mark curriculum as having all content generated"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE curricula 
                SET is_content_generated = 1 
                WHERE id = ?
            """, (curriculum_id,))
            await db.commit()
    
    async def get_metadata_extraction(self, extraction_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata extraction by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM metadata_extractions WHERE id = ?
            """, (extraction_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
        return None
    
    async def get_curriculum(self, curriculum_id: str) -> Optional[Dict[str, Any]]:
        """Get curriculum by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT c.*, m.native_language, m.target_language, m.proficiency
                FROM curricula c
                JOIN metadata_extractions m ON c.metadata_extraction_id = m.id
                WHERE c.id = ?
            """, (curriculum_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
        return None
    
    async def get_learning_content(
        self,
        curriculum_id: str,
        content_type: Optional[str] = None,
        lesson_index: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get learning content for a curriculum"""
        query = "SELECT * FROM learning_content WHERE curriculum_id = ?"
        params = [curriculum_id]
        
        if content_type:
            query += " AND content_type = ?"
            params.append(content_type)
        
        if lesson_index is not None:
            query += " AND lesson_index = ?"
            params.append(lesson_index)
        
        query += " ORDER BY lesson_index"
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_user_metadata_extractions(
        self,
        user_id: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get user's metadata extraction history"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM metadata_extractions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_user_curricula(
        self,
        user_id: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get user's curricula"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT c.*, m.native_language, m.target_language, m.proficiency, m.title
                FROM curricula c
                JOIN metadata_extractions m ON c.metadata_extraction_id = m.id
                WHERE c.user_id = ? 
                ORDER BY c.created_at DESC 
                LIMIT ?
            """, (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_user_learning_journeys(
        self,
        user_id: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get user's complete learning journeys"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM user_learning_journeys 
                WHERE user_id = ? 
                LIMIT ?
            """, (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_curriculum_content_status(self, curriculum_id: str) -> Optional[Dict[str, Any]]:
        """Get content generation status for a curriculum"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM curriculum_content_status WHERE curriculum_id = ?
            """, (curriculum_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
        return None

    async def get_full_curriculum_details(self, curriculum_id: str, include_content: bool = True) -> Optional[Dict[str, Any]]:
        """Get full curriculum details, optionally including all content."""
        curriculum = await self.get_curriculum(curriculum_id)
        if not curriculum:
            return None

        try:
            curriculum_data = json.loads(curriculum['curriculum_json'])
            lessons = curriculum_data.get('sub_topics', [])
        except json.JSONDecodeError:
            curriculum_data = {}
            lessons = []

        if include_content:
            content_list = await self.get_learning_content(curriculum_id)
            content_map = {}
            for content in content_list:
                lesson_index = content['lesson_index']
                content_type = content['content_type']
                if lesson_index not in content_map:
                    content_map[lesson_index] = {}
                
                try:
                    parsed_content = json.loads(content['content_json'])
                except json.JSONDecodeError:
                    parsed_content = content['content_json']

                content_map[lesson_index][content_type] = {
                    "id": content['id'],
                    "lesson_topic": content['lesson_topic'],
                    "content": parsed_content,
                    "created_at": content['created_at']
                }

            # Embed content into lessons
            for i, lesson in enumerate(lessons):
                lesson['content'] = content_map.get(i, {})

        curriculum['curriculum'] = curriculum_data
        del curriculum['curriculum_json']

        return curriculum
    
    async def search_curricula_by_languages(
        self,
        native_language: str,
        target_language: str,
        proficiency: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for existing curricula by language combination"""
        query = """
            SELECT c.*, m.native_language, m.target_language, m.proficiency, m.title
            FROM curricula c
            JOIN metadata_extractions m ON c.metadata_extraction_id = m.id
            WHERE m.native_language = ? AND m.target_language = ?
        """
        params = [native_language, target_language]
        
        if proficiency:
            query += " AND m.proficiency = ?"
            params.append(proficiency)
        
        query += " ORDER BY c.created_at DESC LIMIT ?"
        params.append(limit)
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]


# Global database instance
db = Database()