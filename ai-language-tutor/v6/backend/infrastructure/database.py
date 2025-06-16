import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import logging
from backend.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQL Schema Definition
SCHEMA_SQL = """
-- Drop existing objects if they exist
DROP TABLE IF EXISTS user_activity_progress CASCADE;
DROP TABLE IF EXISTS activities CASCADE;
DROP TABLE IF EXISTS weekly_modules CASCADE;
DROP TABLE IF EXISTS curriculums CASCADE;
DROP TABLE IF EXISTS generated_flashcards CASCADE;
DROP TABLE IF EXISTS flashcard_sets CASCADE;          -- Corrected name
DROP TABLE IF EXISTS generated_exercises CASCADE;
DROP TABLE IF EXISTS exercise_sets CASCADE;           -- Corrected name
DROP TABLE IF EXISTS simulations CASCADE;             -- Corrected name
DROP TABLE IF EXISTS users CASCADE;
DROP TYPE IF EXISTS activity_status CASCADE;

-- Table `users`
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for users
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""

async def get_db_connection():
    """
    Creates and returns a database connection.
    """
    try:
        conn = psycopg2.connect(
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            cursor_factory=RealDictCursor
        )
        logger.info("Database connection established successfully")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise

async def initialize_database():
    """
    Initializes the database with the required schema.
    """
    try:
        conn = await get_db_connection()
        cursor = conn.cursor()
        cursor.execute(SCHEMA_SQL)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Database schema initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database schema: {e}")
        raise