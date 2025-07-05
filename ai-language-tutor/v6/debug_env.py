#!/usr/bin/env python3
"""
Environment Variable Debug Script
Tests if environment variables are being loaded correctly
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_env_file():
    """Check if .env file exists and can be read"""
    env_path = Path(".env")
    
    print("=== .env File Check ===")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Looking for .env at: {env_path.absolute()}")
    
    if env_path.exists():
        print("✅ .env file found")
        print(f"✅ .env file size: {env_path.stat().st_size} bytes")
        
        try:
            with open(env_path, 'r') as f:
                content = f.read()
                lines = content.strip().split('\n')
                print(f"✅ .env file has {len(lines)} lines")
                
                # Show non-empty lines without showing actual values
                print("\n📋 .env file structure:")
                for i, line in enumerate(lines, 1):
                    if line.strip() and not line.startswith('#'):
                        key = line.split('=')[0] if '=' in line else line
                        print(f"  Line {i}: {key}=***")
                    elif line.strip():
                        print(f"  Line {i}: {line}")
                
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
            return False
    else:
        print("❌ .env file not found")
        print("\n💡 Create a .env file with:")
        print("GEMINI_API_KEY=your_api_key_here")
        print("GEMINI_BASE_URL=your_base_url_here")
        print("GEMINI_MODEL=gemini-2.0-flash")
        return False
    
    return True

def load_and_check_env():
    """Load environment variables and check them"""
    print("\n=== Loading Environment Variables ===")
    
    # Load .env file
    result = load_dotenv()
    print(f"load_dotenv() result: {result}")
    
    # Check required variables
    required_vars = ['GEMINI_API_KEY', 'GEMINI_BASE_URL', 'GEMINI_MODEL']
    
    print("\n📊 Environment Variables Status:")
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show first/last few chars for security
            if len(value) > 10:
                masked = f"{value[:4]}...{value[-4:]}"
            else:
                masked = "***"
            print(f"  ✅ {var}: {masked} (length: {len(value)})")
        else:
            print(f"  ❌ {var}: NOT SET")
            all_good = False
    
    # Check additional variables
    optional_vars = ['DATABASE_PATH', 'API_PORT']
    print("\n📋 Optional Variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚪ {var}: Not set (using default)")
    
    return all_good

def check_python_env():
    """Check Python environment details"""
    print("\n=== Python Environment ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
        print(f"Virtual env path: {sys.prefix}")
    else:
        print("⚠️  Not running in virtual environment")

def check_imports():
    """Check if required packages are available"""
    print("\n=== Package Imports ===")
    
    packages = [
        'dotenv',
        'openai',
        'fastapi',
        'aiosqlite',
        'uvicorn'
    ]
    
    for package in packages:
        try:
            __import__(package)
            print(f"  ✅ {package}: Available")
        except ImportError as e:
            print(f"  ❌ {package}: {e}")

def main():
    """Run all checks"""
    print("🔍 AI Language Tutor v6 - Environment Debug Tool")
    print("=" * 60)
    
    # Check Python environment
    check_python_env()
    
    # Check package imports
    check_imports()
    
    # Check .env file
    env_file_ok = check_env_file()
    
    if env_file_ok:
        # Load and check environment variables
        env_vars_ok = load_and_check_env()
        
        print("\n" + "=" * 60)
        if env_vars_ok:
            print("🎉 All environment variables are set correctly!")
            print("Try running the API again: uvicorn backend.main:app --reload")
        else:
            print("❌ Some environment variables are missing.")
            print("Fix your .env file and try again.")
    else:
        print("\n❌ Fix the .env file first, then run this script again.")
    
    print("\n💡 Next step: Run 'python debug_api.py' to test API connectivity")

if __name__ == "__main__":
    main() 