import psycopg2
import os
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

# Database Configuration from environment variables
DB_NAME = os.getenv("POSTGRES_DB", "linguaai")
DB_USER = os.getenv("POSTGRES_USER", "linguaai_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "LinguaAI1008")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# SQL Schema Definition
SCHEMA_SQL = """
-- Drop existing objects if they exist
DROP TABLE IF EXISTS user_activity_progress CASCADE;
DROP TABLE IF EXISTS activities CASCADE;
DROP TABLE IF EXISTS weekly_modules CASCADE;
DROP TABLE IF EXISTS curriculums CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TYPE IF EXISTS activity_status CASCADE;

-- Table `users`
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    native_language VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Trigger for auto-updating updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER users_update_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Table `curriculums`
CREATE TABLE curriculums (
    curriculum_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    target_language VARCHAR(50) NOT NULL,
    current_level VARCHAR(20) NOT NULL,
    learning_goal TEXT NOT NULL,
    interests JSONB NOT NULL,
    duration_weeks INT NOT NULL,
    intensity_per_week VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_curriculum_user ON curriculums(user_id, is_active);

CREATE TRIGGER curriculums_update_updated_at
    BEFORE UPDATE ON curriculums
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Table `weekly_modules`
CREATE TABLE weekly_modules (
    module_id SERIAL PRIMARY KEY,
    curriculum_id INT NOT NULL REFERENCES curriculums(curriculum_id) ON DELETE CASCADE,
    week_number INT NOT NULL,
    theme_title_native VARCHAR(255) NOT NULL,
    theme_title_target VARCHAR(255) NOT NULL,
    theme_description_native TEXT NOT NULL,
    estimated_duration_text VARCHAR(50) NOT NULL,
    learning_objectives_native JSONB NOT NULL,
    module_order INT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (curriculum_id, week_number)
);

CREATE INDEX idx_module_order ON weekly_modules(curriculum_id, module_order);

CREATE TRIGGER weekly_modules_update_updated_at
    BEFORE UPDATE ON weekly_modules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Table `activities`
CREATE TABLE activities (
    activity_id SERIAL PRIMARY KEY,
    module_id INT NOT NULL REFERENCES weekly_modules(module_id) ON DELETE CASCADE,
    blueprint_activity_id VARCHAR(50) NOT NULL,
    title_native VARCHAR(255) NOT NULL,
    title_target VARCHAR(255) NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    skill_focus JSONB NOT NULL,
    estimated_time_minutes INT NOT NULL,
    description_native TEXT NOT NULL,
    ai_helper_role TEXT,
    content_generation_prompt TEXT NOT NULL,
    success_metric_native TEXT NOT NULL,
    activity_order INT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (module_id, blueprint_activity_id)
);

CREATE INDEX idx_activity_order ON activities(module_id, activity_order);

CREATE TRIGGER activities_update_updated_at
    BEFORE UPDATE ON activities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Activity status enum
CREATE TYPE activity_status AS ENUM ('not_started', 'in_progress', 'completed', 'skipped');

-- Table `user_activity_progress`
CREATE TABLE user_activity_progress (
    progress_id BIGSERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    activity_id INT NOT NULL REFERENCES activities(activity_id) ON DELETE CASCADE,
    status activity_status NOT NULL DEFAULT 'not_started',
    started_at TIMESTAMPTZ NULL,
    completed_at TIMESTAMPTZ NULL,
    last_accessed_at TIMESTAMPTZ NULL,
    score NUMERIC(5, 2) NULL,
    user_notes TEXT NULL,
    generated_content_cache JSONB NULL,
    ai_feedback_summary TEXT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, activity_id)
);

CREATE INDEX idx_progress_user_status ON user_activity_progress(user_id, status);
CREATE INDEX idx_progress_activity ON user_activity_progress(activity_id);

CREATE TRIGGER user_activity_progress_update_updated_at
    BEFORE UPDATE ON user_activity_progress
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""

async def get_db_connection():
    """Get an async database connection."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        raise

def reset_sequences():
    """Reset all sequences (auto-incrementing IDs) to 1."""
    sequences_sql = """
    SELECT 'ALTER SEQUENCE ' || sequence_name || ' RESTART WITH 1;'
    FROM information_schema.sequences
    WHERE sequence_schema = 'public';
    """
    return sequences_sql

def reset_database(confirm=True):
    """Reset the database by dropping all tables and recreating them."""
    if confirm:
        confirm = input("WARNING: This will DELETE ALL DATA. Type 'yes' to proceed: ")
        if confirm.lower() != 'yes':
            print("Database reset cancelled.")
            return

    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = False
        print("Database connection established.")

        with conn.cursor() as cur:
            print("Dropping all tables...")
            # First drop all tables
            cur.execute(SCHEMA_SQL)
            print("Tables recreated successfully.")
            
            # Reset sequences
            cur.execute(reset_sequences())
            print("Sequences reset successfully.")

        conn.commit()
        print("Database reset complete.")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
            print("Transaction rolled back.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

# Modify the original setup_database function to be more explicit
def setup_database(confirm=True):
    """Set up the database schema without dropping existing tables."""
    if confirm:
        confirm = input("Do you want to set up the database? Type 'yes' to proceed: ")
        if confirm.lower() != 'yes':
            print("Database setup cancelled.")
            return

    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = False
        print("Database connection established.")

        with conn.cursor() as cur:
            print("Checking if tables exist...")
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    AND table_name = 'users'
                );
            """)
            tables_exist = cur.fetchone()[0]
            
            if tables_exist:
                print("Tables already exist. Use reset_database() to reset the database.")
                return
            
            print("Creating tables...")
            cur.execute(SCHEMA_SQL)
            print("Tables created successfully.")

        conn.commit()
        print("Database setup complete.")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
            print("Transaction rolled back.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    action = input("Enter 'setup' to setup database or 'reset' to reset database: ").lower()
    if action == 'reset':
        reset_database()
    elif action == 'setup':
        setup_database()
    else:
        print("Invalid action. Use 'setup' or 'reset'.")