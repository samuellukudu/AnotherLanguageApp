#!/usr/bin/env python3
"""
Create .env file helper script
Helps create a properly formatted .env file with the required variables
"""

import os
from pathlib import Path

def create_env_template():
    """Create a template .env file"""
    
    template = """# AI Language Tutor v6 Environment Variables
# Copy this file to .env and fill in your actual values

# Gemini API Configuration (via OpenAI-compatible proxy)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_BASE_URL=https://api.fireworks.ai/inference/v1
GEMINI_MODEL=accounts/fireworks/models/gemini-2-0-flash-thinking-exp

# Alternative providers (uncomment and modify as needed):
# For Together AI:
# GEMINI_BASE_URL=https://api.together.xyz/v1
# GEMINI_MODEL=google/gemini-2.0-flash-thinking-exp

# For OpenRouter:
# GEMINI_BASE_URL=https://openrouter.ai/api/v1
# GEMINI_MODEL=google/gemini-2.0-flash-thinking-exp

# Database Configuration
DATABASE_PATH=./ai_tutor.db

# Optional: API Port (default is 8000)
API_PORT=8000
"""
    
    env_path = Path(".env")
    
    print("🔧 AI Language Tutor v6 - .env File Creator")
    print("=" * 50)
    
    if env_path.exists():
        print(f"⚠️  .env file already exists at: {env_path.absolute()}")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("Cancelled. Your existing .env file was not modified.")
            return False
    
    try:
        with open(env_path, 'w') as f:
            f.write(template)
        
        print(f"✅ Created .env template at: {env_path.absolute()}")
        print("\n📝 Next steps:")
        print("1. Edit the .env file and replace 'your_gemini_api_key_here' with your actual API key")
        print("2. Update GEMINI_BASE_URL if using a different provider")
        print("3. Update GEMINI_MODEL if using a different model")
        print("4. Run 'python debug_env.py' to verify your configuration")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def show_provider_examples():
    """Show examples for different API providers"""
    
    print("\n🌐 Popular Gemini API Providers:")
    print("-" * 40)
    
    providers = [
        {
            "name": "Fireworks AI",
            "base_url": "https://api.fireworks.ai/inference/v1",
            "model": "accounts/fireworks/models/gemini-2-0-flash-thinking-exp",
            "note": "Fast and reliable"
        },
        {
            "name": "Together AI", 
            "base_url": "https://api.together.xyz/v1",
            "model": "google/gemini-2.0-flash-thinking-exp",
            "note": "Good for high-volume usage"
        },
        {
            "name": "OpenRouter",
            "base_url": "https://openrouter.ai/api/v1", 
            "model": "google/gemini-2.0-flash-thinking-exp",
            "note": "Multiple model access"
        }
    ]
    
    for provider in providers:
        print(f"\n{provider['name']} ({provider['note']}):")
        print(f"  GEMINI_BASE_URL={provider['base_url']}")
        print(f"  GEMINI_MODEL={provider['model']}")

def validate_existing_env():
    """Validate an existing .env file"""
    
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ No .env file found. Run this script to create one.")
        return False
    
    print("🔍 Validating existing .env file...")
    
    try:
        with open(env_path, 'r') as f:
            content = f.read()
        
        required_vars = ['GEMINI_API_KEY', 'GEMINI_BASE_URL']
        missing_vars = []
        placeholder_vars = []
        
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)
            elif f"{var}=your_" in content or f"{var}=YOUR_" in content:
                placeholder_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing variables: {', '.join(missing_vars)}")
        
        if placeholder_vars:
            print(f"⚠️  Variables with placeholder values: {', '.join(placeholder_vars)}")
        
        if not missing_vars and not placeholder_vars:
            print("✅ .env file looks good!")
            return True
        else:
            print("❌ .env file needs to be updated")
            return False
            
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def main():
    """Main function"""
    
    print("🔧 AI Language Tutor v6 - Environment Setup Helper")
    print("=" * 60)
    
    # Check if .env exists
    env_path = Path(".env")
    
    if env_path.exists():
        print("📋 Found existing .env file")
        if validate_existing_env():
            print("\n🎉 Your .env file is properly configured!")
            print("Run 'python debug_env.py' to test it.")
        else:
            print("\n🔧 Your .env file needs updates.")
            response = input("Do you want to recreate it? (y/N): ").strip().lower()
            if response == 'y':
                create_env_template()
    else:
        print("📝 No .env file found. Creating template...")
        create_env_template()
    
    show_provider_examples()
    
    print("\n💡 Troubleshooting Tips:")
    print("- Make sure your API key is correct and has sufficient credits")
    print("- Some providers require specific model names")
    print("- The base URL should NOT include '/chat/completions' at the end")
    print("- Run 'python debug_env.py' to verify your setup")
    print("- Run 'python debug_api.py' to test API connectivity")

if __name__ == "__main__":
    main() 