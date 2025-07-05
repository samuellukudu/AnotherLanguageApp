#!/usr/bin/env python3
"""
API Connectivity Debug Script
Tests if the API credentials and endpoints work correctly
"""

import os
import asyncio
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
import httpx

async def test_openai_client():
    """Test the OpenAI client configuration"""
    print("=== Testing OpenAI Client Configuration ===")
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    base_url = os.getenv("GEMINI_BASE_URL")
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    print(f"API Key: {api_key[:4] + '...' + api_key[-4:] if api_key else 'NOT SET'}")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    
    if not api_key:
        print("❌ GEMINI_API_KEY is not set!")
        return False
    
    if not base_url:
        print("❌ GEMINI_BASE_URL is not set!")
        return False
    
    try:
        # Initialize client
        print("\n🔧 Initializing OpenAI client...")
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        print("✅ Client initialized successfully")
        
        # Test simple completion
        print("\n🧪 Testing simple completion...")
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Respond with valid JSON."},
            {"role": "user", "content": "Say hello in JSON format with a 'message' field."}
        ]
        
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=100
        )
        
        print("✅ API call successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        
        # Try to extract more details from the error
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status_code if hasattr(e.response, 'status_code') else 'Unknown'}")
            if hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text}")
        
        return False

async def test_raw_http_request():
    """Test raw HTTP request to the API endpoint"""
    print("\n=== Testing Raw HTTP Request ===")
    
    api_key = os.getenv("GEMINI_API_KEY")
    base_url = os.getenv("GEMINI_BASE_URL")
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    if not api_key or not base_url:
        print("❌ Missing API key or base URL")
        return False
    
    # Construct the full URL
    if base_url.endswith('/'):
        url = f"{base_url}chat/completions"
    else:
        url = f"{base_url}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Respond with valid JSON."},
            {"role": "user", "content": "Say hello in JSON format."}
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 100
    }
    
    print(f"🌐 Making request to: {url}")
    print(f"🔑 Authorization header: Bearer {api_key[:4]}...{api_key[-4:]}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            print(f"📊 Response status: {response.status_code}")
            
            response_text = response.text
            print(f"📄 Response length: {len(response_text)} characters")
            
            if response.status_code == 200:
                print("✅ Raw HTTP request successful!")
                try:
                    response_json = response.json()
                    print(f"Response: {response_json.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
                    return True
                except json.JSONDecodeError:
                    print(f"⚠️  Response is not valid JSON: {response_text[:200]}...")
            else:
                print(f"❌ HTTP request failed with status {response.status_code}")
                print(f"Response: {response_text}")
                return False
                    
    except Exception as e:
        print(f"❌ Raw HTTP request failed: {e}")
        return False

async def test_backend_import():
    """Test importing the backend modules"""
    print("\n=== Testing Backend Module Import ===")
    
    try:
        # Test importing the generate_completions module
        print("🔧 Importing backend.utils.generate_completions...")
        from backend.utils import generate_completions
        print("✅ Import successful")
        
        # Test the get_completions function
        print("🧪 Testing get_completions function...")
        result = await generate_completions.get_completions(
            "Say hello",
            "You are a helpful assistant. Respond with valid JSON containing a 'message' field."
        )
        print(f"✅ Function call successful: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Backend import/test failed: {e}")
        return False

def test_env_in_current_process():
    """Test environment variables in current Python process"""
    print("\n=== Testing Environment Variables in Current Process ===")
    
    # Load .env explicitly
    load_dotenv()
    
    vars_to_check = [
        'GEMINI_API_KEY',
        'GEMINI_BASE_URL', 
        'GEMINI_MODEL',
        'DATABASE_PATH'
    ]
    
    print("📊 Environment variables after load_dotenv():")
    for var in vars_to_check:
        value = os.getenv(var)
        if value:
            if 'KEY' in var:
                masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
                print(f"  ✅ {var}: {masked}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: NOT SET")
    
    # Also check if they're in os.environ
    print("\n📋 Checking os.environ directly:")
    for var in vars_to_check:
        if var in os.environ:
            value = os.environ[var]
            if 'KEY' in var:
                masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
                print(f"  ✅ {var}: {masked} (in os.environ)")
            else:
                print(f"  ✅ {var}: {value} (in os.environ)")
        else:
            print(f"  ❌ {var}: NOT in os.environ")

async def main():
    """Run all API tests"""
    print("🔍 AI Language Tutor v6 - API Debug Tool")
    print("=" * 60)
    
    # Test environment variables
    test_env_in_current_process()
    
    # Test OpenAI client
    client_ok = await test_openai_client()
    
    # Test raw HTTP request
    if not client_ok:
        print("\n🔧 Client failed, trying raw HTTP request...")
        http_ok = await test_raw_http_request()
    else:
        http_ok = True
    
    # Test backend import
    backend_ok = await test_backend_import()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"  OpenAI Client: {'✅ PASS' if client_ok else '❌ FAIL'}")
    print(f"  Raw HTTP: {'✅ PASS' if http_ok else '❌ FAIL'}")
    print(f"  Backend Import: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    
    if client_ok and backend_ok:
        print("\n🎉 All tests passed! The API should work correctly.")
        print("Try running: uvicorn backend.main:app --reload")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")
        if not client_ok and not http_ok:
            print("💡 The issue is likely with your API credentials or endpoint.")
        elif not backend_ok:
            print("💡 The issue is with the backend module imports.")

if __name__ == "__main__":
    asyncio.run(main()) 