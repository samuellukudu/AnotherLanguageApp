-- =====================================================
-- QUICK FIX FOR MISSING COLUMNS ERROR
-- =====================================================
-- Run this script to fix "column does not exist" errors

-- Check if columns exist before adding them
DO $$
BEGIN
    -- Add last_active column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'last_active') THEN
        ALTER TABLE users ADD COLUMN last_active TIMESTAMP WITH TIME ZONE;
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
    
    -- Add login_count column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'login_count') THEN
        ALTER TABLE users ADD COLUMN login_count INTEGER DEFAULT 0;
    END IF;
    
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

END $$;

-- Update existing NULL values
UPDATE users 
SET 
    longest_streak = COALESCE(longest_streak, streak, 0),
    daily_goal = COALESCE(daily_goal, 50),
    total_lessons_completed = COALESCE(total_lessons_completed, 0),
    total_time_spent = COALESCE(total_time_spent, 0),
    achievements = COALESCE(achievements, '[]'::jsonb),
    login_count = COALESCE(login_count, 0),
    target_languages = COALESCE(target_languages, '[]'::jsonb),
    notification_preferences = COALESCE(notification_preferences, '{"push_notifications": true, "email_notifications": true, "reminder_time": "19:00"}'::jsonb),
    learning_preferences = COALESCE(learning_preferences, '{"theme": "light", "sound_enabled": true, "interface_language": "en"}'::jsonb)
WHERE 
    longest_streak IS NULL OR 
    daily_goal IS NULL OR 
    total_lessons_completed IS NULL OR 
    total_time_spent IS NULL OR 
    achievements IS NULL OR 
    login_count IS NULL OR 
    target_languages IS NULL OR 
    notification_preferences IS NULL OR 
    learning_preferences IS NULL;

-- Verify the columns exist
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default 
FROM information_schema.columns 
WHERE table_name = 'users' AND table_schema = 'public'
ORDER BY ordinal_position; 