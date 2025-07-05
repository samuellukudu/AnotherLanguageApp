# Database Initialization System

The AI Language Tutor v6 now includes a robust database initialization system that automatically checks for the `ai_tutor.db` file, creates it if missing, and ensures proper schema setup.

## 🔧 How It Works

### Automatic Startup Checks

When you run `uvicorn backend.main:app --reload`, the system automatically:

1. **Checks if `ai_tutor.db` exists**
2. **Verifies database schema** (tables and views)
3. **Tests write permissions**
4. **Creates database if missing**
5. **Repairs database if corrupted**

### Database Health Monitoring

The system continuously monitors:
- ✅ Database file exists
- ✅ Database is accessible
- ✅ Required tables exist
- ✅ Required views exist
- ✅ Write permissions work
- ✅ Record counts

## 🚀 Usage

### 1. Automatic Initialization (Recommended)

Simply start the API - the database will be created automatically:

```bash
cd v6
source ../lang_env/bin/activate
uvicorn backend.main:app --reload
```

**Output:**
```
INFO: Starting database initialization...
INFO: Database initialization successful: created
INFO: Database records: {'metadata_extractions': 0, 'curricula': 0, 'learning_content': 0}
INFO: Application startup complete.
```

### 2. Manual Testing

Test database initialization before starting the API:

```bash
python test_db_init.py
```

This will:
- Check current database status
- Initialize database if needed
- Run comprehensive health checks
- Show database file information

### 3. Health Check Endpoint

Check database health while the API is running:

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "api_version": "2.0.0",
  "database": {
    "database_exists": true,
    "database_accessible": true,
    "schema_loaded": true,
    "tables_exist": true,
    "views_exist": true,
    "can_write": true,
    "record_count": {
      "metadata_extractions": 5,
      "curricula": 3,
      "learning_content": 75
    },
    "errors": []
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🛠️ Admin Endpoints

### Repair Database

If the database gets corrupted:

```bash
curl -X POST http://localhost:8000/admin/database/repair
```

### Recreate Database

To start fresh (⚠️ **destroys all data**):

```bash
curl -X POST http://localhost:8000/admin/database/recreate
```

## 📁 Database Location

The database file is created at:
- **Local development**: `./ai_tutor.db` (in v6 directory)
- **Docker**: `/app/ai_tutor.db` (inside container)
- **Custom path**: Set `DATABASE_PATH` environment variable

## 🔍 What Gets Created

### Tables
- `metadata_extractions` - User queries and language metadata
- `curricula` - Generated 25-lesson curricula
- `learning_content` - Flashcards, exercises, and simulations

### Views
- `user_learning_journeys` - Combined user learning data
- `curriculum_content_status` - Content generation progress

### Indexes
- User ID lookups
- Language pair searches
- Content type filtering
- Lesson indexing

## 🐛 Troubleshooting

### Database File Missing
**Problem:** `ai_tutor.db` not found

**Solution:** Automatic - the system creates it on startup

### Schema Issues
**Problem:** Tables or views missing

**Solution:** 
1. Automatic repair on startup
2. Manual: `curl -X POST http://localhost:8000/admin/database/repair`

### Permission Issues
**Problem:** Cannot write to database

**Solution:**
1. Check file permissions: `ls -la ai_tutor.db`
2. Fix permissions: `chmod 664 ai_tutor.db`
3. Check directory permissions

### Corrupted Database
**Problem:** Database file corrupted

**Solution:**
1. Try repair: `curl -X POST http://localhost:8000/admin/database/repair`
2. If repair fails: `curl -X POST http://localhost:8000/admin/database/recreate`

## 📊 Database Schema

```sql
-- Core tables
metadata_extractions (id, user_id, query, languages, metadata_json)
curricula (id, metadata_extraction_id, curriculum_json)
learning_content (id, curriculum_id, content_type, lesson_index, content_json)

-- Views for easy querying
user_learning_journeys (combined user data)
curriculum_content_status (generation progress)
```

## 🔄 Migration from Previous Versions

### From v3/v4/v5
The v6 database system is completely new. Previous versions used different schemas or no persistent storage.

**Migration steps:**
1. v6 creates a fresh database automatically
2. No data migration needed (previous versions generated content on-demand)
3. Users will need to re-generate their curricula

### Database Backup
Before major changes:

```bash
# Backup current database
cp ai_tutor.db ai_tutor.db.backup

# Restore if needed
cp ai_tutor.db.backup ai_tutor.db
```

## 🎯 Benefits

### ✅ Reliability
- Automatic database creation
- Health monitoring
- Self-repair capabilities
- Comprehensive error handling

### ✅ Performance
- Pre-generated content storage
- Indexed lookups
- Efficient queries
- Fast retrieval

### ✅ Monitoring
- Health check endpoint
- Detailed logging
- Record count tracking
- Error reporting

### ✅ Maintenance
- Admin repair endpoints
- Database recreation
- Backup support
- Schema versioning

The database initialization system ensures your AI Language Tutor v6 always has a working database, whether you're starting fresh or running an existing installation! 