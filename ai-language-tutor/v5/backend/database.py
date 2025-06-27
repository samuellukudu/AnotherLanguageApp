import sqlite3
import json
import uuid
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from contextlib import asynccontextmanager
import aiosqlite
from backend.constants import ContentStatus
import os

class DatabaseManager:
    def __init__(self, db_path: str = None):
        # Import configuration
        try:
            from backend.config import DATABASE_PATH
            self.db_path = db_path or DATABASE_PATH
        except ImportError:
            self.db_path = db_path or "data/language_tutor.db"
        # Ensure the parent directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._locks = {}

    async def initialize_database(self):
        """Initialize the database and create tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript("""
            CREATE TABLE IF NOT EXISTS curricula (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                native_language TEXT,
                target_language TEXT,
                proficiency TEXT,
                lesson_topic TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending'
            );

            CREATE TABLE IF NOT EXISTS lessons (
                id TEXT PRIMARY KEY,
                curriculum_id TEXT NOT NULL,
                sub_topic TEXT NOT NULL,
                description TEXT,
                keywords TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (curriculum_id) REFERENCES curricula (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS flashcards (
                id TEXT PRIMARY KEY,
                lesson_id TEXT NOT NULL,
                word TEXT NOT NULL,
                definition TEXT NOT NULL,
                example TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lessons (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS exercises (
                id TEXT PRIMARY KEY,
                lesson_id TEXT NOT NULL,
                sentence TEXT NOT NULL,
                answer TEXT NOT NULL,
                choices TEXT NOT NULL,
                explanation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lessons (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS simulations (
                id TEXT PRIMARY KEY,
                lesson_id TEXT NOT NULL,
                title TEXT NOT NULL,
                setting TEXT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lessons (id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_curricula_user_id ON curricula(user_id);
            CREATE INDEX IF NOT EXISTS idx_lessons_curriculum_id ON lessons(curriculum_id);
            CREATE INDEX IF NOT EXISTS idx_flashcards_lesson_id ON flashcards(lesson_id);
            CREATE INDEX IF NOT EXISTS idx_exercises_lesson_id ON exercises(lesson_id);
            CREATE INDEX IF NOT EXISTS idx_simulations_lesson_id ON simulations(lesson_id);
            """)
            await db.commit()

    def get_lock(self, curriculum_id: str) -> asyncio.Lock:
        """Get or create a lock for a specific curriculum"""
        if curriculum_id not in self._locks:
            self._locks[curriculum_id] = asyncio.Lock()
        return self._locks[curriculum_id]

    async def store_curriculum(self, user_id: int, metadata: Dict[str, Any], curriculum_data: Dict[str, Any]) -> str:
        """Store curriculum and return curriculum ID"""
        curriculum_id = str(uuid.uuid4())
        
        async with self.get_lock(curriculum_id):
            async with aiosqlite.connect(self.db_path) as db:
                # Extract lesson topic from curriculum data
                lesson_topic = ""
                if curriculum_data:
                    lesson_topic = curriculum_data.get('lesson_topic', '')
                
                # Insert curriculum metadata
                await db.execute("""
                    INSERT INTO curricula (
                        id, user_id, title, description, native_language, 
                        target_language, proficiency, lesson_topic, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    curriculum_id,
                    user_id,
                    metadata.get('title', ''),
                    metadata.get('description', ''),
                    metadata.get('native_language', ''),
                    metadata.get('target_language', ''),
                    metadata.get('proficiency', ''),
                    lesson_topic,
                    ContentStatus.COMPLETED if curriculum_data else ContentStatus.PENDING
                ))
                
                # Store lessons if curriculum data is provided
                if curriculum_data and 'sub_topics' in curriculum_data:
                    for sub_topic_data in curriculum_data['sub_topics']:
                        lesson_id = str(uuid.uuid4())
                        await db.execute("""
                            INSERT INTO lessons (id, curriculum_id, sub_topic, description, keywords)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            lesson_id,
                            curriculum_id,
                            sub_topic_data.get('sub_topic', ''),
                            sub_topic_data.get('description', ''),
                            json.dumps(sub_topic_data.get('keywords', []))
                        ))
                
                await db.commit()
        
        return curriculum_id

    async def get_curriculum(self, curriculum_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve curriculum by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Get curriculum metadata
            async with db.execute("""
                SELECT * FROM curricula WHERE id = ?
            """, (curriculum_id,)) as cursor:
                curriculum_row = await cursor.fetchone()
                
            if not curriculum_row:
                return None
            
            # Get lessons for this curriculum
            async with db.execute("""
                SELECT * FROM lessons WHERE curriculum_id = ? ORDER BY created_at
            """, (curriculum_id,)) as cursor:
                lesson_rows = await cursor.fetchall()
            
            # Get flashcards, exercises, and simulations for all lessons
            flashcards = []
            exercises = []
            simulations = []
            
            for lesson_row in lesson_rows:
                lesson_id = lesson_row["id"]
                
                # Get flashcards for this lesson
                async with db.execute("""
                    SELECT * FROM flashcards WHERE lesson_id = ?
                """, (lesson_id,)) as cursor:
                    lesson_flashcards = await cursor.fetchall()
                    flashcards.extend([dict(row) for row in lesson_flashcards])
                
                # Get exercises for this lesson
                async with db.execute("""
                    SELECT * FROM exercises WHERE lesson_id = ?
                """, (lesson_id,)) as cursor:
                    lesson_exercises = await cursor.fetchall()
                    for exercise_row in lesson_exercises:
                        exercise = dict(exercise_row)
                        exercise['choices'] = json.loads(exercise['choices'])
                        exercises.append(exercise)
                
                # Get simulations for this lesson
                async with db.execute("""
                    SELECT * FROM simulations WHERE lesson_id = ?
                """, (lesson_id,)) as cursor:
                    lesson_simulations = await cursor.fetchall()
                    for sim_row in lesson_simulations:
                        simulation = dict(sim_row)
                        simulation['content'] = json.loads(simulation['content'])
                        simulations.append(simulation)
            
            # Build sub_topics from lessons
            sub_topics = []
            for lesson_row in lesson_rows:
                sub_topics.append({
                    "sub_topic": lesson_row["sub_topic"],
                    "description": lesson_row["description"],
                    "keywords": json.loads(lesson_row["keywords"]) if lesson_row["keywords"] else []
                })
            
            # Build the curriculum object in the expected format
            curriculum = {
                "id": curriculum_row["id"],
                "user_id": curriculum_row["user_id"],
                "metadata": {
                    "title": curriculum_row["title"],
                    "description": curriculum_row["description"],
                    "native_language": curriculum_row["native_language"],
                    "target_language": curriculum_row["target_language"],
                    "proficiency": curriculum_row["proficiency"]
                },
                "created_at": curriculum_row["created_at"],
                "updated_at": curriculum_row["updated_at"],
                "status": {
                    "curriculum": curriculum_row["status"],
                    "flashcards": "completed" if flashcards else "pending",
                    "exercises": "completed" if exercises else "pending",
                    "simulation": "completed" if simulations else "pending"
                },
                "content": {
                    "curriculum": {
                        "lesson_topic": curriculum_row["lesson_topic"],
                        "sub_topics": sub_topics
                    } if curriculum_row["lesson_topic"] else None,
                    "flashcards": flashcards if flashcards else None,
                    "exercises": exercises if exercises else None,
                    "simulation": simulations[0] if simulations else None  # Assuming one simulation per curriculum
                }
            }
            
            return curriculum

    async def update_curriculum_status(self, curriculum_id: str, status: ContentStatus):
        """Update the status of a curriculum"""
        async with self.get_lock(curriculum_id):
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE curricula 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, curriculum_id))
                await db.commit()
                
                # Check if update was successful
                async with db.execute("SELECT changes()") as cursor:
                    changes = await cursor.fetchone()
                    return changes[0] > 0
    
    # Legacy method for backward compatibility
    async def update_content_status(self, curriculum_id: str, content_type: str, status: ContentStatus):
        """Update the status of a curriculum (legacy method for backward compatibility)"""
        if content_type == "curriculum":
            return await self.update_curriculum_status(curriculum_id, status)
        # For other content types, we don't need status updates in the new schema
        # as status is determined by presence of data
        return True

    async def store_flashcards(self, lesson_id: str, flashcards_data: List[Dict[str, Any]]):
        """Store flashcards for a lesson"""
        async with aiosqlite.connect(self.db_path) as db:
            # Clear existing flashcards for this lesson
            await db.execute("DELETE FROM flashcards WHERE lesson_id = ?", (lesson_id,))
            
            # Insert new flashcards
            for flashcard in flashcards_data:
                flashcard_id = str(uuid.uuid4())
                await db.execute("""
                    INSERT INTO flashcards (id, lesson_id, word, definition, example)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    flashcard_id,
                    lesson_id,
                    flashcard.get('word', ''),
                    flashcard.get('definition', ''),
                    flashcard.get('example', '')
                ))
            
            await db.commit()
            return True

    async def store_exercises(self, lesson_id: str, exercises_data: List[Dict[str, Any]]):
        """Store exercises for a lesson"""
        async with aiosqlite.connect(self.db_path) as db:
            # Clear existing exercises for this lesson
            await db.execute("DELETE FROM exercises WHERE lesson_id = ?", (lesson_id,))
            
            # Insert new exercises
            for exercise in exercises_data:
                exercise_id = str(uuid.uuid4())
                await db.execute("""
                    INSERT INTO exercises (id, lesson_id, sentence, answer, choices, explanation)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    exercise_id,
                    lesson_id,
                    exercise.get('sentence', ''),
                    exercise.get('answer', ''),
                    json.dumps(exercise.get('choices', [])),
                    exercise.get('explanation', '')
                ))
            
            await db.commit()
            return True

    async def store_simulation(self, lesson_id: str, simulation_data: Dict[str, Any]):
        """Store simulation for a lesson"""
        async with aiosqlite.connect(self.db_path) as db:
            # Clear existing simulation for this lesson
            await db.execute("DELETE FROM simulations WHERE lesson_id = ?", (lesson_id,))
            
            # Insert new simulation
            simulation_id = str(uuid.uuid4())
            await db.execute("""
                INSERT INTO simulations (id, lesson_id, title, setting, content)
                VALUES (?, ?, ?, ?, ?)
            """, (
                simulation_id,
                lesson_id,
                simulation_data.get('title', ''),
                simulation_data.get('setting', ''),
                json.dumps(simulation_data.get('content', []))
            ))
            
            await db.commit()
            return True

    async def get_lessons(self, curriculum_id: str) -> List[Dict[str, Any]]:
        """Get all lessons for a curriculum"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            async with db.execute("""
                SELECT * FROM lessons WHERE curriculum_id = ? ORDER BY created_at
            """, (curriculum_id,)) as cursor:
                lesson_rows = await cursor.fetchall()
                
            return [dict(row) for row in lesson_rows]

    async def store_curriculum_content(self, curriculum_id: str, curriculum_data: Dict[str, Any]) -> bool:
        """Store curriculum content by updating the curriculum record and creating lessons"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Parse curriculum data to extract lesson topic and sub-topics
                lesson_topic = curriculum_data.get('lesson_topic', '')
                sub_topics = curriculum_data.get('sub_topics', [])
                
                # Update curriculum record with lesson topic and mark as completed
                await db.execute("""
                    UPDATE curricula 
                    SET lesson_topic = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (lesson_topic, ContentStatus.COMPLETED, curriculum_id))
                
                # Create lessons from sub_topics
                for sub_topic in sub_topics:
                    lesson_id = str(uuid.uuid4())
                    await db.execute("""
                        INSERT INTO lessons (id, curriculum_id, sub_topic, description, keywords)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        lesson_id,
                        curriculum_id,
                        sub_topic.get('sub_topic', ''),
                        sub_topic.get('description', ''),
                        json.dumps(sub_topic.get('keywords', []))
                    ))
                
                await db.commit()
                return True
                
        except Exception as e:
            print(f"Error storing curriculum content: {e}")
            return False

    async def create_default_lesson(self, curriculum_id: str) -> bool:
        """Create a default lesson if none exists"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                lesson_id = str(uuid.uuid4())
                await db.execute("""
                    INSERT INTO lessons (id, curriculum_id, sub_topic, description, keywords)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    lesson_id,
                    curriculum_id,
                    "General Lesson",
                    "Default lesson for content storage",
                    json.dumps([])
                ))
                await db.commit()
                return True
                
        except Exception as e:
            print(f"Error creating default lesson: {e}")
            return False

    # Legacy method for backward compatibility
    async def store_generated_content(self, curriculum_id: str, content_type: str, content_data: Dict[str, Any]):
        """Store generated content (legacy method for backward compatibility)"""
        
        # Handle curriculum content separately - it updates the curriculum record itself
        if content_type == "curriculum":
            return await self.store_curriculum_content(curriculum_id, content_data)
        
        # For other content types, we need lessons
        lessons = await self.get_lessons(curriculum_id)
        
        if not lessons:
            # If no lessons exist, create a default lesson from curriculum content
            await self.create_default_lesson(curriculum_id)
            lessons = await self.get_lessons(curriculum_id)
            
        if not lessons:
            return False
            
        # For backward compatibility, we'll store content for the first lesson
        lesson_id = lessons[0]['id']
        
        if content_type == "flashcards" and isinstance(content_data, list):
            return await self.store_flashcards(lesson_id, content_data)
        elif content_type == "exercises" and isinstance(content_data, list):
            return await self.store_exercises(lesson_id, content_data)
        elif content_type == "simulation":
            return await self.store_simulation(lesson_id, content_data)
        
        return True

    async def get_user_curricula(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all curricula for a user"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            async with db.execute("""
                SELECT * FROM curricula 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            """, (user_id,)) as cursor:
                rows = await cursor.fetchall()
            
            curricula = []
            for row in rows:
                curriculum_id = row["id"]
                
                # Get lessons for this curriculum
                async with db.execute("""
                    SELECT * FROM lessons WHERE curriculum_id = ? ORDER BY created_at
                """, (curriculum_id,)) as cursor:
                    lesson_rows = await cursor.fetchall()
                
                # Get content counts for status determination
                flashcard_count = 0
                exercise_count = 0
                simulation_count = 0
                
                for lesson_row in lesson_rows:
                    lesson_id = lesson_row["id"]
                    
                    # Count flashcards
                    async with db.execute("""
                        SELECT COUNT(*) FROM flashcards WHERE lesson_id = ?
                    """, (lesson_id,)) as cursor:
                        flashcard_count += (await cursor.fetchone())[0]
                    
                    # Count exercises
                    async with db.execute("""
                        SELECT COUNT(*) FROM exercises WHERE lesson_id = ?
                    """, (lesson_id,)) as cursor:
                        exercise_count += (await cursor.fetchone())[0]
                    
                    # Count simulations
                    async with db.execute("""
                        SELECT COUNT(*) FROM simulations WHERE lesson_id = ?
                    """, (lesson_id,)) as cursor:
                        simulation_count += (await cursor.fetchone())[0]
                
                # Build sub_topics from lessons
                sub_topics = []
                for lesson_row in lesson_rows:
                    sub_topics.append({
                        "sub_topic": lesson_row["sub_topic"],
                        "description": lesson_row["description"],
                        "keywords": json.loads(lesson_row["keywords"]) if lesson_row["keywords"] else []
                    })
                
                curriculum = {
                    "id": curriculum_id,
                    "user_id": row["user_id"],
                    "metadata": {
                        "title": row["title"],
                        "description": row["description"],
                        "native_language": row["native_language"],
                        "target_language": row["target_language"],
                        "proficiency": row["proficiency"]
                    },
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "status": {
                        "curriculum": row["status"],
                        "flashcards": "completed" if flashcard_count > 0 else "pending",
                        "exercises": "completed" if exercise_count > 0 else "pending",
                        "simulation": "completed" if simulation_count > 0 else "pending"
                    },
                    "content": {
                        "curriculum": {
                            "lesson_topic": row["lesson_topic"],
                            "sub_topics": sub_topics
                        } if row["lesson_topic"] else None,
                        "flashcards": None,  # Not loaded here for performance
                        "exercises": None,   # Not loaded here for performance
                        "simulation": None   # Not loaded here for performance
                    }
                }
                
                curricula.append(curriculum)
            
            return curricula

    async def create_curriculum_record(self, user_id: int, metadata: Dict[str, Any], curriculum_id: str = None) -> str:
        """Create curriculum record without content (for background generation)"""
        if curriculum_id is None:
            curriculum_id = str(uuid.uuid4())
        
        async with self.get_lock(curriculum_id):
            async with aiosqlite.connect(self.db_path) as db:
                try:
                    await db.execute("""
                        INSERT INTO curricula (
                            id, user_id, title, description, native_language, 
                            target_language, proficiency, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        curriculum_id,
                        user_id,
                        metadata.get('title', ''),
                        metadata.get('description', ''),
                        metadata.get('native_language', ''),
                        metadata.get('target_language', ''),
                        metadata.get('proficiency', ''),
                        ContentStatus.PENDING
                    ))
                    await db.commit()
                    
                    # Verify the insertion
                    async with db.execute("SELECT id FROM curricula WHERE id = ?", (curriculum_id,)) as cursor:
                        result = await cursor.fetchone()
                        if not result:
                            raise Exception(f"Failed to insert curriculum {curriculum_id}")
                            
                except Exception as e:
                    print(f"Database insertion error: {e}")
                    raise
        
        return curriculum_id

# Global database instance
database = DatabaseManager() 