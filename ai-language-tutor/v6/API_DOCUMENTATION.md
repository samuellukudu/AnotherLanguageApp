# AI Language Tutor API v2.0 Documentation

## Overview

The AI Language Tutor API v2.0 is a complete rewrite that integrates SQLite database for persistent storage of all generated content. The system now automatically generates and stores all learning materials (curriculum, flashcards, exercises, and simulations) after metadata extraction.

## Key Changes from v1 (v3 folder)

1. **Automatic Content Generation**: When you extract metadata, the system automatically generates the curriculum and all learning content for all 25 lessons.
2. **Database Storage**: All content is stored in SQLite database as JSON, enabling fast retrieval.
3. **Unique IDs**: Every extraction, curriculum, and content piece has a unique UUID.
4. **GET Endpoints**: New endpoints to retrieve stored content without regeneration.

## Database Schema

### Tables

1. **metadata_extractions**: Stores user queries and extracted language learning metadata
2. **curricula**: Stores generated 25-lesson curricula
3. **learning_content**: Stores flashcards, exercises, and simulations for each lesson

## API Endpoints

### 1. Extract Metadata (POST)
**Endpoint**: `/extract/metadata`

Extracts language learning metadata from user query and automatically generates curriculum and all content.

**Request Body**:
```json
{
  "query": "I want to learn Spanish for my trip to Mexico",
  "user_id": 123  // Optional
}
```

**Response**:
```json
{
  "data": {
    "native_language": "english",
    "target_language": "spanish",
    "proficiency": "beginner",
    "title": "Spanish for Mexico Travel",
    "description": "Master essential Spanish for an amazing Mexican adventure!"
  },
  "extraction_id": "a4650023-3b4d-47f3-87aa-67ce68ce734c",
  "curriculum_id": "b5760134-4c5e-58g4-98bb-78df79df845d",
  "content_generation_started": true,
  "type": "language_metadata",
  "status": "success"
}
```

### 2. Get Metadata Extraction (GET)
**Endpoint**: `/metadata/{extraction_id}`

Retrieve a specific metadata extraction by ID.

**Response**:
```json
{
  "id": "a4650023-3b4d-47f3-87aa-67ce68ce734c",
  "user_id": 123,
  "query": "I want to learn Spanish for my trip to Mexico",
  "native_language": "english",
  "target_language": "spanish",
  "proficiency": "beginner",
  "title": "Spanish for Mexico Travel",
  "description": "Master essential Spanish for an amazing Mexican adventure!",
  "metadata": { ... },
  "created_at": "2024-01-20T10:30:00"
}
```

### 3. Get Curriculum (GET)
**Endpoint**: `/curriculum/{curriculum_id}`

Retrieve a curriculum with its 25 lessons.

**Response**:
```json
{
  "id": "b5760134-4c5e-58g4-98bb-78df79df845d",
  "metadata_extraction_id": "a4650023-3b4d-47f3-87aa-67ce68ce734c",
  "user_id": 123,
  "lesson_topic": "Spanish for Travel in Mexico",
  "curriculum": {
    "lesson_topic": "Spanish for Travel in Mexico",
    "sub_topics": [
      {
        "sub_topic": "Greetings and Basic Courtesy",
        "keywords": ["greetings", "politeness", "introductions"],
        "description": "Learn essential greetings and polite expressions for daily interactions"
      },
      // ... 24 more lessons
    ]
  },
  "is_content_generated": 1,
  "content_status": {
    "curriculum_id": "b5760134-4c5e-58g4-98bb-78df79df845d",
    "lessons_with_content": 25,
    "lessons_with_flashcards": 25,
    "lessons_with_exercises": 25,
    "lessons_with_simulations": 25
  },
  "created_at": "2024-01-20T10:30:00"
}
```

### 4. Get Curriculum Content (GET)
**Endpoint**: `/curriculum/{curriculum_id}/content`

Retrieve all learning content for a curriculum, with optional filters.

**Query Parameters**:
- `content_type` (optional): Filter by type (flashcards, exercises, simulation)
- `lesson_index` (optional): Filter by lesson index (0-24)

**Example**: `/curriculum/b5760134-4c5e-58g4-98bb-78df79df845d/content?content_type=flashcards&lesson_index=0`

**Response**:
```json
{
  "curriculum_id": "b5760134-4c5e-58g4-98bb-78df79df845d",
  "content": [
    {
      "id": "c6870245-5d6f-69h5-a9cc-89eg8aeg956e",
      "curriculum_id": "b5760134-4c5e-58g4-98bb-78df79df845d",
      "content_type": "flashcards",
      "lesson_index": 0,
      "lesson_topic": "Greetings and Basic Courtesy",
      "content": [
        {
          "word": "Buenos días",
          "definition": "Good morning (formal greeting)",
          "example": "Buenos días, ¿cómo está usted?"
        },
        // ... 9 more flashcards
      ],
      "created_at": "2024-01-20T10:31:00"
    }
  ],
  "total": 1,
  "filters": {
    "content_type": "flashcards",
    "lesson_index": 0
  }
}
```

### 5. Get Lesson Content (GET)
**Endpoint**: `/curriculum/{curriculum_id}/lesson/{lesson_index}`

Get all content types for a specific lesson.

**Example**: `/curriculum/b5760134-4c5e-58g4-98bb-78df79df845d/lesson/0`

**Response**:
```json
{
  "curriculum_id": "b5760134-4c5e-58g4-98bb-78df79df845d",
  "lesson_index": 0,
  "flashcards": {
    "id": "c6870245-5d6f-69h5-a9cc-89eg8aeg956e",
    "lesson_topic": "Greetings and Basic Courtesy",
    "content": [ ... ],
    "created_at": "2024-01-20T10:31:00"
  },
  "exercises": {
    "id": "d7980356-6e7g-7ai6-badd-9afh9bfha67f",
    "lesson_topic": "Greetings and Basic Courtesy",
    "content": [ ... ],
    "created_at": "2024-01-20T10:31:30"
  },
  "simulation": {
    "id": "e8a90467-7f8h-8bj7-cbee-abgi0cgib78g",
    "lesson_topic": "Greetings and Basic Courtesy",
    "content": { ... },
    "created_at": "2024-01-20T10:32:00"
  }
}
```

### 6. Get User Metadata History (GET)
**Endpoint**: `/user/{user_id}/metadata`

Get a user's metadata extraction history.

**Query Parameters**:
- `limit` (optional, default=20): Maximum results to return

**Response**:
```json
{
  "user_id": 123,
  "extractions": [
    {
      "id": "a4650023-3b4d-47f3-87aa-67ce68ce734c",
      "query": "I want to learn Spanish for my trip to Mexico",
      "native_language": "english",
      "target_language": "spanish",
      "proficiency": "beginner",
      "title": "Spanish for Mexico Travel",
      "description": "Master essential Spanish for an amazing Mexican adventure!",
      "metadata": { ... },
      "created_at": "2024-01-20T10:30:00"
    }
  ],
  "total": 1
}
```

### 7. Get User Curricula (GET)
**Endpoint**: `/user/{user_id}/curricula`

Get all curricula for a user.

**Response**:
```json
{
  "user_id": 123,
  "curricula": [
    {
      "id": "b5760134-4c5e-58g4-98bb-78df79df845d",
      "metadata_extraction_id": "a4650023-3b4d-47f3-87aa-67ce68ce734c",
      "lesson_topic": "Spanish for Travel in Mexico",
      "curriculum": { ... },
      "is_content_generated": 1,
      "content_status": { ... },
      "created_at": "2024-01-20T10:30:00"
    }
  ],
  "total": 1
}
```

### 8. Get User Learning Journeys (GET)
**Endpoint**: `/user/{user_id}/journeys`

Get user's complete learning journeys (combines metadata and curriculum info).

### 9. Search Curricula (GET)
**Endpoint**: `/search/curricula`

Search for existing curricula by language combination.

**Query Parameters**:
- `native_language` (required): Native language
- `target_language` (required): Target language
- `proficiency` (optional): Proficiency level
- `limit` (optional, default=10): Maximum results

**Example**: `/search/curricula?native_language=english&target_language=spanish&proficiency=beginner`

### 10. Get Content Generation Status (GET)
**Endpoint**: `/content/status/{curriculum_id}`

Check if all content has been generated for a curriculum.

**Response**:
```json
{
  "curriculum_id": "b5760134-4c5e-58g4-98bb-78df79df845d",
  "status": {
    "curriculum_id": "b5760134-4c5e-58g4-98bb-78df79df845d",
    "user_id": 123,
    "lesson_topic": "Spanish for Travel in Mexico",
    "lessons_with_content": 25,
    "lessons_with_flashcards": 25,
    "lessons_with_exercises": 25,
    "lessons_with_simulations": 25,
    "created_at": "2024-01-20T10:30:00"
  },
  "completion_percentage": 100.0,
  "is_complete": true
}
```

## Workflow Example

1. **Extract Metadata and Start Generation**:
   ```bash
   POST /extract/metadata
   {
     "query": "I want to learn French for business meetings",
     "user_id": 456
   }
   ```

2. **Check Generation Status**:
   ```bash
   GET /content/status/{curriculum_id}
   ```

3. **Retrieve Content When Ready**:
   ```bash
   # Get full curriculum
   GET /curriculum/{curriculum_id}
   
   # Get all flashcards
   GET /curriculum/{curriculum_id}/content?content_type=flashcards
   
   # Get content for lesson 5
   GET /curriculum/{curriculum_id}/lesson/5
   ```

## Content Types

### Flashcards
Array of 10 vocabulary items per lesson:
```json
[
  {
    "word": "target language word/phrase",
    "definition": "explanation in native language",
    "example": "example sentence in target language"
  }
]
```

### Exercises
Array of 5 cloze-style exercises per lesson:
```json
[
  {
    "sentence": "Sentence with ___",
    "answer": "correct answer",
    "choices": ["option1", "option2", "option3", "option4"],
    "explanation": "why this answer is correct"
  }
]
```

### Simulation
Interactive story/dialogue per lesson:
```json
{
  "title": "Story title",
  "setting": "Background description",
  "content": [
    {
      "speaker": "Character name",
      "target_language_text": "Text in target language",
      "phonetics": "Phonetic transcription",
      "base_language_translation": "Translation"
    }
  ]
}
```

## Notes

- Content generation happens asynchronously in the background
- Each curriculum contains exactly 25 lessons
- Each lesson has flashcards, exercises, and simulation content
- All content is stored as JSON in the database
- The system uses UUIDs for all IDs 