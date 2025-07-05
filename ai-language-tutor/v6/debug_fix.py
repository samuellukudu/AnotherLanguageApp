#!/usr/bin/env python3
"""
Comprehensive Debug and Fix Script
Diagnoses the API key issue and provides fixes
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI

class DebugFixer:
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
        self.env_loaded = False
    
    def log_issue(self, issue):
        """Log an issue found"""
        self.issues_found.append(issue)
        print(f"❌ {issue}")
    
    def log_fix(self, fix):
        """Log a fix applied"""
        self.fixes_applied.append(fix)
        print(f"✅ {fix}")
    
    def check_working_directory(self):
        """Check if we're in the right directory"""
        print("=== Step 1: Check Working Directory ===")
        
        cwd = os.getcwd()
        print(f"Current directory: {cwd}")
        
        # Check if we're in v6 directory
        if not cwd.endswith('v6'):
            self.log_issue(f"Not in v6 directory (currently in {os.path.basename(cwd)})")
            print("💡 Run: cd v6")
            return False
        
        # Check if backend directory exists
        backend_path = Path("backend")
        if not backend_path.exists():
            self.log_issue("backend/ directory not found")
            return False
        
        self.log_fix("Working directory is correct")
        return True
    
    def check_virtual_env(self):
        """Check if virtual environment is activated"""
        print("\n=== Step 2: Check Virtual Environment ===")
        
        # Check if in virtual environment
        in_venv = (hasattr(sys, 'real_prefix') or 
                  (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
        
        if in_venv:
            self.log_fix(f"Virtual environment activated: {sys.prefix}")
            
            # Check if it's the right one (lang_env)
            if 'lang_env' in sys.prefix:
                self.log_fix("Using lang_env virtual environment")
            else:
                print(f"⚠️  Using different virtual environment: {os.path.basename(sys.prefix)}")
        else:
            self.log_issue("Virtual environment not activated")
            print("💡 Run: source ../lang_env/bin/activate")
            return False
        
        return True
    
    def check_env_file(self):
        """Check and potentially fix .env file"""
        print("\n=== Step 3: Check .env File ===")
        
        env_path = Path(".env")
        
        if not env_path.exists():
            self.log_issue(".env file does not exist")
            print("💡 Run: python create_env_file.py")
            return False
        
        try:
            with open(env_path, 'r') as f:
                content = f.read()
            
            # Check for required variables
            required_vars = ['GEMINI_API_KEY', 'GEMINI_BASE_URL']
            missing = []
            placeholder = []
            
            for var in required_vars:
                if f"{var}=" not in content:
                    missing.append(var)
                elif any(placeholder_text in content for placeholder_text in [
                    f"{var}=your_", f"{var}=YOUR_", f"{var}=<", f"{var}=xxx"
                ]):
                    placeholder.append(var)
            
            if missing:
                self.log_issue(f"Missing variables in .env: {', '.join(missing)}")
                return False
            
            if placeholder:
                self.log_issue(f"Placeholder values in .env: {', '.join(placeholder)}")
                print("💡 Edit .env file and set real values")
                return False
            
            self.log_fix(".env file structure looks good")
            return True
            
        except Exception as e:
            self.log_issue(f"Error reading .env file: {e}")
            return False
    
    def load_and_test_env_vars(self):
        """Load environment variables and test them"""
        print("\n=== Step 4: Load and Test Environment Variables ===")
        
        # Load .env file
        result = load_dotenv()
        self.env_loaded = result
        print(f"load_dotenv() result: {result}")
        
        if not result:
            self.log_issue("Failed to load .env file")
            return False
        
        # Check variables
        api_key = os.getenv("GEMINI_API_KEY")
        base_url = os.getenv("GEMINI_BASE_URL") 
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        
        if not api_key:
            self.log_issue("GEMINI_API_KEY not loaded")
            return False
        
        if not base_url:
            self.log_issue("GEMINI_BASE_URL not loaded")
            return False
        
        # Validate API key format
        if len(api_key) < 10:
            self.log_issue("API key seems too short")
            return False
        
        # Validate base URL format
        if not base_url.startswith('http'):
            self.log_issue("Base URL should start with http:// or https://")
            return False
        
        self.log_fix(f"API Key loaded (length: {len(api_key)})")
        self.log_fix(f"Base URL: {base_url}")
        self.log_fix(f"Model: {model}")
        
        return True
    
    async def test_api_connection(self):
        """Test actual API connection"""
        print("\n=== Step 5: Test API Connection ===")
        
        if not self.env_loaded:
            self.log_issue("Environment variables not loaded, skipping API test")
            return False
        
        api_key = os.getenv("GEMINI_API_KEY")
        base_url = os.getenv("GEMINI_BASE_URL")
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        
        try:
            print("🔧 Creating OpenAI client...")
            client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url
            )
            
            print("🧪 Testing simple API call...")
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Hello, API is working!' exactly."}
                ],
                max_tokens=20
            )
            
            result = response.choices[0].message.content
            print(f"API Response: {result}")
            
            if "Hello" in result or "working" in result:
                self.log_fix("API connection successful!")
                return True
            else:
                self.log_issue(f"Unexpected API response: {result}")
                return False
                
        except Exception as e:
            self.log_issue(f"API connection failed: {e}")
            
            # Try to provide specific guidance based on error
            error_str = str(e).lower()
            if "401" in error_str or "unauthorized" in error_str:
                print("💡 This is an authentication error. Check your API key.")
            elif "404" in error_str:
                print("💡 This might be a wrong base URL or model name.")
            elif "timeout" in error_str:
                print("💡 This might be a network issue or wrong base URL.")
            
            return False
    
    async def test_backend_integration(self):
        """Test the backend integration"""
        print("\n=== Step 6: Test Backend Integration ===")
        
        try:
            # Import the generate_completions module
            print("🔧 Importing backend.utils.generate_completions...")
            from backend.utils import generate_completions
            
            print("🧪 Testing get_completions function...")
            result = await generate_completions.get_completions(
                user_input="Test message",
                system_prompt="Respond with 'Backend integration working!'"
            )
            
            if result and "working" in result.lower():
                self.log_fix("Backend integration successful!")
                return True
            else:
                self.log_issue(f"Backend integration issue: {result}")
                return False
                
        except Exception as e:
            self.log_issue(f"Backend integration failed: {e}")
            return False
    
    def generate_report(self):
        """Generate a diagnostic report"""
        print("\n" + "=" * 60)
        print("🔍 DIAGNOSTIC REPORT")
        print("=" * 60)
        
        print(f"\n❌ Issues Found ({len(self.issues_found)}):")
        for i, issue in enumerate(self.issues_found, 1):
            print(f"  {i}. {issue}")
        
        print(f"\n✅ Fixes Applied ({len(self.fixes_applied)}):")
        for i, fix in enumerate(self.fixes_applied, 1):
            print(f"  {i}. {fix}")
        
        if not self.issues_found:
            print("\n🎉 No issues found! Your setup should work correctly.")
            print("Try running: uvicorn backend.main:app --reload")
        else:
            print(f"\n🔧 Next Steps:")
            print("1. Fix the issues listed above")
            print("2. Run this script again to verify fixes")
            print("3. If all issues are resolved, try running the API")
    
    async def run_diagnosis(self):
        """Run complete diagnosis"""
        print("🔍 AI Language Tutor v6 - Comprehensive Debug & Fix Tool")
        print("=" * 60)
        
        # Run all checks
        checks = [
            self.check_working_directory(),
            self.check_virtual_env(),
            self.check_env_file(),
            self.load_and_test_env_vars()
        ]
        
        # Only test API if basic checks pass
        if all(checks):
            api_ok = await self.test_api_connection()
            checks.append(api_ok)
            
            # Only test backend if API works
            if api_ok:
                backend_ok = await self.test_backend_integration()
                checks.append(backend_ok)
        
        # Generate report
        self.generate_report()
        
        return all(checks) if checks else False

async def main():
    """Main function"""
    fixer = DebugFixer()
    success = await fixer.run_diagnosis()
    
    if success:
        print("\n🚀 Ready to run the API!")
        print("Command: uvicorn backend.main:app --reload")
    else:
        print("\n🛠️  Please fix the issues above and try again.")
        print("\nHelpful commands:")
        print("- python create_env_file.py  # Create/fix .env file")
        print("- python debug_env.py        # Check environment variables")  
        print("- python debug_api.py        # Test API connectivity")

if __name__ == "__main__":
    asyncio.run(main()) 