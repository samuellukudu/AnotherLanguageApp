-- Initialize database for AI Language Tutor
-- This script runs when the PostgreSQL container starts

-- Create database (if not exists)
\c postgres
SELECT 'CREATE DATABASE ai_tutor_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ai_tutor_db')\gexec

-- Connect to our database
\c ai_tutor_db

-- Grant permissions to user
GRANT ALL PRIVILEGES ON DATABASE ai_tutor_db TO ai_tutor;
GRANT ALL PRIVILEGES ON SCHEMA public TO ai_tutor;

-- Create extension for better performance (if needed)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: Tables will be created automatically by SQLAlchemy when the app starts 