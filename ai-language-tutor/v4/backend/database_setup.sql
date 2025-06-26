-- Users table to store user profiles and metadata
-- This table should be created in your Supabase project

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT auth.uid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100),
    xp INTEGER DEFAULT 0,
    streak INTEGER DEFAULT 0,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Curriculums table to store user's learning curriculums
CREATE TABLE IF NOT EXISTS curriculums (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    metadata JSONB DEFAULT '{}',
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create an updated_at trigger function (reusable)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE OR REPLACE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

CREATE OR REPLACE TRIGGER update_curriculums_updated_at 
    BEFORE UPDATE ON curriculums 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

-- Row Level Security (RLS) policies for users
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only read their own profile
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

-- Policy: Users can only update their own profile
CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Policy: Users can insert their own profile
CREATE POLICY "Users can insert own profile" ON users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Row Level Security (RLS) policies for curriculums
ALTER TABLE curriculums ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only view their own curriculums
CREATE POLICY "Users can view own curriculums" ON curriculums
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can only create their own curriculums
CREATE POLICY "Users can create own curriculums" ON curriculums
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can only update their own curriculums
CREATE POLICY "Users can update own curriculums" ON curriculums
    FOR UPDATE USING (auth.uid() = user_id);

-- Policy: Users can only delete their own curriculums
CREATE POLICY "Users can delete own curriculums" ON curriculums
    FOR DELETE USING (auth.uid() = user_id);

-- Grant necessary permissions
GRANT ALL ON users TO authenticated;
GRANT ALL ON users TO service_role;
GRANT ALL ON curriculums TO authenticated;
GRANT ALL ON curriculums TO service_role;
GRANT USAGE, SELECT ON SEQUENCE curriculums_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE curriculums_id_seq TO service_role; 