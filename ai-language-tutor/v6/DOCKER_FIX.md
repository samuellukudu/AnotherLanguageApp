# Docker Environment Variable Fix

## Problem Identified ✅

You're absolutely right! The issue was with Docker, not your local setup. The 401 API key error only occurred in Docker because:

1. **Wrong environment variable name**: `docker-compose.yml` was using `OPENAI_API_KEY` instead of `GEMINI_API_KEY`
2. **Missing environment variables**: `GEMINI_BASE_URL` and `GEMINI_MODEL` weren't passed to the container
3. **No .env file in container**: The Dockerfile wasn't copying your `.env` file

## What I Fixed 🔧

### 1. Updated `docker-compose.yml`
**Before:**
```yaml
environment:
  - OPENAI_API_KEY=${OPENAI_API_KEY}  # ❌ Wrong variable name
  - DATABASE_PATH=./ai_tutor.db
```

**After:**
```yaml
environment:
  - GEMINI_API_KEY=${GEMINI_API_KEY}     # ✅ Correct variable name
  - GEMINI_BASE_URL=${GEMINI_BASE_URL}   # ✅ Added missing variable
  - GEMINI_MODEL=${GEMINI_MODEL:-gemini-2.0-flash}  # ✅ Added with default
  - DATABASE_PATH=./ai_tutor.db
env_file:
  - .env  # ✅ Load .env file into container
```

### 2. Updated `Dockerfile`
**Added:**
```dockerfile
COPY .env* ./  # Copy .env file to container
```

## How to Test the Fix 🧪

### Option 1: Use Fixed Docker Setup
```bash
# Test the Docker configuration
python docker-debug.py

# If all tests pass, run with Docker
docker-compose up --build
```

### Option 2: Continue Using Local (Recommended for Development)
Since your local setup works perfectly:
```bash
cd v6
source ../lang_env/bin/activate
uvicorn backend.main:app --reload
```

## Why This Happened 🤔

Docker containers are isolated environments. When you run `uvicorn` locally:
- It reads your `.env` file from the v6 directory
- It has access to your environment variables
- Everything works perfectly

When you run with Docker:
- The container didn't have your `.env` file
- The environment variables were mapped incorrectly
- The API key never reached the OpenAI client

## Docker vs Local Development 📊

| Aspect | Local (`uvicorn`) | Docker |
|--------|------------------|---------|
| **Setup** | ✅ Simple | ⚠️ More complex |
| **Environment** | ✅ Uses your .env directly | ❌ Needs explicit mapping |
| **Development** | ✅ Hot reload, easy debugging | ⚠️ Rebuild needed for changes |
| **Production** | ❌ Not portable | ✅ Consistent across environments |

## Recommendation 💡

**For Development**: Continue using local setup
```bash
uvicorn backend.main:app --reload
```

**For Production**: Use the fixed Docker setup
```bash
docker-compose up --build
```

## Testing Your Docker Fix

Run the Docker debug script to verify everything works:
```bash
python docker-debug.py
```

This will:
- ✅ Check Docker installation
- ✅ Verify .env file exists
- ✅ Validate docker-compose.yml configuration
- ✅ Test Docker build
- ✅ Test environment variables inside container

## Summary

Your instinct was correct - the issue was Docker-specific! Your local environment setup is perfect, and now your Docker setup should work too. The 401 error was happening because the Docker container wasn't receiving the `GEMINI_API_KEY` environment variable. 