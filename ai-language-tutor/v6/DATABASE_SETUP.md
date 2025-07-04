# Database Setup Guide for AI Language Tutor

This guide explains how to set up and use the database caching functionality that improves performance by persisting generated content.

## Features Added

- **Persistent Caching**: Generated content is stored in PostgreSQL database
- **GET Endpoints**: Retrieve cached content without regenerating
- **User Analytics**: Track access patterns and usage statistics
- **Cache Keys**: Reference generated content for future retrieval

## Database Setup

### Option 1: Using Docker (Recommended)

1. **Start PostgreSQL with Docker Compose**:
```bash
docker-compose up -d postgres
```

2. **Set Environment Variables**:
Create a `.env` file in the project root:
```env
# AI API Configuration
BASE_URL=https://api.openai.com/v1
API_KEY=your_openai_api_key_here
MODEL=gpt-4-turbo-preview

# Database Configuration
DATABASE_URL=postgresql+asyncpg://ai_tutor:password123@localhost:5432/ai_tutor_db

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
```

3. **Initialize Database Tables**:
```bash
python backend/database_init.py
```

### Option 2: Manual PostgreSQL Setup

1. **Install PostgreSQL**:
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql
```

2. **Create Database and User**:
```sql
-- Connect to PostgreSQL as superuser
sudo -u postgres psql

-- Create database and user
CREATE DATABASE ai_tutor_db;
CREATE USER ai_tutor WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_tutor_db TO ai_tutor;
```

3. **Update Environment Variables**:
```env
DATABASE_URL=postgresql+asyncpg://ai_tutor:your_password@localhost:5432/ai_tutor_db
```

4. **Initialize Tables**:
```bash
python backend/database_init.py
```

## API Changes

### New GET Endpoints

#### 1. Get Cached Content by Cache Key
```http
GET /content/{cache_key}
```

**Response**:
```json
{
  "data": "...generated content...",
  "type": "curriculum",
  "query": "original query",
  "created_at": "2024-01-01T12:00:00",
  "access_count": 5,
  "status": "success"
}
```

#### 2. Get User's Cached Content
```http
GET /user/{user_id}/content?content_type=curriculum&limit=20
```

**Response**:
```json
{
  "data": [
    {
      "cache_key": "abc123...",
      "content_type": "curriculum",
      "query": "learn spanish",
      "content": "...generated content...",
      "native_language": "english",
      "target_language": "spanish",
      "proficiency": "beginner",
      "created_at": "2024-01-01T12:00:00",
      "access_count": 3
    }
  ],
  "total": 1,
  "user_id": 123,
  "status": "success"
}
```

#### 3. Delete Cached Content
```http
DELETE /content/{cache_key}
```

### Updated POST Endpoints

All existing POST endpoints now return a `cache_key` field:

```json
{
  "data": "...generated content...",
  "type": "curriculum",
  "status": "success",
  "cache_key": "abc123def456..."
}
```

## Performance Benefits

- **Instant Retrieval**: Cached content loads immediately via GET endpoints
- **Reduced API Costs**: No duplicate API calls for same queries
- **Persistent Storage**: Content survives application restarts
- **Analytics**: Track popular content and user patterns

## Usage Examples

### 1. Generate and Cache Content
```python
import requests

# Generate curriculum (creates cache entry)
response = requests.post("/generate/curriculum", json={
    "user_id": 123,
    "query": "learn spanish basics",
    "native_language": "english",
    "target_language": "spanish",
    "proficiency": "beginner"
})

cache_key = response.json()["cache_key"]
```

### 2. Retrieve Cached Content
```python
# Get the same content instantly
cached_response = requests.get(f"/content/{cache_key}")
print(f"Access count: {cached_response.json()['access_count']}")
```

### 3. Browse User History
```python
# Get all curricula for a user
user_content = requests.get("/user/123/content?content_type=curriculum")
for item in user_content.json()["data"]:
    print(f"Query: {item['query']}")
    print(f"Created: {item['created_at']}")
```

## Database Management

### Reset Database (⚠️ Deletes all data)
```bash
python backend/database_init.py --reset
```

### Backup Database
```bash
pg_dump ai_tutor_db > backup.sql
```

### Restore Database
```bash
psql ai_tutor_db < backup.sql
```

## Monitoring

The database tracks:
- `access_count`: How many times content was retrieved
- `last_accessed`: When content was last accessed
- `created_at`: When content was first generated
- User patterns and popular content types

This data can be used for analytics and performance optimization. 