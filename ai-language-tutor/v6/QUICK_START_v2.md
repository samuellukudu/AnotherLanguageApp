# Quick Start Guide - AI Language Tutor v2.0

## Overview

The v6 implementation is a complete rewrite that uses pure SQLite for database operations and automatically generates all learning content when metadata is extracted.

## Key Features

1. **Pure SQLite**: No complex database setup required
2. **Automatic Content Generation**: All 25 lessons with flashcards, exercises, and simulations are generated automatically
3. **Fast Retrieval**: Pre-generated content is stored in the database for instant access
4. **RESTful API**: Clean GET endpoints for retrieving stored content

## Setup Instructions

### 1. Install Dependencies

```bash
cd v6
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the v6 directory with the following content:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4 for better quality

# Database Configuration
DATABASE_PATH=./ai_tutor.db

# API Configuration (optional)
API_PORT=8000
```

**Important Notes:**
- Replace `your_openai_api_key_here` with your actual OpenAI API key
- `gpt-3.5-turbo` is faster and cheaper, `gpt-4` provides better quality content
- The database file will be created automatically on first run

### 3. Run the Application

#### Option A: Direct Python
```bash
cd v6
uvicorn backend.main:app --reload
```

#### Option B: Docker
```bash
cd v6
docker-compose up --build
```

The API will be available at `http://localhost:8000`

## How It Works

### Step 1: Extract Metadata and Generate Content

```bash
curl -X POST http://localhost:8000/extract/metadata \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I want to learn Spanish for my trip to Mexico",
    "user_id": 123
  }'
```

This single request:
1. Extracts language learning metadata
2. Generates a 25-lesson curriculum
3. Starts background generation of all learning content

Response includes:
- `extraction_id`: Unique ID for the metadata extraction
- `curriculum_id`: Unique ID for the generated curriculum
- `content_generation_started`: Indicates background generation has begun

### Step 2: Check Content Generation Status

```bash
curl http://localhost:8000/content/status/{curriculum_id}
```

Returns completion percentage and status for all content types.

### Step 3: Retrieve Content

Once generation is complete, you can retrieve content:

**Get full curriculum:**
```bash
curl http://localhost:8000/curriculum/{curriculum_id}
```

**Get all flashcards:**
```bash
curl http://localhost:8000/curriculum/{curriculum_id}/content?content_type=flashcards
```

**Get content for a specific lesson:**
```bash
curl http://localhost:8000/curriculum/{curriculum_id}/lesson/0
```

**Get user's learning history:**
```bash
curl http://localhost:8000/user/123/curricula
```

## Testing

Run the included test script:
```bash
python test_api.py
```

This demonstrates the complete workflow from metadata extraction to content retrieval.

## Database Schema

The system uses three main tables:
- `metadata_extractions`: Stores user queries and extracted metadata
- `curricula`: Stores 25-lesson curricula
- `learning_content`: Stores flashcards, exercises, and simulations

All content is stored as JSON for flexibility and easy retrieval.

## API Documentation

See `API_DOCUMENTATION.md` for complete endpoint documentation.

## Differences from v3

| Feature | v3 | v6 |
|---------|----|----|
| Content Generation | On-demand | Automatic background generation |
| Storage | Cache only | Persistent SQLite database |
| Retrieval Speed | Slow (regenerates) | Fast (pre-generated) |
| API Endpoints | POST only | POST for generation, GET for retrieval |
| User Tracking | Limited | Full history with unique IDs |

## Troubleshooting

1. **Database not found**: The schema.sql file will automatically create the database on first run
2. **Content not generating**: Check OpenAI API key and rate limits
3. **Slow generation**: Content generation for 25 lessons × 3 content types can take 5-10 minutes

## Next Steps

1. Monitor content generation with `/content/status/{curriculum_id}`
2. Use GET endpoints to retrieve pre-generated content
3. Search existing curricula with `/search/curricula`
4. Track user progress with `/user/{user_id}/journeys` 