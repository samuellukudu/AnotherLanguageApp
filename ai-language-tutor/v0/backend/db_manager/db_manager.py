import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os
from uuid import UUID, uuid4
import time

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cur = None
        self.connect()

    def connect(self):
        retries = 5
        while retries > 0:
            try:
                self.conn = psycopg2.connect(
                    dbname=os.getenv("POSTGRES_DB", "linguaai"),
                    user=os.getenv("POSTGRES_USER", "linguaai_user"),
                    password=os.getenv("POSTGRES_PASSWORD", "LinguaAI1008"),
                    host=os.getenv("DB_HOST", "db"),  # Default to 'db' instead of 'localhost'
                    port=os.getenv("DB_PORT", "5432")
                )
                self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
                print("Database connection successful!")
                return
            except Exception as e:
                print(f"Database connection error: {str(e)}")
                retries -= 1
                if retries > 0:
                    time.sleep(2)
                else:
                    raise e

    def create_user(self, email, name=None):
        """Create a new user and return their UUID"""
        try:
            user_id = str(uuid4())
            self.cur.execute(
                "INSERT INTO users (id, email, name) VALUES (%s, %s, %s) RETURNING id",
                (user_id, email, name)
            )
            result = self.cur.fetchone()
            self.conn.commit()
            return result['id']
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_user(self, user_id):
        """Get user by UUID string"""
        if not user_id:
            return None
        try:
            # Validate UUID format
            uuid_obj = UUID(str(user_id))
            self.cur.execute("SELECT * FROM users WHERE id = %s", (str(uuid_obj),))
            return self.cur.fetchone()
        except (ValueError, TypeError):
            return None

    def save_curriculum(self, user_id, prompt, curriculum_data):
        try:
            # Insert curriculum with prompt only
            self.cur.execute(
                "INSERT INTO curriculums (prompt) VALUES (%s) RETURNING id",
                (prompt,)
            )
            curriculum_id = self.cur.fetchone()['id']
            
            # Save curriculum data
            self.cur.execute(
                """
                INSERT INTO curriculum_data 
                (curriculum_id, language, learning_goal, current_level, weeks) 
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    curriculum_id,
                    curriculum_data.get('language'),
                    curriculum_data.get('learning_goal'),
                    curriculum_data.get('current_level'),
                    json.dumps(curriculum_data.get('weeks', []))
                )
            )
            
            self.conn.commit()
            return curriculum_id
        except Exception as e:
            self.conn.rollback()
            print(f"Database error: {str(e)}")
            raise e

    def save_lesson(self, curriculum_id, week_number, lesson_data):
        try:
            self.cur.execute(
                "INSERT INTO lessons (curriculum_id, week_number, content) VALUES (%s, %s, %s) RETURNING id",
                (curriculum_id, week_number, json.dumps(lesson_data))
            )
            lesson_id = self.cur.fetchone()['id']
            self.conn.commit()
            return lesson_id
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_curriculum(self, curriculum_id):
        self.cur.execute(
            """
            SELECT c.*, json_build_object(
                'language', cd.language,
                'learning_goal', cd.learning_goal,
                'current_level', cd.current_level,
                'weeks', cd.weeks
            ) as content
            FROM curriculums c
            LEFT JOIN curriculum_data cd ON c.id = cd.curriculum_id
            WHERE c.id = %s
            """,
            (curriculum_id,)
        )
        return self.cur.fetchone()

    def get_lesson(self, curriculum_id, week_number):
        self.cur.execute(
            "SELECT content FROM lessons WHERE curriculum_id = %s AND week_number = %s",
            (curriculum_id, week_number)
        )
        result = self.cur.fetchone()
        return json.loads(result['content']) if result else None

    def list_curriculums(self):
        """List all curriculums with their data"""
        self.cur.execute(
            """
            SELECT c.id, c.prompt, c.created_at,
                   cd.language, cd.learning_goal, cd.current_level
            FROM curriculums c
            LEFT JOIN curriculum_data cd ON c.id = cd.curriculum_id
            ORDER BY c.created_at DESC
            """
        )
        return self.cur.fetchall()

    def list_curriculum_lessons(self, curriculum_id):
        """List all lessons for a curriculum"""
        self.cur.execute(
            """
            SELECT id, week_number, content, created_at
            FROM lessons
            WHERE curriculum_id = %s
            ORDER BY week_number
            """,
            (curriculum_id,)
        )
        return self.cur.fetchall()

    def get_daily_lessons(self, lesson_id):
        """Get daily lessons for a lesson"""
        self.cur.execute(
            """
            SELECT id, day_number, content, created_at
            FROM daily_lessons
            WHERE lesson_id = %s
            ORDER BY day_number
            """,
            (lesson_id,)
        )
        return self.cur.fetchall()

    def __del__(self):
        try:
            if self.cur:
                self.cur.close()
            if self.conn:
                self.conn.close()
        except Exception:
            pass
