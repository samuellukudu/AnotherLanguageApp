#!/usr/bin/env python3
"""
Docker Environment Debug Script
Helps debug environment variable issues in Docker containers
"""

import os
import subprocess
import json
from pathlib import Path

def check_docker_setup():
    """Check Docker setup and configuration"""
    print("🐳 Docker Environment Debug Tool")
    print("=" * 50)
    
    # Check if Docker is running
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        print(f"✅ Docker version: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Docker not found. Install Docker first.")
        return False
    
    # Check if docker-compose is available
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        print(f"✅ Docker Compose version: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Docker Compose not found.")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\n=== .env File Check ===")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        print("💡 Create one with: python create_env_file.py")
        return False
    
    print("✅ .env file found")
    
    # Read and check required variables
    required_vars = ['GEMINI_API_KEY', 'GEMINI_BASE_URL']
    missing_vars = []
    
    try:
        with open(env_path, 'r') as f:
            content = f.read()
        
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)
            elif f"{var}=your_" in content:
                missing_vars.append(f"{var} (has placeholder value)")
        
        if missing_vars:
            print(f"❌ Missing or incomplete variables: {', '.join(missing_vars)}")
            return False
        
        print("✅ .env file has required variables")
        return True
        
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def check_docker_compose_config():
    """Check docker-compose.yml configuration"""
    print("\n=== Docker Compose Configuration ===")
    
    compose_path = Path("docker-compose.yml")
    if not compose_path.exists():
        print("❌ docker-compose.yml not found")
        return False
    
    try:
        with open(compose_path, 'r') as f:
            content = f.read()
        
        # Check for correct environment variables
        required_env_vars = ['GEMINI_API_KEY', 'GEMINI_BASE_URL']
        issues = []
        
        for var in required_env_vars:
            if var not in content:
                issues.append(f"Missing {var} in environment section")
        
        if "OPENAI_API_KEY" in content:
            issues.append("Found OPENAI_API_KEY (should be GEMINI_API_KEY)")
        
        if "env_file:" not in content:
            issues.append("Missing env_file: .env configuration")
        
        if issues:
            print("❌ Docker Compose issues found:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        
        print("✅ Docker Compose configuration looks good")
        return True
        
    except Exception as e:
        print(f"❌ Error reading docker-compose.yml: {e}")
        return False

def test_docker_build():
    """Test if Docker image builds successfully"""
    print("\n=== Docker Build Test ===")
    
    try:
        print("🔧 Building Docker image...")
        result = subprocess.run(
            ['docker', 'build', '-t', 'ai-tutor-test', '.'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ Docker image built successfully")
            return True
        else:
            print("❌ Docker build failed:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Docker build timed out")
        return False
    except Exception as e:
        print(f"❌ Docker build error: {e}")
        return False

def test_docker_env_vars():
    """Test environment variables inside Docker container"""
    print("\n=== Docker Environment Variables Test ===")
    
    try:
        print("🔧 Testing environment variables in container...")
        
        # Run a container to check environment variables
        cmd = [
            'docker', 'run', '--rm',
            '--env-file', '.env',
            '-e', 'GEMINI_API_KEY=${GEMINI_API_KEY}',
            '-e', 'GEMINI_BASE_URL=${GEMINI_BASE_URL}',
            'ai-tutor-test',
            'python', '-c',
            '''
import os
print("GEMINI_API_KEY:", "SET" if os.getenv("GEMINI_API_KEY") else "NOT SET")
print("GEMINI_BASE_URL:", "SET" if os.getenv("GEMINI_BASE_URL") else "NOT SET")
print("GEMINI_MODEL:", os.getenv("GEMINI_MODEL", "NOT SET"))
'''
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Container environment test results:")
            print(result.stdout)
            
            if "NOT SET" in result.stdout:
                print("❌ Some environment variables are not set in container")
                return False
            else:
                print("✅ All environment variables are set in container")
                return True
        else:
            print("❌ Container environment test failed:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Container test timed out")
        return False
    except Exception as e:
        print(f"❌ Container test error: {e}")
        return False

def generate_fixed_docker_compose():
    """Generate a corrected docker-compose.yml"""
    print("\n=== Generating Fixed Docker Compose ===")
    
    fixed_compose = """version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app/backend
      - ./schema.sql:/app/schema.sql
      - ./ai_tutor.db:/app/ai_tutor.db
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GEMINI_BASE_URL=${GEMINI_BASE_URL}
      - GEMINI_MODEL=${GEMINI_MODEL:-gemini-2.0-flash}
      - DATABASE_PATH=./ai_tutor.db
    env_file:
      - .env
    restart: unless-stopped
"""
    
    try:
        with open("docker-compose-fixed.yml", "w") as f:
            f.write(fixed_compose)
        
        print("✅ Created docker-compose-fixed.yml with correct configuration")
        print("💡 To use: docker-compose -f docker-compose-fixed.yml up --build")
        return True
        
    except Exception as e:
        print(f"❌ Error creating fixed docker-compose: {e}")
        return False

def main():
    """Run all Docker debugging tests"""
    print("🐳 AI Language Tutor v6 - Docker Debug Tool")
    print("This helps debug Docker environment variable issues")
    print("=" * 60)
    
    # Run all checks
    checks = [
        check_docker_setup(),
        check_env_file(),
        check_docker_compose_config()
    ]
    
    if all(checks):
        print("\n🔧 Basic checks passed. Testing Docker build...")
        
        build_ok = test_docker_build()
        if build_ok:
            env_ok = test_docker_env_vars()
            checks.append(env_ok)
    
    # Generate report
    print("\n" + "=" * 60)
    print("🔍 DOCKER DIAGNOSTIC REPORT")
    print("=" * 60)
    
    if all(checks):
        print("🎉 All Docker tests passed!")
        print("\nYour Docker setup should work correctly now.")
        print("Try running: docker-compose up --build")
    else:
        print("❌ Some Docker issues found.")
        print("\n🔧 Recommended fixes:")
        print("1. Make sure .env file exists with correct values")
        print("2. Update docker-compose.yml environment variables")
        print("3. Use the generated docker-compose-fixed.yml")
        
        generate_fixed_docker_compose()
    
    print("\n💡 Alternative: Since it works locally, you can just use:")
    print("   uvicorn backend.main:app --reload")
    print("   (No Docker needed for development)")

if __name__ == "__main__":
    main() 