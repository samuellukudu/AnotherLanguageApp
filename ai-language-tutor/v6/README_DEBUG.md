# Debugging Scripts for 401 API Key Error

This directory contains debugging scripts to help fix the **401 API key error** you're experiencing when running `uvicorn backend.main:app`.

## Quick Start

1. **Navigate to v6 directory and activate virtual environment:**
   ```bash
   cd v6
   source ../lang_env/bin/activate
   ```

2. **Run the comprehensive diagnostic:**
   ```bash
   python debug_fix.py
   ```

3. **If .env file is missing, create it:**
   ```bash
   python create_env_file.py
   ```

4. **Fix your .env file with real values and test again:**
   ```bash
   python debug_fix.py
   ```

## Available Scripts

| Script | Purpose |
|--------|---------|
| **`debug_fix.py`** | 🔧 **Start here** - comprehensive diagnosis and fix |
| **`create_env_file.py`** | 📝 Create template .env file with proper format |
| **`debug_env.py`** | 🔍 Test environment variable loading |
| **`debug_api.py`** | 🌐 Test API connectivity |
| **`test_minimal.py`** | 🔬 Reproduce the exact 401 error |

## Most Common Issue

The 401 error typically means your `.env` file is either:
- Missing from the v6 directory
- Missing the `GEMINI_API_KEY` line
- Has incorrect format (spaces, quotes, etc.)

## Quick Fix Example

If you're using Fireworks AI, your `.env` should look like:
```
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_BASE_URL=https://api.fireworks.ai/inference/v1
GEMINI_MODEL=accounts/fireworks/models/gemini-2-0-flash-thinking-exp
```

## Need Help?

1. Run `python debug_fix.py` and follow the error messages
2. Read the full guide: `DEBUG_GUIDE.md`
3. If all scripts pass but FastAPI still fails, the issue might be elsewhere

## Once Fixed

When all debugging scripts pass:
```bash
uvicorn backend.main:app --reload
```

The API should start without the 401 error and begin generating content automatically. 