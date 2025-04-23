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
DROP TABLE IF EXISTS generated_flashcards CASCADE;
DROP TABLE IF EXISTS flashcard_sets CASCADE;
DROP TABLE IF EXISTS generated_exercises CASCADE;
DROP TABLE IF EXISTS exercise_sets CASCADE;
DROP TABLE IF EXISTS simulations CASCADE;
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

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER users_update_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Flashcard sets and items
CREATE TABLE flashcard_sets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    query TEXT NOT NULL,
    flashcards JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_flashcard_set_user ON flashcard_sets(user_id);
CREATE TRIGGER flashcard_sets_update_updated_at
    BEFORE UPDATE ON flashcard_sets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE generated_flashcards (
    flashcard_id SERIAL PRIMARY KEY,
    set_id INT NOT NULL REFERENCES flashcard_sets(id) ON DELETE CASCADE,
    word TEXT NOT NULL,
    definition TEXT NOT NULL,
    example TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_flashcard_set ON generated_flashcards(set_id);
CREATE TRIGGER generated_flashcards_update_updated_at
    BEFORE UPDATE ON generated_flashcards
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Exercise sets and items
CREATE TABLE exercise_sets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    query TEXT NOT NULL,
    exercises JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_exercise_set_user ON exercise_sets(user_id);
CREATE TRIGGER exercise_sets_update_updated_at
    BEFORE UPDATE ON exercise_sets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE generated_exercises (
    exercise_id SERIAL PRIMARY KEY,
    set_id INT NOT NULL REFERENCES exercise_sets(id) ON DELETE CASCADE,
    sentence TEXT NOT NULL,
    answer TEXT NOT NULL,
    choices JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_exercise_set ON generated_exercises(set_id);
CREATE TRIGGER generated_exercises_update_updated_at
    BEFORE UPDATE ON generated_exercises
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Simulations
CREATE TABLE simulations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    query TEXT NOT NULL,
    scenario TEXT NOT NULL,
    dialog JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_simulation_user ON simulations(user_id);
CREATE TRIGGER simulations_update_updated_at
    BEFORE UPDATE ON simulations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Query logs for tracking user queries
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    query_type VARCHAR(50) NOT NULL,
    query TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_query_logs_user ON query_logs(user_id);
"""

def get_db_connection():
    """Get a synchronous database connection."""
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
    """Generate SQL to reset all sequences to 1."""
    return "SELECT 'ALTER SEQUENCE ' || sequence_name || ' RESTART WITH 1;' FROM information_schema.sequences WHERE sequence_schema = 'public';"

def reset_database(confirm=True):
    """Reset the database by dropping all tables and recreating them."""
    if confirm:
        ans = input("WARNING: This will DELETE ALL DATA. Type 'yes' to proceed: ")
        if ans.lower() != 'yes':
            print("Cancelled.")
            return

    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
            reset_sql = reset_sequences()
            cur.execute(reset_sql)
            for cmd in cur.fetchall():
                cur.execute(cmd[0])
        conn.commit()
        print("Database reset complete.")
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def view_tables():
    """Print all tables in the public schema."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        tables = cur.fetchall()
        print("Tables in public schema:")
        for t in tables:
            print(f"- {t[0]}")
    conn.close()

if __name__ == "__main__":
    action = input("Enter 'reset' or 'view': ").lower()
    if action == 'reset':
        reset_database()
    elif action == 'view':
        view_tables()
    else:
        print("Usage: enter 'reset' to drop/recreate schema, or 'view' to list tables.")
