import psycopg2
import os

def setup_database():
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "linguaai"),
        user=os.getenv("POSTGRES_USER", "linguaai_user"),
        password=os.getenv("POSTGRES_PASSWORD", "LinguaAI1008"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )
    
    cur = conn.cursor()

    # Drop existing tables if they exist
    cur.execute("""
    DROP TABLE IF EXISTS curriculum_data CASCADE;
    DROP TABLE IF EXISTS user_progress CASCADE;
    DROP TABLE IF EXISTS daily_lessons CASCADE;
    DROP TABLE IF EXISTS lessons CASCADE;
    DROP TABLE IF EXISTS curriculums CASCADE;
    DROP TABLE IF EXISTS users CASCADE;
    """)

    # Create Tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email TEXT UNIQUE NOT NULL,
        name TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS curriculums (
        id SERIAL PRIMARY KEY,
        prompt TEXT NOT NULL,
        user_id UUID NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS lessons (
        id SERIAL PRIMARY KEY,
        curriculum_id INT REFERENCES curriculums(id) ON DELETE CASCADE,
        week_number INT NOT NULL CHECK (week_number >= 0),
        content JSONB NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(curriculum_id, week_number)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS daily_lessons (
        id SERIAL PRIMARY KEY,
        lesson_id INT REFERENCES lessons(id) ON DELETE CASCADE,
        day_number INT NOT NULL CHECK (day_number BETWEEN 0 AND 6),
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(lesson_id, day_number)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_progress (
        id SERIAL PRIMARY KEY,
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        lesson_id INT REFERENCES lessons(id) ON DELETE CASCADE,
        daily_lesson_id INT REFERENCES daily_lessons(id) ON DELETE CASCADE,
        status VARCHAR(20) CHECK (status IN ('not started', 'in progress', 'completed')) DEFAULT 'not started',
        progress_percentage DECIMAL(5,2) CHECK (progress_percentage BETWEEN 0 AND 100) DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, lesson_id, daily_lesson_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS curriculum_data (
        id SERIAL PRIMARY KEY,
        curriculum_id INT REFERENCES curriculums(id) ON DELETE CASCADE,
        language TEXT,
        learning_goal TEXT,
        current_level TEXT,
        weeks JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(curriculum_id)
    );
    """)

    # Create Indexes for Optimization
    cur.execute("CREATE INDEX IF NOT EXISTS idx_curriculum_id ON lessons(curriculum_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_lesson_id ON daily_lessons(lesson_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_user_progress ON user_progress(user_id, lesson_id, daily_lesson_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_status_progress ON user_progress(status, progress_percentage);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_curriculum_data ON curriculum_data(curriculum_id);")

    conn.commit()
    cur.close()
    conn.close()
    print("Database schema created successfully!")

if __name__ == "__main__":
    setup_database()