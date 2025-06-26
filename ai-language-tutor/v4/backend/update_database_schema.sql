-- Migration script to update the users table schema
-- Run this in your Supabase SQL Editor

-- First, let's see what columns we have
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users';

-- Add missing columns to the users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS username VARCHAR(100),
ADD COLUMN IF NOT EXISTS xp INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS streak INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}';

-- Remove password_hash column if it exists (we use Supabase Auth, not local passwords)
ALTER TABLE users DROP COLUMN IF EXISTS password_hash;

-- Update existing users to have default values
UPDATE users 
SET 
    username = COALESCE(username, split_part(email, '@', 1)),
    xp = COALESCE(xp, 0),
    streak = COALESCE(streak, 0),
    preferences = COALESCE(preferences, '{}'::jsonb)
WHERE username IS NULL OR xp IS NULL OR streak IS NULL OR preferences IS NULL;

-- Ensure the updated_at trigger still works
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE OR REPLACE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

-- Make sure RLS is enabled and policies are correct
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Drop existing policies to recreate them
DROP POLICY IF EXISTS "Users can view own profile" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;
DROP POLICY IF EXISTS "Users can insert own profile" ON users;

-- Recreate policies
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Grant permissions
GRANT ALL ON users TO authenticated;
GRANT ALL ON users TO service_role; 