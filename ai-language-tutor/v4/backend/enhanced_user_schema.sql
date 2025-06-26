-- =====================================================
-- ENHANCED USER MANAGEMENT SCHEMA
-- =====================================================
-- This schema extends the basic users table with comprehensive user management features

-- Drop existing users table if you want to recreate with enhanced schema
-- DROP TABLE IF EXISTS users CASCADE;

-- Enhanced users table with comprehensive user management features
CREATE TABLE IF NOT EXISTS users (
    -- Core identity
    id UUID PRIMARY KEY DEFAULT auth.uid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE,
    display_name VARCHAR(100),
    bio TEXT,
    
    -- Language learning specific
    native_language VARCHAR(10), -- ISO language code (e.g., 'en', 'es')
    target_languages JSONB DEFAULT '[]', -- Array of target languages
    
    -- Progress tracking
    xp INTEGER NOT NULL DEFAULT 0,
    streak INTEGER NOT NULL DEFAULT 0,
    longest_streak INTEGER NOT NULL DEFAULT 0,
    daily_goal INTEGER NOT NULL DEFAULT 50, -- Daily XP goal
    total_lessons_completed INTEGER NOT NULL DEFAULT 0,
    total_time_spent INTEGER NOT NULL DEFAULT 0, -- in minutes
    achievements JSONB DEFAULT '[]', -- Array of achievement IDs
    
    -- User preferences
    timezone VARCHAR(50), -- e.g., 'America/New_York'
    notification_preferences JSONB DEFAULT '{
        "push_notifications": true,
        "email_notifications": true,
        "reminder_time": "19:00",
        "reminder_days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
    }',
    learning_preferences JSONB DEFAULT '{
        "theme": "light",
        "sound_enabled": true,
        "interface_language": "en",
        "auto_speak": false,
        "speaking_exercises": true
    }',
    
    -- Account status
    email_verified BOOLEAN DEFAULT false,
    account_status VARCHAR(20) DEFAULT 'active', -- active, suspended, deleted
    privacy_settings JSONB DEFAULT '{
        "profile_public": false,
        "show_progress": true,
        "allow_friend_requests": true
    }',
    
    -- Activity tracking
    last_active TIMESTAMP WITH TIME ZONE,
    last_lesson_date DATE,
    login_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Additional tables for enhanced user management

-- User sessions table for device management
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) NOT NULL,
    device_info JSONB DEFAULT '{}', -- browser, OS, IP, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT true
);

-- Password reset tokens table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User learning goals table
CREATE TABLE IF NOT EXISTS user_goals (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    goal_type VARCHAR(50) NOT NULL, -- daily_xp, weekly_lessons, monthly_streak
    target_value INTEGER NOT NULL,
    current_value INTEGER DEFAULT 0,
    start_date DATE NOT NULL,
    end_date DATE,
    completed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User activity log for analytics
CREATE TABLE IF NOT EXISTS user_activity_log (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL, -- login, lesson_start, lesson_complete, etc.
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- ADD NEW COLUMNS TO EXISTING USERS TABLE (Migration)
-- =====================================================
-- Run this if you already have a users table and want to add new columns

/*
-- Add new columns to existing users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS display_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS bio TEXT,
ADD COLUMN IF NOT EXISTS native_language VARCHAR(10),
ADD COLUMN IF NOT EXISTS target_languages JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS longest_streak INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS daily_goal INTEGER NOT NULL DEFAULT 50,
ADD COLUMN IF NOT EXISTS total_lessons_completed INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_time_spent INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS achievements JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS timezone VARCHAR(50),
ADD COLUMN IF NOT EXISTS notification_preferences JSONB DEFAULT '{"push_notifications": true, "email_notifications": true, "reminder_time": "19:00"}',
ADD COLUMN IF NOT EXISTS learning_preferences JSONB DEFAULT '{"theme": "light", "sound_enabled": true, "interface_language": "en"}',
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS account_status VARCHAR(20) DEFAULT 'active',
ADD COLUMN IF NOT EXISTS privacy_settings JSONB DEFAULT '{"profile_public": false, "show_progress": true}',
ADD COLUMN IF NOT EXISTS last_active TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS last_lesson_date DATE,
ADD COLUMN IF NOT EXISTS login_count INTEGER DEFAULT 0;

-- Update existing preferences column data if it exists
UPDATE users 
SET 
    notification_preferences = COALESCE(notification_preferences, '{"push_notifications": true, "email_notifications": true, "reminder_time": "19:00"}'::jsonb),
    learning_preferences = COALESCE(learning_preferences, '{"theme": "light", "sound_enabled": true, "interface_language": "en"}'::jsonb),
    achievements = COALESCE(achievements, '[]'::jsonb),
    target_languages = COALESCE(target_languages, '[]'::jsonb)
WHERE notification_preferences IS NULL OR learning_preferences IS NULL;
*/

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_users_last_active ON users (last_active);
CREATE INDEX IF NOT EXISTS idx_users_streak ON users (streak);
CREATE INDEX IF NOT EXISTS idx_users_xp ON users (xp);
CREATE INDEX IF NOT EXISTS idx_users_account_status ON users (account_status);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions (user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens (token);
CREATE INDEX IF NOT EXISTS idx_user_goals_user_id ON user_goals (user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity_log (user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_type ON user_activity_log (activity_type);

-- =====================================================
-- TRIGGERS
-- =====================================================
CREATE OR REPLACE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

-- =====================================================
-- ROW LEVEL SECURITY POLICIES
-- =====================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE password_reset_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_activity_log ENABLE ROW LEVEL SECURITY;

-- Users table policies
DROP POLICY IF EXISTS "Users can view own profile" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;
DROP POLICY IF EXISTS "Users can insert own profile" ON users;

CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- User sessions policies
CREATE POLICY "Users can view own sessions" ON user_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own sessions" ON user_sessions
    FOR ALL USING (auth.uid() = user_id);

-- Password reset tokens policies (service role only)
CREATE POLICY "Service can manage reset tokens" ON password_reset_tokens
    FOR ALL USING (auth.role() = 'service_role');

-- User goals policies
CREATE POLICY "Users can view own goals" ON user_goals
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own goals" ON user_goals
    FOR ALL USING (auth.uid() = user_id);

-- User activity log policies
CREATE POLICY "Users can view own activity" ON user_activity_log
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service can log activity" ON user_activity_log
    FOR INSERT WITH CHECK (auth.role() = 'service_role' OR auth.uid() = user_id);

-- =====================================================
-- GRANT PERMISSIONS
-- =====================================================
GRANT ALL ON users TO authenticated;
GRANT ALL ON users TO service_role;
GRANT ALL ON user_sessions TO authenticated;
GRANT ALL ON user_sessions TO service_role;
GRANT ALL ON password_reset_tokens TO service_role;
GRANT ALL ON user_goals TO authenticated;
GRANT ALL ON user_goals TO service_role;
GRANT ALL ON user_activity_log TO authenticated;
GRANT ALL ON user_activity_log TO service_role;

-- Grant sequence permissions
GRANT USAGE, SELECT ON SEQUENCE user_goals_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE user_goals_id_seq TO service_role;
GRANT USAGE, SELECT ON SEQUENCE user_activity_log_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE user_activity_log_id_seq TO service_role; 