-- =====================================================
-- DROP ALL TABLES AND RELATED OBJECTS
-- =====================================================
-- ⚠️  WARNING: This will permanently delete ALL data!
-- ⚠️  Make sure to backup your data before running this!
-- ⚠️  This action cannot be undone!

-- =====================================================
-- DISABLE ROW LEVEL SECURITY FIRST
-- =====================================================
ALTER TABLE IF EXISTS users DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS curriculums DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS lessons DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS flashcards DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS exercises DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS simulations DISABLE ROW LEVEL SECURITY;

-- =====================================================
-- DROP ALL RLS POLICIES
-- =====================================================

-- Users table policies
DROP POLICY IF EXISTS "Users can view own profile" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;
DROP POLICY IF EXISTS "Users can insert own profile" ON users;
DROP POLICY IF EXISTS "Allow all operations" ON users;

-- Curriculums table policies
DROP POLICY IF EXISTS "Users can view own curriculums" ON curriculums;
DROP POLICY IF EXISTS "Users can create own curriculums" ON curriculums;
DROP POLICY IF EXISTS "Users can update own curriculums" ON curriculums;
DROP POLICY IF EXISTS "Users can delete own curriculums" ON curriculums;
DROP POLICY IF EXISTS "Allow all operations" ON curriculums;

-- Lessons table policies
DROP POLICY IF EXISTS "Users can view curriculum lessons" ON lessons;
DROP POLICY IF EXISTS "Users can manage curriculum lessons" ON lessons;
DROP POLICY IF EXISTS "Allow all operations" ON lessons;

-- Flashcards table policies
DROP POLICY IF EXISTS "Users can view curriculum flashcards" ON flashcards;
DROP POLICY IF EXISTS "Users can manage curriculum flashcards" ON flashcards;
DROP POLICY IF EXISTS "Allow all operations" ON flashcards;

-- Exercises table policies
DROP POLICY IF EXISTS "Users can view curriculum exercises" ON exercises;
DROP POLICY IF EXISTS "Users can manage curriculum exercises" ON exercises;
DROP POLICY IF EXISTS "Allow all operations" ON exercises;

-- Simulations table policies
DROP POLICY IF EXISTS "Users can view curriculum simulations" ON simulations;
DROP POLICY IF EXISTS "Users can manage curriculum simulations" ON simulations;
DROP POLICY IF EXISTS "Allow all operations" ON simulations;

-- =====================================================
-- DROP ALL TRIGGERS
-- =====================================================
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP TRIGGER IF EXISTS update_curriculums_updated_at ON curriculums;
DROP TRIGGER IF EXISTS update_lessons_updated_at ON lessons;
DROP TRIGGER IF EXISTS update_flashcards_updated_at ON flashcards;
DROP TRIGGER IF EXISTS update_exercises_updated_at ON exercises;
DROP TRIGGER IF EXISTS update_simulations_updated_at ON simulations;

-- =====================================================
-- DROP ALL INDEXES (Optional - they'll be dropped with tables)
-- =====================================================
DROP INDEX IF EXISTS idx_users_email;
DROP INDEX IF EXISTS idx_users_username;
DROP INDEX IF EXISTS idx_curriculums_user_id;
DROP INDEX IF EXISTS idx_curriculums_created_at;
DROP INDEX IF EXISTS idx_lessons_curriculum_id;
DROP INDEX IF EXISTS idx_lessons_order;
DROP INDEX IF EXISTS idx_flashcards_curriculum_id;
DROP INDEX IF EXISTS idx_exercises_curriculum_id;
DROP INDEX IF EXISTS idx_simulations_curriculum_id;

-- =====================================================
-- DROP ALL TABLES (in dependency order)
-- =====================================================
-- Drop content tables first (they depend on curriculums)
DROP TABLE IF EXISTS simulations CASCADE;
DROP TABLE IF EXISTS exercises CASCADE;
DROP TABLE IF EXISTS flashcards CASCADE;
DROP TABLE IF EXISTS lessons CASCADE;

-- Drop curriculums table (depends on users)
DROP TABLE IF EXISTS curriculums CASCADE;

-- Drop users table last
DROP TABLE IF EXISTS users CASCADE;

-- =====================================================
-- DROP SEQUENCES (if they exist independently)
-- =====================================================
DROP SEQUENCE IF EXISTS curriculums_id_seq CASCADE;
DROP SEQUENCE IF EXISTS lessons_id_seq CASCADE;
DROP SEQUENCE IF EXISTS flashcards_id_seq CASCADE;
DROP SEQUENCE IF EXISTS exercises_id_seq CASCADE;
DROP SEQUENCE IF EXISTS simulations_id_seq CASCADE;

-- =====================================================
-- DROP CUSTOM FUNCTIONS
-- =====================================================
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- =====================================================
-- REVOKE PERMISSIONS (Optional cleanup)
-- =====================================================
-- Note: These will fail if tables don't exist, but that's OK

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Uncomment these to verify everything was dropped

-- Check remaining tables
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- AND table_name IN ('users', 'curriculums', 'lessons', 'flashcards', 'exercises', 'simulations');

-- Check remaining functions
-- SELECT routine_name FROM information_schema.routines 
-- WHERE routine_schema = 'public' 
-- AND routine_name = 'update_updated_at_column';

-- Check remaining policies
-- SELECT schemaname, tablename, policyname FROM pg_policies 
-- WHERE schemaname = 'public' 
-- AND tablename IN ('users', 'curriculums', 'lessons', 'flashcards', 'exercises', 'simulations');

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================
-- If no errors occurred, all tables and related objects have been dropped
-- You can now run the complete_database_schema.sql to recreate everything

SELECT 'All tables and related objects have been successfully dropped!' as status; 