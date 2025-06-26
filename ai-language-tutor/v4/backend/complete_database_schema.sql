-- =====================================================
-- COMPLETE DATABASE SCHEMA FOR AI LANGUAGE TUTOR
-- =====================================================
-- This schema is designed for Supabase with proper RLS policies
-- Includes comprehensive user management features

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- =====================================================
-- ENHANCED USERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    -- Core identity
    id UUID PRIMARY KEY DEFAULT auth.uid(), -- Use Supabase auth user ID
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
    
    -- Legacy field for backward compatibility
    preferences JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- USER MANAGEMENT TABLES
-- =====================================================

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
-- CURRICULUMS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS curriculums (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE, -- Changed to CASCADE and NOT NULL
    title VARCHAR(255) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- LESSONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS lessons (
    id SERIAL PRIMARY KEY,
    curriculum_id INTEGER NOT NULL REFERENCES curriculums(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content JSONB DEFAULT '{}',
    lesson_order INTEGER DEFAULT 1, -- Added for ordering lessons
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- FLASHCARDS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS flashcards (
    id SERIAL PRIMARY KEY,
    curriculum_id INTEGER NOT NULL REFERENCES curriculums(id) ON DELETE CASCADE,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    difficulty VARCHAR(20) DEFAULT 'medium', -- Added difficulty level
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- EXERCISES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS exercises (
    id SERIAL PRIMARY KEY,
    curriculum_id INTEGER NOT NULL REFERENCES curriculums(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    exercise_type VARCHAR(50) DEFAULT 'multiple_choice', -- Added exercise type
    options JSONB DEFAULT '[]', -- For multiple choice options
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- SIMULATIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS simulations (
    id SERIAL PRIMARY KEY,
    curriculum_id INTEGER NOT NULL REFERENCES curriculums(id) ON DELETE CASCADE,
    scenario TEXT NOT NULL,
    simulation_type VARCHAR(50) DEFAULT 'conversation', -- Added simulation type
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- UPDATED_AT TRIGGERS
-- =====================================================
CREATE OR REPLACE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

CREATE OR REPLACE TRIGGER update_curriculums_updated_at 
    BEFORE UPDATE ON curriculums 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

CREATE OR REPLACE TRIGGER update_lessons_updated_at 
    BEFORE UPDATE ON lessons 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

CREATE OR REPLACE TRIGGER update_flashcards_updated_at 
    BEFORE UPDATE ON flashcards 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

CREATE OR REPLACE TRIGGER update_exercises_updated_at 
    BEFORE UPDATE ON exercises 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

CREATE OR REPLACE TRIGGER update_simulations_updated_at 
    BEFORE UPDATE ON simulations 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- User table indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_users_last_active ON users (last_active);
CREATE INDEX IF NOT EXISTS idx_users_streak ON users (streak);
CREATE INDEX IF NOT EXISTS idx_users_xp ON users (xp);
CREATE INDEX IF NOT EXISTS idx_users_account_status ON users (account_status);

-- User management table indexes
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions (user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens (token);
CREATE INDEX IF NOT EXISTS idx_user_goals_user_id ON user_goals (user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity_log (user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_type ON user_activity_log (activity_type);

-- Learning content table indexes
CREATE INDEX IF NOT EXISTS idx_curriculums_user_id ON curriculums (user_id);
CREATE INDEX IF NOT EXISTS idx_curriculums_created_at ON curriculums (created_at);
CREATE INDEX IF NOT EXISTS idx_lessons_curriculum_id ON lessons (curriculum_id);
CREATE INDEX IF NOT EXISTS idx_lessons_order ON lessons (curriculum_id, lesson_order);
CREATE INDEX IF NOT EXISTS idx_flashcards_curriculum_id ON flashcards (curriculum_id);
CREATE INDEX IF NOT EXISTS idx_exercises_curriculum_id ON exercises (curriculum_id);
CREATE INDEX IF NOT EXISTS idx_simulations_curriculum_id ON simulations (curriculum_id);

-- =====================================================
-- ENABLE ROW LEVEL SECURITY (RLS)
-- =====================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE password_reset_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_activity_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE curriculums ENABLE ROW LEVEL SECURITY;
ALTER TABLE lessons ENABLE ROW LEVEL SECURITY;
ALTER TABLE flashcards ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercises ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulations ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- DROP EXISTING POLICIES (Clean slate)
-- =====================================================
DROP POLICY IF EXISTS "Users can view own profile" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;
DROP POLICY IF EXISTS "Users can insert own profile" ON users;
DROP POLICY IF EXISTS "Allow all operations" ON users;

DROP POLICY IF EXISTS "Users can view own sessions" ON user_sessions;
DROP POLICY IF EXISTS "Users can manage own sessions" ON user_sessions;
DROP POLICY IF EXISTS "Service can manage reset tokens" ON password_reset_tokens;
DROP POLICY IF EXISTS "Users can view own goals" ON user_goals;
DROP POLICY IF EXISTS "Users can manage own goals" ON user_goals;
DROP POLICY IF EXISTS "Users can view own activity" ON user_activity_log;
DROP POLICY IF EXISTS "Service can log activity" ON user_activity_log;

DROP POLICY IF EXISTS "Users can view own curriculums" ON curriculums;
DROP POLICY IF EXISTS "Users can create own curriculums" ON curriculums;
DROP POLICY IF EXISTS "Users can update own curriculums" ON curriculums;
DROP POLICY IF EXISTS "Users can delete own curriculums" ON curriculums;
DROP POLICY IF EXISTS "Allow all operations" ON curriculums;

DROP POLICY IF EXISTS "Users can view curriculum lessons" ON lessons;
DROP POLICY IF EXISTS "Users can manage curriculum lessons" ON lessons;
DROP POLICY IF EXISTS "Allow all operations" ON lessons;

DROP POLICY IF EXISTS "Users can view curriculum flashcards" ON flashcards;
DROP POLICY IF EXISTS "Users can manage curriculum flashcards" ON flashcards;
DROP POLICY IF EXISTS "Allow all operations" ON flashcards;

DROP POLICY IF EXISTS "Users can view curriculum exercises" ON exercises;
DROP POLICY IF EXISTS "Users can manage curriculum exercises" ON exercises;
DROP POLICY IF EXISTS "Allow all operations" ON exercises;

DROP POLICY IF EXISTS "Users can view curriculum simulations" ON simulations;
DROP POLICY IF EXISTS "Users can manage curriculum simulations" ON simulations;
DROP POLICY IF EXISTS "Allow all operations" ON simulations;

-- =====================================================
-- SECURE ROW LEVEL SECURITY POLICIES
-- =====================================================

-- USERS TABLE POLICIES
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- USER SESSIONS POLICIES
CREATE POLICY "Users can view own sessions" ON user_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own sessions" ON user_sessions
    FOR ALL USING (auth.uid() = user_id);

-- PASSWORD RESET TOKENS POLICIES (service role only)
CREATE POLICY "Service can manage reset tokens" ON password_reset_tokens
    FOR ALL USING (auth.role() = 'service_role');

-- USER GOALS POLICIES
CREATE POLICY "Users can view own goals" ON user_goals
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own goals" ON user_goals
    FOR ALL USING (auth.uid() = user_id);

-- USER ACTIVITY LOG POLICIES
CREATE POLICY "Users can view own activity" ON user_activity_log
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service can log activity" ON user_activity_log
    FOR INSERT WITH CHECK (auth.role() = 'service_role' OR auth.uid() = user_id);

-- CURRICULUMS TABLE POLICIES
CREATE POLICY "Users can view own curriculums" ON curriculums
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own curriculums" ON curriculums
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own curriculums" ON curriculums
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own curriculums" ON curriculums
    FOR DELETE USING (auth.uid() = user_id);

-- LESSONS TABLE POLICIES
CREATE POLICY "Users can view curriculum lessons" ON lessons
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM curriculums 
            WHERE curriculums.id = lessons.curriculum_id 
            AND curriculums.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can manage curriculum lessons" ON lessons
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM curriculums 
            WHERE curriculums.id = lessons.curriculum_id 
            AND curriculums.user_id = auth.uid()
        )
    );

-- FLASHCARDS TABLE POLICIES
CREATE POLICY "Users can view curriculum flashcards" ON flashcards
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM curriculums 
            WHERE curriculums.id = flashcards.curriculum_id 
            AND curriculums.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can manage curriculum flashcards" ON flashcards
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM curriculums 
            WHERE curriculums.id = flashcards.curriculum_id 
            AND curriculums.user_id = auth.uid()
        )
    );

-- EXERCISES TABLE POLICIES
CREATE POLICY "Users can view curriculum exercises" ON exercises
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM curriculums 
            WHERE curriculums.id = exercises.curriculum_id 
            AND curriculums.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can manage curriculum exercises" ON exercises
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM curriculums 
            WHERE curriculums.id = exercises.curriculum_id 
            AND curriculums.user_id = auth.uid()
        )
    );

-- SIMULATIONS TABLE POLICIES
CREATE POLICY "Users can view curriculum simulations" ON simulations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM curriculums 
            WHERE curriculums.id = simulations.curriculum_id 
            AND curriculums.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can manage curriculum simulations" ON simulations
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM curriculums 
            WHERE curriculums.id = simulations.curriculum_id 
            AND curriculums.user_id = auth.uid()
        )
    );

-- =====================================================
-- GRANT PERMISSIONS
-- =====================================================

-- Users table permissions
GRANT ALL ON users TO authenticated;
GRANT ALL ON users TO service_role;

-- User management table permissions
GRANT ALL ON user_sessions TO authenticated;
GRANT ALL ON user_sessions TO service_role;
GRANT ALL ON password_reset_tokens TO service_role;
GRANT ALL ON user_goals TO authenticated;
GRANT ALL ON user_goals TO service_role;
GRANT ALL ON user_activity_log TO authenticated;
GRANT ALL ON user_activity_log TO service_role;

-- Learning content table permissions
GRANT ALL ON curriculums TO authenticated;
GRANT ALL ON curriculums TO service_role;
GRANT ALL ON lessons TO authenticated;
GRANT ALL ON lessons TO service_role;
GRANT ALL ON flashcards TO authenticated;
GRANT ALL ON flashcards TO service_role;
GRANT ALL ON exercises TO authenticated;
GRANT ALL ON exercises TO service_role;
GRANT ALL ON simulations TO authenticated;
GRANT ALL ON simulations TO service_role;

-- Grant sequence permissions
GRANT USAGE, SELECT ON SEQUENCE user_goals_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE user_goals_id_seq TO service_role;
GRANT USAGE, SELECT ON SEQUENCE user_activity_log_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE user_activity_log_id_seq TO service_role;
GRANT USAGE, SELECT ON SEQUENCE curriculums_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE curriculums_id_seq TO service_role;
GRANT USAGE, SELECT ON SEQUENCE lessons_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE lessons_id_seq TO service_role;
GRANT USAGE, SELECT ON SEQUENCE flashcards_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE flashcards_id_seq TO service_role;
GRANT USAGE, SELECT ON SEQUENCE exercises_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE exercises_id_seq TO service_role;
GRANT USAGE, SELECT ON SEQUENCE simulations_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE simulations_id_seq TO service_role;

-- =====================================================
-- SAMPLE DATA INSERTION (Optional - for testing)
-- =====================================================
-- Uncomment the following to add sample data

/*
-- Sample user (this will be created automatically via Supabase Auth)
-- INSERT INTO users (id, email, username, xp, streak) VALUES 
-- ('de126f47-59e8-49b3-abe4-6c409a48b773', 'samu01@gmail.com', 'samu01', 100, 5);

-- Sample curriculum
-- INSERT INTO curriculums (user_id, title, metadata) VALUES 
-- ('de126f47-59e8-49b3-abe4-6c409a48b773', 'Spanish for Beginners', '{"native_language": "English", "target_language": "Spanish", "proficiency": "beginner"}');
*/

-- =====================================================
-- VERIFICATION QUERIES (Optional - run to verify)
-- =====================================================
-- Check if all tables exist
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;

-- Check if all RLS policies are enabled
-- SELECT schemaname, tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';

-- Check all policies
-- SELECT schemaname, tablename, policyname FROM pg_policies WHERE schemaname = 'public';

-- =====================================================
-- SMART DATABASE MIGRATION SCRIPT
-- =====================================================
-- This section handles both new and existing databases intelligently

-- Check if columns exist before adding them (prevents errors)
DO $$
BEGIN
    -- Add display_name column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'display_name') THEN
        ALTER TABLE users ADD COLUMN display_name VARCHAR(100);
    END IF;
    
    -- Add bio column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'bio') THEN
        ALTER TABLE users ADD COLUMN bio TEXT;
    END IF;
    
    -- Add native_language column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'native_language') THEN
        ALTER TABLE users ADD COLUMN native_language VARCHAR(10);
    END IF;
    
    -- Add target_languages column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'target_languages') THEN
        ALTER TABLE users ADD COLUMN target_languages JSONB DEFAULT '[]';
    END IF;
    
    -- Add longest_streak column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'longest_streak') THEN
        ALTER TABLE users ADD COLUMN longest_streak INTEGER DEFAULT 0;
    END IF;
    
    -- Add daily_goal column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'daily_goal') THEN
        ALTER TABLE users ADD COLUMN daily_goal INTEGER DEFAULT 50;
    END IF;
    
    -- Add total_lessons_completed column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'total_lessons_completed') THEN
        ALTER TABLE users ADD COLUMN total_lessons_completed INTEGER DEFAULT 0;
    END IF;
    
    -- Add total_time_spent column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'total_time_spent') THEN
        ALTER TABLE users ADD COLUMN total_time_spent INTEGER DEFAULT 0;
    END IF;
    
    -- Add achievements column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'achievements') THEN
        ALTER TABLE users ADD COLUMN achievements JSONB DEFAULT '[]';
    END IF;
    
    -- Add timezone column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'timezone') THEN
        ALTER TABLE users ADD COLUMN timezone VARCHAR(50);
    END IF;
    
    -- Add notification_preferences column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'notification_preferences') THEN
        ALTER TABLE users ADD COLUMN notification_preferences JSONB DEFAULT '{"push_notifications": true, "email_notifications": true, "reminder_time": "19:00"}';
    END IF;
    
    -- Add learning_preferences column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'learning_preferences') THEN
        ALTER TABLE users ADD COLUMN learning_preferences JSONB DEFAULT '{"theme": "light", "sound_enabled": true, "interface_language": "en"}';
    END IF;
    
    -- Add email_verified column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'email_verified') THEN
        ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT false;
    END IF;
    
    -- Add account_status column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'account_status') THEN
        ALTER TABLE users ADD COLUMN account_status VARCHAR(20) DEFAULT 'active';
    END IF;
    
    -- Add privacy_settings column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'privacy_settings') THEN
        ALTER TABLE users ADD COLUMN privacy_settings JSONB DEFAULT '{"profile_public": false, "show_progress": true}';
    END IF;
    
    -- Add last_active column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'last_active') THEN
        ALTER TABLE users ADD COLUMN last_active TIMESTAMP WITH TIME ZONE;
    END IF;
    
    -- Add last_lesson_date column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'last_lesson_date') THEN
        ALTER TABLE users ADD COLUMN last_lesson_date DATE;
    END IF;
    
    -- Add login_count column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'login_count') THEN
        ALTER TABLE users ADD COLUMN login_count INTEGER DEFAULT 0;
    END IF;

END $$;

-- Update existing NULL values with defaults (safe operation)
UPDATE users 
SET 
    target_languages = COALESCE(target_languages, '[]'::jsonb),
    longest_streak = COALESCE(longest_streak, streak, 0),
    daily_goal = COALESCE(daily_goal, 50),
    total_lessons_completed = COALESCE(total_lessons_completed, 0),
    total_time_spent = COALESCE(total_time_spent, 0),
    achievements = COALESCE(achievements, '[]'::jsonb),
    notification_preferences = COALESCE(notification_preferences, '{"push_notifications": true, "email_notifications": true, "reminder_time": "19:00"}'::jsonb),
    learning_preferences = COALESCE(learning_preferences, '{"theme": "light", "sound_enabled": true, "interface_language": "en"}'::jsonb),
    email_verified = COALESCE(email_verified, false),
    account_status = COALESCE(account_status, 'active'),
    privacy_settings = COALESCE(privacy_settings, '{"profile_public": false, "show_progress": true}'::jsonb),
    login_count = COALESCE(login_count, 0)
WHERE 
    target_languages IS NULL OR 
    longest_streak IS NULL OR 
    daily_goal IS NULL OR 
    total_lessons_completed IS NULL OR 
    total_time_spent IS NULL OR 
    achievements IS NULL OR 
    notification_preferences IS NULL OR 
    learning_preferences IS NULL OR 
    email_verified IS NULL OR 
    account_status IS NULL OR 
    privacy_settings IS NULL OR 
    login_count IS NULL;

-- =====================================================
-- TROUBLESHOOTING NOTES
-- =====================================================
/*
If you get "column does not exist" errors, run the migration script above first.

Common errors and solutions:
1. "column last_active does not exist" - Run the ALTER TABLE commands above
2. "column longest_streak does not exist" - Run the ALTER TABLE commands above
3. "relation user_sessions does not exist" - The new tables will be created automatically

To check what columns exist in your users table:
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'users' AND table_schema = 'public'
ORDER BY ordinal_position;

To check what tables exist:
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
*/ 