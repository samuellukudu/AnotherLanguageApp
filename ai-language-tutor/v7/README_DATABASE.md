# Language Learning Content Database

This system saves all generated content from the DSPy language learning application into a SQLite database as JSON, making it easy to store, retrieve, and manage language learning sessions.

## Files Overview

- **`dspy_app.py`** - Original DSPy application that generates language learning content
- **`save_to_database.py`** - Main script that captures content and saves it to SQLite as JSON
- **`query_database.py`** - Script to query and display all saved content
- **`database_utils.py`** - Command-line utility for managing database content
- **`language_learning_content.db`** - SQLite database file containing all saved sessions

## Database Schema

The database contains the following tables:

### Main Table: `learning_sessions`
- `id` (TEXT) - Unique session identifier
- `query` (TEXT) - Original user query/context
- `created_at` (TIMESTAMP) - Session creation time
- `metadata_json` (TEXT) - Language metadata as JSON
- `curriculum_json` (TEXT) - Generated curriculum as JSON
- `exercises_json` (TEXT) - Generated exercises as JSON
- `flashcards_json` (TEXT) - Generated flashcards as JSON
- `story_json` (TEXT) - Generated story as JSON

### Individual Content Tables
- `metadata` - Language learning metadata
- `curricula` - Learning curricula
- `exercises` - Practice exercises
- `flashcards` - Vocabulary flashcards
- `stories` - Learning stories/dialogues

## Usage

### 1. Initialize Database
```bash
python database_utils.py init
```

### 2. Generate and Save Content
```bash
# Run the main script to generate content for a specific query
python save_to_database.py

# Or add a new session with custom query
python database_utils.py add "learning Spanish for travel to Mexico"
```

### 3. List All Sessions
```bash
python database_utils.py list
```

### 4. View Session Content
```bash
# View all content for a session
python database_utils.py get <session_id>

# View specific content type
python database_utils.py get <session_id> --type metadata
python database_utils.py get <session_id> --type curriculum
python database_utils.py get <session_id> --type exercises
python database_utils.py get <session_id> --type flashcards
python database_utils.py get <session_id> --type story
```

### 5. Export Session to JSON File
```bash
# Export with auto-generated filename
python database_utils.py export <session_id>

# Export with custom filename
python database_utils.py export <session_id> --filename my_session.json
```

### 6. Search Sessions
```bash
python database_utils.py search "engineer"
python database_utils.py search "Berlin"
```

### 7. Query Database Directly
```bash
# View all saved content in readable format
python query_database.py
```

## JSON Structure

Each session contains the following JSON structures:

### Metadata
```json
{
  "native_language": "English",
  "target_language": "German",
  "proficiency": "intermediate",
  "title": "Job Search in Berlin",
  "description": "Professional German for structural engineering career"
}
```

### Curriculum
```json
{
  "lesson_topic": "Professional German for Engineering Jobs",
  "sub_topics": [
    {
      "sub_topic": "Technical Vocabulary",
      "keywords": ["Engineering", "Technical Terms"],
      "description": "Learn essential engineering terminology"
    }
  ]
}
```

### Exercises
```json
[
  {
    "sentence": "Der Ingenieur ___ das Projekt.",
    "answer": "leitet",
    "choices": ["leitet", "macht", "baut", "plant"],
    "explanation": "The correct answer is 'leitet' which means 'leads' in English."
  }
]
```

### Flashcards
```json
[
  {
    "word": "Bauingenieur",
    "definition": "Civil engineer",
    "example": "Als Bauingenieur plane ich Brücken und Gebäude."
  }
]
```

### Story
```json
{
  "title": "Meeting in Berlin",
  "setting": "A professional networking event in Berlin",
  "content": [
    {
      "speaker": "Engineer 1",
      "target_language_text": "Guten Tag, ich bin Bauingenieur.",
      "base_language_translation": "Good day, I am a civil engineer."
    }
  ]
}
```

## Benefits

1. **Persistent Storage** - All generated content is saved permanently
2. **JSON Format** - Easy to parse and integrate with other applications
3. **Structured Data** - Well-organized database schema for efficient querying
4. **Export Capability** - Easy export to JSON files for backup or sharing
5. **Search Functionality** - Find sessions by keywords
6. **Version Control** - Track when content was generated
7. **Scalable** - Can handle multiple users and sessions

## Example Workflow

```bash
# 1. Initialize database
python database_utils.py init

# 2. Generate content for a new query
python database_utils.py add "learning French for business meetings"

# 3. List all sessions
python database_utils.py list

# 4. Export the session
python database_utils.py export <session_id> --filename french_business.json

# 5. Search for specific content
python database_utils.py search "business"
```

This system provides a complete solution for managing language learning content with full JSON storage and retrieval capabilities.