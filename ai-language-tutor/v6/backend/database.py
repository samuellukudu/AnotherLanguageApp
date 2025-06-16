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
-- Note: Some drops below might be for tables not defined in this specific script.
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

-- Trigger function (remains the same)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for users (remains the same)
CREATE TRIGGER users_update_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================
-- Tables for Generated Content (Flashcards)
-- ============================================

-- Table `flashcard_sets` (Represents one request/query)
CREATE TABLE flashcard_sets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id), -- Added FK reference for completeness
    query TEXT NOT NULL,
    flashcards JSONB NOT NULL,  -- Stores an array of 5 flashcards
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP -- Added updated_at for consistency
);

CREATE INDEX idx_flashcard_set_user ON flashcard_sets(user_id);

-- Corrected Trigger definition for flashcard_sets
CREATE TRIGGER flashcard_sets_update_updated_at      -- Renamed trigger
    BEFORE UPDATE ON flashcard_sets                  -- Corrected table name
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();     -- Assumes you want updated_at here too

-- Table `generated_flashcards` (Individual flashcards within a set)
CREATE TABLE generated_flashcards (
    flashcard_id SERIAL PRIMARY KEY,
    set_id INT NOT NULL REFERENCES flashcard_sets(id) ON DELETE CASCADE, -- Corrected FK reference (table and column)
    word TEXT NOT NULL,
    definition TEXT NOT NULL,
    example TEXT, -- Example might be optional
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_flashcard_set ON generated_flashcards(set_id);

-- Trigger for generated_flashcards (remains the same)
CREATE TRIGGER generated_flashcards_update_updated_at
    BEFORE UPDATE ON generated_flashcards
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================
-- Tables for Generated Content (Exercises)
-- ============================================

-- Table `exercise_sets` (Represents one request/query) -- Corrected comment
CREATE TABLE exercise_sets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id), -- Added FK reference for completeness
    query TEXT NOT NULL,
    exercises JSONB NOT NULL,  -- Array of 5 exercises
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP -- Added updated_at for consistency
);

CREATE INDEX idx_exercise_set_user ON exercise_sets(user_id); -- Corrected table name (was already correct but double-checked)

-- Corrected Trigger definition for exercise_sets
CREATE TRIGGER exercise_sets_update_updated_at       -- Renamed trigger
    BEFORE UPDATE ON exercise_sets                   -- Corrected table name
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();      -- Assumes you want updated_at here too

-- Table `generated_exercises` (Individual exercises within a set)
CREATE TABLE generated_exercises (
    exercise_id SERIAL PRIMARY KEY,
    set_id INT NOT NULL REFERENCES exercise_sets(id) ON DELETE CASCADE, -- Corrected FK reference (table and column)
    sentence TEXT NOT NULL,
    answer TEXT NOT NULL,
    choices JSONB NOT NULL, -- Storing the array of choices
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_exercise_set ON generated_exercises(set_id);

-- Trigger for generated_exercises (remains the same)
CREATE TRIGGER generated_exercises_update_updated_at
    BEFORE UPDATE ON generated_exercises
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================
-- Table for Generated Content (Simulations)
-- ============================================

-- Table `simulations` (Represents one simulation request/result) -- Corrected comment
CREATE TABLE simulations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id), -- Added FK reference for completeness
    query TEXT NOT NULL,
    scenario TEXT NOT NULL,
    dialog JSONB NOT NULL,  -- Array of turns with 'role', 'chinese', 'pinyin', 'english'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP -- Added updated_at for consistency
);

CREATE INDEX idx_simulation_user ON simulations(user_id); -- Corrected table name

-- Corrected Trigger definition for simulations
CREATE TRIGGER simulations_update_updated_at       -- Renamed trigger
    BEFORE UPDATE ON simulations                   -- Corrected table name
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();      -- Assumes you want updated_at here too
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
    """Generate SQL to reset all sequences (auto-incrementing IDs) to 1."""
    sequences_sql = """
    SELECT 'ALTER SEQUENCE ' || sequence_name || ' RESTART WITH 1;'
    FROM information_schema.sequences
    WHERE sequence_schema = 'public';
    """
    return sequences_sql

def reset_database(confirm=True):
    """Reset the database by dropping all tables and recreating them."""
    if confirm:
        user_confirm = input("WARNING: This will DELETE ALL DATA. Type 'yes' to proceed: ")
        if user_confirm.lower() != 'yes':
            print("Database reset cancelled.")
            return

    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = False
        print("Database connection established.")

        with conn.cursor() as cur:
            print("Dropping and recreating schema...")
            # Execute the main schema SQL (includes drops)
            cur.execute(SCHEMA_SQL)
            print("Schema recreated successfully.")

            # Generate and execute sequence reset SQL
            print("Resetting sequences...")
            reset_sql_query = reset_sequences()
            cur.execute(reset_sql_query)
            reset_commands = cur.fetchall()
            for command in reset_commands:
                cur.execute(command[0])
            print("Sequences reset successfully.")

        conn.commit()
        print("Database reset complete.")

    except psycopg2.Error as e:
        print(f"Database error during reset: {e}")
        if conn:
            conn.rollback()
            print("Transaction rolled back.")
    except Exception as e:
        print(f"An unexpected error occurred during reset: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

def setup_database(confirm=True):
    """Set up the database schema if tables do not exist."""
    if confirm:
        user_confirm = input("Do you want to set up the database? Type 'yes' to proceed: ")
        if user_confirm.lower() != 'yes':
            print("Database setup cancelled.")
            return

    conn = None
    try:
        conn = get_db_connection()
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
                print("Tables already exist. Use reset_database() to reset the database or run setup with confirm=False.")
                conn.rollback() # Rollback as no changes should be made
                return

            print("Creating schema...")
            cur.execute(SCHEMA_SQL)
            print("Schema created successfully.")

        conn.commit()
        print("Database setup complete.")

    except psycopg2.Error as e:
        print(f"Database error during setup: {e}")
        if conn:
            conn.rollback()
            print("Transaction rolled back.")
    except Exception as e:
        print(f"An unexpected error occurred during setup: {e}")
        if conn:
            conn.rollback()
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