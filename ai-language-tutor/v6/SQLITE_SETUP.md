# 🗄️ SQLite Content Saving for AI Language Tutor

This implementation uses SQLite to persistently save AI-generated content, starting with the metadata extraction API.

## 🎯 What's Changed

### From In-Memory Cache ➡️ SQLite Database
- **Before**: Content lost on restart, no persistence
- **After**: All content saved to SQLite database file
- **Focus**: Starting with metadata extraction API first

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install aiosqlite sqlalchemy
```

### 2. Test the Database
```bash
python test_sqlite.py
```

### 3. Start the API
```bash
uvicorn backend.main:app --reload --port 8001
```

### 4. Test Metadata Extraction
```bash
curl -X POST "http://localhost:8001/extract/metadata" \
-H "Content-Type: application/json" \
-d '{
  "query": "I want to learn Spanish for my upcoming trip to Mexico",
  "user_id": 123
}'
```

**Response**:
```json
{
  "data": {
    "native_language": "english",
    "target_language": "spanish",
    "proficiency": "beginner",
    "title": "Spanish for Travel",
    "description": "Learning Spanish basics for a trip to Mexico"
  },
  "type": "language_metadata",
  "status": "success",
  "content_id": "a3868150a198eece...",
  "saved": true
}
```

## 📊 Database Schema

### `saved_content` Table
Stores all AI-generated content:
```sql
CREATE TABLE saved_content (
    id INTEGER PRIMARY KEY,
    content_id VARCHAR(64) UNIQUE,     -- SHA-256 hash
    content_type VARCHAR(50),          -- metadata, curriculum, flashcards, etc.
    user_id INTEGER,                   -- User identifier
    query TEXT,                        -- Original user query
    generated_content TEXT,            -- JSON response from AI
    native_language VARCHAR(50),
    target_language VARCHAR(50),
    proficiency VARCHAR(20),
    created_at DATETIME,
    updated_at DATETIME
);
```

### `user_metadata` Table
Specialized table for metadata extraction:
```sql
CREATE TABLE user_metadata (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    query TEXT,
    native_language VARCHAR(50),
    target_language VARCHAR(50),
    proficiency VARCHAR(20),
    title VARCHAR(200),
    description TEXT,
    created_at DATETIME
);
```

## 🛠️ API Endpoints

### POST Endpoints (Save Content)

#### Extract Metadata (✅ Implemented)
```http
POST /extract/metadata
{
  "query": "I want to learn French",
  "user_id": 123  // Optional
}
```

#### Generate Content (✅ Updated to Save)
All generation endpoints now save content:
- `POST /generate/curriculum`
- `POST /generate/flashcards`
- `POST /generate/exercises`
- `POST /generate/simulation`

### GET Endpoints (Retrieve Saved Content)

#### Get Specific Content
```http
GET /content/{content_id}
```

#### Get User's Metadata History
```http
GET /user/{user_id}/metadata?limit=20
```

#### Get User's All Content
```http
GET /user/{user_id}/content?content_type=metadata&limit=50
```

#### Delete Content
```http
DELETE /content/{content_id}
```

## 💡 Key Features

### Content ID Generation
Each piece of content gets a unique SHA-256 hash:
```python
content_id = hash(query + content_type + user_id)
```

### Duplicate Prevention
Same query + user + content type = same content_id
Prevents duplicate storage of identical requests.

### Anonymous Support
Metadata extraction works without user_id:
```json
{
  "query": "learn italian",
  "user_id": null  // Optional
}
```

## 📁 File Structure

```
backend/
├── database.py          # SQLAlchemy models & connection
├── content_service.py   # Service for saving/retrieving content
├── main.py             # FastAPI endpoints (updated)
└── utils/
    └── handlers.py     # Generation handlers (updated)

ai_tutor.db             # SQLite database file (auto-created)
test_sqlite.py          # Test script
```

## 🔍 Monitoring & Debugging

### View SQLite Database
Use any SQLite browser:
- [DB Browser for SQLite](https://sqlitebrowser.org/) (GUI)
- SQLite CLI: `sqlite3 ai_tutor.db`

### Check Database Contents
```sql
-- View all metadata extractions
SELECT query, native_language, target_language, created_at 
FROM user_metadata 
ORDER BY created_at DESC;

-- View all saved content
SELECT content_type, COUNT(*) as count 
FROM saved_content 
GROUP BY content_type;
```

### API Logs
The application logs all saves:
```
INFO:backend.content_service:Saved metadata for query: I want to learn Spanish...
INFO:backend.content_service:Saved curriculum content for query: teach me spanish...
```

## 🎯 Next Steps

1. **✅ Metadata Extraction** - Complete and tested
2. **🔄 Content Generation** - Updated to save to database
3. **📊 Analytics** - Add usage tracking
4. **🔄 Cache Layer** - Add Redis for frequently accessed content
5. **📱 User Profiles** - Expand user metadata tracking

## 🚨 Production Considerations

### Database Location
- **Development**: `./ai_tutor.db` (current directory)
- **Production**: Use environment variable or dedicated path
- **Docker**: Mount volume for persistence

### Backup Strategy
```bash
# Simple backup
cp ai_tutor.db ai_tutor_backup_$(date +%Y%m%d).db

# Continuous backup with SQLite
sqlite3 ai_tutor.db ".backup backup.db"
```

### Performance
- SQLite handles thousands of concurrent reads
- For high-write scenarios, consider PostgreSQL
- Current setup perfect for MVP and moderate usage

## 🧪 Testing

### Run Tests
```bash
python test_sqlite.py
```

### Test Specific Functionality
```python
# Test metadata extraction
import requests
response = requests.post("http://localhost:8001/extract/metadata", json={
    "query": "voglio imparare italiano",
    "user_id": 456
})
print(response.json()["content_id"])

# Retrieve saved metadata
content_id = response.json()["content_id"]
saved_content = requests.get(f"http://localhost:8001/content/{content_id}")
print(saved_content.json())
```

This SQLite-based approach provides a solid foundation for persistent content storage with minimal setup requirements! 🎉 