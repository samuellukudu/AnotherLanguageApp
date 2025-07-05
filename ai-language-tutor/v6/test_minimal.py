#!/usr/bin/env python3
"""
Minimal Test Script
Reproduces the exact error you're seeing in the FastAPI app
"""

import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

async def test_exact_failure():
    """Test the exact same setup that's failing in your FastAPI app"""
    
    print("🔬 Minimal Test - Reproducing FastAPI Error")
    print("=" * 50)
    
    # Load environment variables exactly like your app does
    print("1. Loading environment variables...")
    load_dotenv()
    
    # Get the same variables your app uses
    api_key = os.getenv("GEMINI_API_KEY")
    base_url = os.getenv("GEMINI_BASE_URL")
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    print(f"   API Key: {'✅ Set' if api_key else '❌ NOT SET'}")
    print(f"   Base URL: {'✅ Set' if base_url else '❌ NOT SET'}")
    print(f"   Model: {model}")
    
    if not api_key:
        print("\n❌ GEMINI_API_KEY is None - this will cause the 401 error!")
        print("💡 Fix: Make sure your .env file has GEMINI_API_KEY=your_actual_key")
        return False
    
    if not base_url:
        print("\n❌ GEMINI_BASE_URL is None - this will cause connection errors!")
        print("💡 Fix: Make sure your .env file has GEMINI_BASE_URL=your_api_endpoint")
        return False
    
    # Create client exactly like your generate_completions.py does
    print("\n2. Creating OpenAI client...")
    try:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        print("   ✅ Client created successfully")
    except Exception as e:
        print(f"   ❌ Client creation failed: {e}")
        return False
    
    # Test the exact API call that's failing
    print("\n3. Testing API call (this is line 76 in generate_completions.py)...")
    
    try:
        # This mimics the exact call in your backend
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Test message"}
            ],
            max_tokens=50
        )
        
        print("   ✅ API call successful!")
        print(f"   Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"   ❌ API call failed: {e}")
        
        # Check if it's the exact error you're seeing
        error_str = str(e)
        if "401" in error_str and "didn't provide an API key" in error_str:
            print("\n🎯 THIS IS THE EXACT ERROR YOU'RE SEEING!")
            print("\n🔍 Diagnosis:")
            print("   - The API key is being passed as None to the OpenAI client")
            print("   - This happens when os.getenv('GEMINI_API_KEY') returns None")
            print("   - Usually caused by:")
            print("     1. .env file not in the current directory")
            print("     2. .env file missing GEMINI_API_KEY line")
            print("     3. .env file has wrong format (spaces, quotes, etc.)")
            print("     4. load_dotenv() not finding/loading the .env file")
            
            print("\n🔧 Quick Fix:")
            print("   1. Run: python create_env_file.py")
            print("   2. Edit .env and set your real API key")
            print("   3. Run: python debug_env.py to verify")
        
        return False

def test_env_loading():
    """Test environment loading in detail"""
    print("\n" + "=" * 50)
    print("🔍 Detailed Environment Variable Test")
    print("=" * 50)
    
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if .env file exists
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ .env file found: {os.path.abspath(env_file)}")
        
        # Read and analyze .env file
        try:
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            print(f"✅ .env file has {len(lines)} lines")
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key = line.split('=')[0]
                        print(f"   Line {i}: {key}=***")
                    else:
                        print(f"   Line {i}: {line}")
                        
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
    else:
        print(f"❌ .env file not found in {os.getcwd()}")
    
    # Test load_dotenv()
    print(f"\nTesting load_dotenv()...")
    result = load_dotenv()
    print(f"load_dotenv() returned: {result}")
    
    # Check specific variables
    vars_to_check = ['GEMINI_API_KEY', 'GEMINI_BASE_URL', 'GEMINI_MODEL']
    print(f"\nChecking environment variables:")
    
    for var in vars_to_check:
        value = os.getenv(var)
        if value:
            if 'KEY' in var:
                print(f"   ✅ {var}: {value[:4]}...{value[-4:]} (length: {len(value)})")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: None")

async def main():
    """Run all tests"""
    print("🔬 AI Language Tutor v6 - Minimal Error Reproduction")
    print("This script reproduces the exact 401 error you're seeing")
    print("=" * 60)
    
    # Test environment loading first
    test_env_loading()
    
    # Test the exact failure
    success = await test_exact_failure()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS! Your API setup is working correctly.")
        print("The 401 error in your FastAPI app might be caused by something else.")
        print("Try running your FastAPI app again: uvicorn backend.main:app --reload")
    else:
        print("❌ REPRODUCED THE ERROR!")
        print("This is the same issue causing your FastAPI 401 error.")
        print("\nNext steps:")
        print("1. Fix the issues identified above")
        print("2. Run this script again until it passes")
        print("3. Then try your FastAPI app")

if __name__ == "__main__":
    asyncio.run(main()) 