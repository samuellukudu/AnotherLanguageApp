# AI Language Tutor v6 - Debug Guide

This guide helps you diagnose and fix the **401 API key error** you're experiencing.

## Quick Fix (Most Common Issues)

The 401 error usually means your API key isn't being loaded properly. Here's the quickest way to fix it:

### 1. Check Your Current Setup
```bash
# Make sure you're in the v6 directory
cd v6

# Make sure virtual environment is activated
source ../lang_env/bin/activate

# Run the comprehensive diagnostic
python debug_fix.py
```

### 2. If .env File is Missing
```bash
# Create a template .env file
python create_env_file.py

# Edit the .env file with your real values
nano .env  # or use your preferred editor
```

### 3. If Environment Variables Aren't Loading
```bash
# Test environment variable loading
python debug_env.py

# Test API connectivity 
python debug_api.py
```

## Debug Scripts Overview

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `debug_fix.py` | **🔧 Main diagnostic tool** | Start here - comprehensive diagnosis |
| `create_env_file.py` | **📝 Create/fix .env file** | When .env is missing or malformed |
| `debug_env.py` | **🔍 Check environment variables** | When variables aren't loading |
| `debug_api.py` | **🌐 Test API connectivity** | When API calls are failing |

## Step-by-Step Troubleshooting

### Step 1: Run Main Diagnostic
```bash
python debug_fix.py
```

This script will:
- ✅ Check if you're in the right directory
- ✅ Verify virtual environment is activated
- ✅ Validate .env file exists and has correct structure
- ✅ Load and test environment variables
- ✅ Test actual API connection
- ✅ Test backend integration

### Step 2: Fix Issues Found

**If .env file doesn't exist:**
```bash
python create_env_file.py
# Then edit .env with your real API key and settings
```

**If environment variables aren't loading:**
```bash
python debug_env.py
# This will show exactly what's loaded and what's missing
```

**If API connection fails:**
```bash
python debug_api.py
# This will test both OpenAI client and raw HTTP requests
```

### Step 3: Verify Fix
```bash
# Run diagnostic again to confirm everything works
python debug_fix.py

# If all tests pass, start the API
uvicorn backend.main:app --reload
```

## Common Issues and Solutions

### Issue 1: "GEMINI_API_KEY not loaded"

**Cause:** Environment variables aren't being loaded from .env file

**Solution:**
1. Check if .env file exists in v6 directory
2. Make sure .env has `GEMINI_API_KEY=your_actual_key`
3. No spaces around the `=` sign
4. No quotes around the value (unless part of the key)

**Example .env:**
```
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_BASE_URL=https://api.fireworks.ai/inference/v1
GEMINI_MODEL=accounts/fireworks/models/gemini-2-0-flash-thinking-exp
```

### Issue 2: "401 - You didn't provide an API key"

**Cause:** API key is None when passed to OpenAI client

**Solution:**
1. Run `python debug_env.py` to see what's actually loaded
2. Check your .env file format
3. Make sure you're in the right directory (v6)
4. Verify virtual environment is activated

### Issue 3: "404 Not Found" or model errors

**Cause:** Wrong base URL or model name for your provider

**Solution:**
Check these common configurations:

**Fireworks AI:**
```
GEMINI_BASE_URL=https://api.fireworks.ai/inference/v1
GEMINI_MODEL=accounts/fireworks/models/gemini-2-0-flash-thinking-exp
```

**Together AI:**
```
GEMINI_BASE_URL=https://api.together.xyz/v1
GEMINI_MODEL=google/gemini-2.0-flash-thinking-exp
```

**OpenRouter:**
```
GEMINI_BASE_URL=https://openrouter.ai/api/v1
GEMINI_MODEL=google/gemini-2.0-flash-thinking-exp
```

### Issue 4: Virtual environment problems

**Cause:** Not using the right virtual environment

**Solution:**
```bash
# Deactivate current environment
deactivate

# Navigate to project root and activate lang_env
cd ..
source lang_env/bin/activate

# Go back to v6 and try again
cd v6
python debug_fix.py
```

## Manual Testing

If the scripts don't work, you can manually test:

### Test 1: Check if .env loads
```python
from dotenv import load_dotenv
import os

load_dotenv()
print("API Key:", os.getenv("GEMINI_API_KEY"))
print("Base URL:", os.getenv("GEMINI_BASE_URL"))
```

### Test 2: Test API directly
```python
import asyncio
from openai import AsyncOpenAI
import os

async def test():
    client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url=os.getenv("GEMINI_BASE_URL")
    )
    
    response = await client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print(response.choices[0].message.content)

asyncio.run(test())
```

## Getting Help

If you're still having issues:

1. **Run the full diagnostic:**
   ```bash
   python debug_fix.py > debug_output.txt 2>&1
   ```

2. **Check the exact error:**
   ```bash
   python debug_api.py > api_debug.txt 2>&1
   ```

3. **Show your .env structure (without revealing keys):**
   ```bash
   python debug_env.py
   ```

4. **Test the exact same setup as v3:**
   Compare your v3 configuration with v6 to see what changed.

## Next Steps

Once all debugging scripts pass:

1. **Start the API:**
   ```bash
   uvicorn backend.main:app --reload
   ```

2. **Test with curl:**
   ```bash
   curl -X POST "http://localhost:8000/extract/metadata" \
        -H "Content-Type: application/json" \
        -d '{"text": "I want to learn Spanish", "user_id": "test-user"}'
   ```

3. **Check the logs:**
   The API should start generating content automatically after the metadata extraction.

Remember: The 401 error specifically means the API key isn't reaching the OpenAI client properly, so focus on the environment variable loading first! 