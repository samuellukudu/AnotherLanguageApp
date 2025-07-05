# AI Language Tutor v6 - Database-Integrated Backend

## Overview

This is an upgraded version of the AI Language Tutor backend (originally from v3) that integrates a pure SQLite database for persistent storage and automatic content generation.

## Key Improvements

1. **Database Integration**: Uses pure SQLite (no ORM) for fast, reliable storage
2. **Automatic Content Generation**: When metadata is extracted, the system automatically:
   - Generates a 25-lesson curriculum
   - Creates flashcards, exercises, and simulations for all lessons
   - Stores everything in the database
3. **Fast Retrieval**: Pre-generated content is served instantly via GET endpoints
4. **Unique IDs**: Every extraction, curriculum, and content piece has a UUID for easy tracking
5. **User History**: Full tracking of user queries and generated content

## Architecture

```
POST /extract/metadata
    ↓
Extracts metadata → Saves to DB
    ↓
Generates curriculum → Saves to DB
    ↓
Background task: Generates all content → Saves to DB
    ↓
GET endpoints serve pre-generated content
```

## Files Structure

```
v6/
├── schema.sql              # SQLite database schema
├── backend/
│   ├── main.py            # FastAPI application with all endpoints
│   ├── db.py              # Pure SQLite database operations
│   ├── content_generator.py # Handles automatic content generation
│   ├── config.py          # Instruction templates (from v3)
│   └── utils/             # AI generation utilities (from v3)
├── API_DOCUMENTATION.md   # Complete API reference
├── QUICK_START_v2.md      # Setup and usage guide
├── test_api.py            # Test script demonstrating workflow
└── requirements.txt       # Python dependencies
```

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Set OpenAI API key in `.env` file
3. Run: `uvicorn backend.main:app --reload`
4. Test: `python test_api.py`

See `QUICK_START_v2.md` for detailed instructions.

## API Highlights

- `POST /extract/metadata` - Extract metadata and trigger content generation
- `GET /curriculum/{id}` - Get curriculum with 25 lessons
- `GET /curriculum/{id}/content` - Get all learning content
- `GET /curriculum/{id}/lesson/{index}` - Get specific lesson content
- `GET /user/{id}/curricula` - Get user's learning history
- `GET /search/curricula` - Search existing curricula

See `API_DOCUMENTATION.md` for complete reference.

## Database Schema

Three main tables:
- `metadata_extractions` - User queries and extracted metadata
- `curricula` - 25-lesson curricula  
- `learning_content` - Flashcards, exercises, simulations per lesson

All content stored as JSON for flexibility. 