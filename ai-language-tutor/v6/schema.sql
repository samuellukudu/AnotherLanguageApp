-- AI Language Tutor Database Schema

-- Table for storing extracted metadata from user queries
CREATE TABLE IF NOT EXISTS metadata_extractions (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id INTEGER,
    query TEXT NOT NULL,
    native_language TEXT,
    target_language TEXT,
    proficiency TEXT CHECK(proficiency IN ('beginner', 'intermediate', 'advanced')),
    title TEXT,
    description TEXT,
    metadata_json TEXT NOT NULL, -- Full JSON response
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for user queries
CREATE INDEX IF NOT EXISTS idx_metadata_user_id ON metadata_extractions(user_id);
CREATE INDEX IF NOT EXISTS idx_metadata_languages ON metadata_extractions(native_language, target_language);

-- Table for storing generated curricula
CREATE TABLE IF NOT EXISTS curricula (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    metadata_extraction_id TEXT NOT NULL,
    user_id INTEGER,
    lesson_topic TEXT,
    curriculum_json TEXT NOT NULL, -- Full curriculum JSON with 25 lessons
    is_content_generated INTEGER DEFAULT 0, -- Boolean: has all content been generated?
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (metadata_extraction_id) REFERENCES metadata_extractions(id) ON DELETE CASCADE
);

-- Index for curriculum lookups
CREATE INDEX IF NOT EXISTS idx_curricula_metadata_id ON curricula(metadata_extraction_id);
CREATE INDEX IF NOT EXISTS idx_curricula_user_id ON curricula(user_id);

-- Table for storing all types of learning content
CREATE TABLE IF NOT EXISTS learning_content (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    curriculum_id TEXT NOT NULL,
    content_type TEXT NOT NULL CHECK(content_type IN ('flashcards', 'exercises', 'simulation')),
    lesson_index INTEGER NOT NULL CHECK(lesson_index >= 0 AND lesson_index < 25),
    lesson_topic TEXT,
    content_json TEXT NOT NULL, -- The actual generated content
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (curriculum_id) REFERENCES curricula(id) ON DELETE CASCADE
);

-- Index for content lookups
CREATE INDEX IF NOT EXISTS idx_content_curriculum_id ON learning_content(curriculum_id);
CREATE INDEX IF NOT EXISTS idx_content_type ON learning_content(content_type);
CREATE INDEX IF NOT EXISTS idx_content_lesson ON learning_content(curriculum_id, lesson_index);

-- View for easy access to user's learning journeys
CREATE VIEW IF NOT EXISTS user_learning_journeys AS
SELECT 
    m.id as metadata_id,
    m.user_id,
    m.query,
    m.native_language,
    m.target_language,
    m.proficiency,
    m.title,
    m.description,
    c.id as curriculum_id,
    c.lesson_topic,
    c.is_content_generated,
    m.created_at
FROM metadata_extractions m
LEFT JOIN curricula c ON m.id = c.metadata_extraction_id
ORDER BY m.created_at DESC;

-- View for content availability per curriculum
CREATE VIEW IF NOT EXISTS curriculum_content_status AS
SELECT 
    c.id as curriculum_id,
    c.user_id,
    c.lesson_topic,
    COUNT(DISTINCT lc.lesson_index) as lessons_with_content,
    COUNT(DISTINCT CASE WHEN lc.content_type = 'flashcards' THEN lc.lesson_index END) as lessons_with_flashcards,
    COUNT(DISTINCT CASE WHEN lc.content_type = 'exercises' THEN lc.lesson_index END) as lessons_with_exercises,
    COUNT(DISTINCT CASE WHEN lc.content_type = 'simulation' THEN lc.lesson_index END) as lessons_with_simulations,
    c.created_at
FROM curricula c
LEFT JOIN learning_content lc ON c.id = lc.curriculum_id
GROUP BY c.id; 