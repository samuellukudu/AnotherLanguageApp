Okay, let's design a practical database schema for your AI Learning Assistant, focusing on storing the necessary information for personalization, tracking progress, and enabling future features like review, while keeping it manageable initially. We'll use PostgreSQL syntax as an example.

**Core Goals for DB Design:**

1.  **User Management:** Store user credentials and preferences.
2.  **Personalization:** Capture defaults (languages, level) to inform prompts.
3.  **Usage Tracking:** Log user interactions (what they generated, when).
4.  **Content Persistence:** Allow users to save specific generated content.
5.  **Feedback Collection:** Store user feedback on content quality/relevance.
6.  **Foundation for Future Features:** Allow for potential expansion (like SRS-Spaced Repetition System).

**Proposed Schema (SQL `CREATE TABLE` statements):**

```sql
-- Optional ENUM types for consistency (if your Postgres version supports them easily)
-- CREATE TYPE user_level AS ENUM ('Beginner', 'Intermediate', 'Advanced', 'Fluent');
-- CREATE TYPE content_type AS ENUM ('flashcards', 'exercises', 'simulation');

-- 1. Users Table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,                           -- Unique identifier for the user
    username VARCHAR(50) UNIQUE NOT NULL,                 -- User's chosen username
    email VARCHAR(255) UNIQUE,                            -- User's email (optional, for recovery/notifications)
    password_hash VARCHAR(255) NOT NULL,                  -- Securely hashed password
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- When the user account was created
    last_login TIMESTAMP WITH TIME ZONE,                   -- Optional: track last login time
    default_target_language VARCHAR(50),                  -- User's preferred target language (e.g., 'Spanish', 'fr')
    default_base_language VARCHAR(50),                    -- User's preferred base language (e.g., 'English', 'en')
    -- self_assessed_level user_level                      -- User's self-reported level (using ENUM type)
    self_assessed_level VARCHAR(20)                       -- User's self-reported level (using VARCHAR if ENUM not used)
);

-- Index for faster login lookups
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);


-- 2. Activity Log Table
CREATE TABLE activity_log (
    log_id SERIAL PRIMARY KEY,                           -- Unique identifier for the log entry
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, -- Link to the user who performed the action
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- When the activity occurred
    -- content_type content_type NOT NULL,                  -- Type of content generated (using ENUM)
    content_type VARCHAR(20) NOT NULL CHECK (content_type IN ('flashcards', 'exercises', 'simulation')), -- Type of content generated (using CHECK constraint)
    query_text TEXT NOT NULL,                             -- The exact query string the user submitted
    target_language VARCHAR(50) NOT NULL,                 -- Target language used for *this specific request*
    base_language VARCHAR(50),                            -- Base language used for *this specific request* (nullable if not always applicable)
    request_metadata JSONB,                               -- Optional: Store extra request info (e.g., device type, session ID)
    response_metadata JSONB                               -- Optional: Store info about the response (e.g., generation time, model used)
    -- Add performance metrics if needed later, e.g., for exercises:
    -- score FLOAT CHECK (score >= 0.0 AND score <= 1.0)
);

-- Index for quickly finding a user's activities, ordered by time
CREATE INDEX idx_activity_log_user_timestamp ON activity_log(user_id, timestamp DESC);


-- 3. Saved Content Table
CREATE TABLE saved_content (
    saved_content_id SERIAL PRIMARY KEY,                 -- Unique identifier for the saved item
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, -- Link to the user who saved it
    -- content_type content_type NOT NULL,                  -- Type of content saved (using ENUM)
    content_type VARCHAR(20) NOT NULL CHECK (content_type IN ('flashcards', 'exercises', 'simulation')), -- Type of content saved (using CHECK)
    original_query TEXT NOT NULL,                         -- The query that generated this content
    content_data JSONB NOT NULL,                          -- The actual generated JSON data (flashcards array, exercise array, story object)
    saved_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- When the content was saved
    user_label VARCHAR(100),                              -- Optional: A short label/name given by the user
    user_notes TEXT                                       -- Optional: Longer notes from the user about this content
);

-- Index for quickly finding a user's saved content
CREATE INDEX idx_saved_content_user ON saved_content(user_id);


-- 4. Feedback Table
CREATE TABLE feedback (
    feedback_id SERIAL PRIMARY KEY,                      -- Unique identifier for the feedback entry
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, -- Link to the user giving feedback
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- When feedback was submitted
    related_log_id INTEGER REFERENCES activity_log(log_id) ON DELETE SET NULL, -- Optional: Link to the specific activity log entry
    related_saved_content_id INTEGER REFERENCES saved_content(saved_content_id) ON DELETE SET NULL, -- Optional: Link to specific saved content
    rating SMALLINT CHECK (rating >= 1 AND rating <= 5),   -- Optional: Simple 1-5 rating
    feedback_text TEXT,                                   -- User's qualitative feedback
    context_details JSONB                                 -- Optional: Store snapshot of relevant context (e.g., query, content snippet) if not linking directly
);

-- Index for finding feedback by user or related content
CREATE INDEX idx_feedback_user ON feedback(user_id);
CREATE INDEX idx_feedback_related_log ON feedback(related_log_id);
CREATE INDEX idx_feedback_related_saved ON feedback(related_saved_content_id);

```

**Explanation and Content to Store:**

1.  **`users` Table:**
    *   Stores login info (`username`, `password_hash`, maybe `email`).
    *   Crucially stores `default_target_language`, `default_base_language`, and `self_assessed_level`. Your backend can fetch these to pre-populate or inform prompts if the user doesn't specify them in a particular query.

2.  **`activity_log` Table:**
    *   **The Core of Usage Tracking.** Every time a user successfully generates content (`/generate/*`), log an entry here.
    *   `user_id`: Who did it?
    *   `timestamp`: When?
    *   `content_type`: What kind of generation? (flashcards, exercises, simulation)
    *   `query_text`: **Essential.** Store the *exact* query the user sent. This tells you the topic, hobby/work context, and any specific languages/levels requested for that instance. This is vital context for understanding user behaviour and potentially for feedback.
    *   `target_language`, `base_language`: Store the actual languages used for *this specific generation*, which might differ from the user's defaults if they specified them in the query.

3.  **`saved_content` Table:**
    *   When a user explicitly chooses to "save" a generated set (via a `/content/save` endpoint).
    *   `user_id`, `content_type`, `original_query`: Track who saved what, generated from which query.
    *   `content_data` (`JSONB`): Store the **entire JSON response** received from the LLM for that generation. `JSONB` is efficient in Postgres for storage and potential querying. This allows the user to retrieve exactly what they saved.
    *   `user_label`, `user_notes`: Allow users to organize/annotate saved content.

4.  **`feedback` Table:**
    *   Capture user opinions on the generated content.
    *   `user_id`, `timestamp`.
    *   `related_log_id` / `related_saved_content_id`: **Important.** Try to link feedback directly to the activity or saved item it refers to. This gives much better context than just storing the feedback text alone.
    *   `rating`, `feedback_text`: The feedback itself.

**How this Enables Proper Usage and Learning:**

*   **Personalization:** User defaults help tailor general interactions. The `query_text` in `activity_log` captures the *specific* context for each generation, driving the LLM personalization.
*   **Progress Insight (Basic):** Querying `activity_log` for a `user_id` shows their activity frequency, topics explored (`query_text`), and content types used. You can build summary dashboards from this.
*   **Review/Revisit:** The `saved_content` table allows users to manually curate and revisit useful learning materials.
*   **Improvement Cycle:** The `feedback` table (especially when linked to specific activities/content) provides invaluable data to refine your prompts (`config.*_instructions`) or even fine-tune models in the future.
*   **Foundation:** This structure doesn't include a full Spaced Repetition System (SRS) yet, but logging individual activities and allowing content saving are steps towards potentially identifying items for SRS later (e.g., analyzing difficult exercises logged or flashcards frequently saved).

**Key Considerations:**

*   **Data Volume:** The `activity_log` could grow large. Ensure proper indexing (`user_id`, `timestamp`). Consider archiving or summarizing old logs eventually if needed.
*   **Storing JSON:** Using `JSONB` is generally recommended over `JSON` in Postgres due to better indexing and performance.
*   **Security:** Ensure `password_hash` is generated using a strong, salted algorithm (like bcrypt, Argon2). Handle sensitive data like `email` appropriately.
*   **Consistency:** Decide on a consistent way to store language names/codes (e.g., full names like 'Spanish', ISO 639-1 codes like 'es'). Be consistent across tables and your application logic.

This schema provides a solid foundation for your application's core needs. Start with this, and you can always evolve it as new feature requirements emerge.

# Database Integration for AI Language Tutor

This document explains the SQLite database integration that has been added to the AI Language Tutor backend.

## Overview

The system now uses **database-first storage** by default:
- **Primary**: SQLite database for efficient querying and data management
- **Optional**: File-based storage backup (can be enabled if needed)

**No migrations needed** - the system automatically uses the database for all new data.

## Setup

### 1. Install Dependencies

The required dependency `aiosqlite` has been added to `requirements.txt`. Install it with:

```bash
pip install -r requirements.txt
```

### 2. Database Initialization

The database is automatically initialized when the FastAPI application starts. The database file will be created at `data/language_tutor.db`.

### 3. Migration from File Storage (Optional)

If you have existing curriculum data in JSON files and want to migrate it to the database:

```bash
python -m backend.db_utils migrate
```

**Note**: This is only needed if you're upgrading from a previous version with file-based data. New installations automatically use the database.

## Database Schema

### Tables

#### `curricula`
Stores curriculum metadata and overall status.

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key (UUID) |
| user_id | INTEGER | User identifier |
| title | TEXT | Curriculum title |
| description | TEXT | Curriculum description |
| native_language | TEXT | User's native language |
| target_language | TEXT | Target learning language |
| proficiency | TEXT | User's proficiency level |
| lesson_topic | TEXT | Main topic of the curriculum |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| status | TEXT | Overall curriculum status |

#### `lessons`
Stores individual lessons within a curriculum.

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key (UUID) |
| curriculum_id | TEXT | Foreign key to curricula table |
| sub_topic | TEXT | Lesson sub-topic |
| description | TEXT | Lesson description |
| keywords | TEXT | JSON array of keywords |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

#### `flashcards`
Stores flashcards for each lesson.

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key (UUID) |
| lesson_id | TEXT | Foreign key to lessons table |
| word | TEXT | Flashcard word/term |
| definition | TEXT | Definition of the word |
| example | TEXT | Example sentence |
| created_at | TIMESTAMP | Creation timestamp |

#### `exercises`
Stores exercises for each lesson.

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key (UUID) |
| lesson_id | TEXT | Foreign key to lessons table |
| sentence | TEXT | Exercise sentence |
| answer | TEXT | Correct answer |
| choices | TEXT | JSON array of multiple choice options |
| explanation | TEXT | Explanation of the answer |
| created_at | TIMESTAMP | Creation timestamp |

#### `simulations`
Stores conversation simulations for each lesson.

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key (UUID) |
| lesson_id | TEXT | Foreign key to lessons table |
| title | TEXT | Simulation title |
| setting | TEXT | Simulation setting/context |
| content | TEXT | JSON array of conversation content |
| created_at | TIMESTAMP | Creation timestamp |

## How It Works

### Database-First Strategy

1. **Write Operations**: Data is written to the database (primary storage)
2. **Read Operations**: Data is retrieved from the database
3. **Error Handling**: Robust error handling ensures data integrity
4. **Optional Backup**: File storage can be enabled as backup if needed

### Storage Class Updates

The `CurriculumStorage` class has been enhanced with:
- Database integration option (`use_database` parameter)
- Automatic fallback to file storage on database errors
- Consistent API - no changes needed in existing code

### API Compatibility

All existing API endpoints work exactly the same way. The database integration is transparent to the API consumers.

## Configuration

### Storage Configuration

The system uses database-first storage by default. You can configure it in `backend/config.py`:

```python
# Database Configuration
DATABASE_ENABLED = True
DATABASE_PATH = "data/language_tutor.db"
FILE_BACKUP_ENABLED = False  # Set to True if you want file backup

# Storage Configuration
USE_DATABASE_PRIMARY = True  # Default: database-first
USE_FILE_BACKUP = False      # Default: no file backup
```

### Manual Configuration

You can also configure storage programmatically:

```python
# Database-only (default)
storage = CurriculumStorage(use_database=True, use_file_backup=False)

# Database with file backup
storage = CurriculumStorage(use_database=True, use_file_backup=True)

# File-only mode (not recommended)
storage = CurriculumStorage(use_database=False, use_file_backup=True)
```

### Database Path

The database path can be configured:

```python
from backend.database import DatabaseManager

# Custom database path
database = DatabaseManager(db_path="custom/path/language_tutor.db")
```

## Maintenance Commands

### Migration
Migrate existing file data to database:
```bash
python -m backend.db_utils migrate
```

## Benefits

1. **Performance**: Faster queries and filtering capabilities
2. **Scalability**: Better handling of large datasets
3. **Data Integrity**: ACID compliance and foreign key constraints
4. **Flexibility**: Easy to add new query patterns and reporting
5. **Backup**: Dual storage provides data redundancy

## Troubleshooting

### Database Connection Issues
- Check if `aiosqlite` is installed
- Verify write permissions in the `data/` directory
- Check disk space availability

### Migration Issues
- Ensure all JSON files are valid
- Check file permissions in the `data/curricula/` directory
- Review migration logs for specific error messages

### Fallback Behavior
If database operations fail, the system automatically falls back to file storage. Check application logs for database error messages.

## Performance Considerations

- Database queries are optimized with indexes on frequently queried columns
- Large content data is stored as JSON in the database
- File storage is maintained for backup and compatibility

## New API Methods

The restructured database provides new methods for better content management:

### Curriculum Management
- `store_curriculum(user_id, metadata, curriculum_data)` - Create curriculum with lessons
- `get_curriculum(curriculum_id)` - Get complete curriculum with all content
- `get_user_curricula(user_id)` - Get all curricula for a user
- `update_curriculum_status(curriculum_id, status)` - Update curriculum status

### Lesson Management
- `get_lessons(curriculum_id)` - Get all lessons for a curriculum

### Content Management
- `store_flashcards(lesson_id, flashcards_data)` - Store flashcards for a lesson
- `store_exercises(lesson_id, exercises_data)` - Store exercises for a lesson
- `store_simulation(lesson_id, simulation_data)` - Store simulation for a lesson

### Legacy Compatibility
- `store_generated_content(curriculum_id, content_type, content_data)` - Legacy method (deprecated)
- `update_content_status(curriculum_id, content_type, status)` - Legacy method (deprecated)

## Database Relationships

The new schema properly represents the relationships:

```
curricula (1) -> (many) lessons
lessons (1) -> (many) flashcards
lessons (1) -> (many) exercises  
lessons (1) -> (many) simulations
```

This allows for:
- Multiple lessons per curriculum
- Multiple flashcards/exercises per lesson
- Better content organization and querying
- Individual lesson-based content generation

## Future Enhancements

Potential improvements that could be added:
- User management tables
- Content versioning and history
- Analytics and usage tracking
- Full-text search capabilities
- Lesson progress tracking
- Content difficulty ratings
- Spaced repetition algorithms
- Data archiving strategies