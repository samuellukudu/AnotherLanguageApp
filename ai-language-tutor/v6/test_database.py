#!/usr/bin/env python3
"""
Test script for database functionality
Run this to verify database caching is working properly
"""

import asyncio
import json
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import create_tables, generate_cache_key
from backend.db_cache import db_cache

async def test_database_functionality():
    """Test the database caching functionality"""
    print("🔧 Testing Database Functionality")
    print("=" * 50)
    
    # Initialize database
    print("1. Initializing database tables...")
    try:
        await create_tables()
        print("   ✅ Database tables created successfully")
    except Exception as e:
        print(f"   ❌ Error creating tables: {e}")
        return False
    
    # Test cache key generation
    print("\n2. Testing cache key generation...")
    test_query = "learn spanish basics"
    test_instructions = "Generate curriculum for Spanish learning"
    cache_key = generate_cache_key(test_query, test_instructions, "curriculum")
    print(f"   ✅ Generated cache key: {cache_key[:16]}...")
    
    # Mock async function for testing
    async def mock_generate_content(query, instructions):
        return json.dumps({
            "lesson_topic": "Basic Spanish Learning",
            "sub_topics": [
                {
                    "sub_topic": "Greetings and Introductions",
                    "keywords": ["conversation", "basics"],
                    "description": "Learn how to greet people and introduce yourself"
                }
            ]
        })
    
    # Test caching functionality
    print("\n3. Testing cache miss (first request)...")
    content1 = await db_cache.get_or_set(
        (test_query, test_instructions),
        mock_generate_content,
        content_type="curriculum",
        user_id=123,
        native_language="english",
        target_language="spanish",
        proficiency="beginner",
        query=test_query,
        instructions=test_instructions
    )
    print("   ✅ Content generated and cached")
    
    # Test cache hit
    print("\n4. Testing cache hit (second request)...")
    content2 = await db_cache.get_or_set(
        (test_query, test_instructions),
        mock_generate_content,
        content_type="curriculum",
        user_id=123,
        native_language="english",
        target_language="spanish",
        proficiency="beginner",
        query=test_query,
        instructions=test_instructions
    )
    
    if content1 == content2:
        print("   ✅ Cache hit successful - same content returned")
    else:
        print("   ❌ Cache miss - different content returned")
        return False
    
    # Test retrieval by cache key
    print("\n5. Testing retrieval by cache key...")
    retrieved = await db_cache.get_by_cache_key(cache_key)
    if retrieved:
        print(f"   ✅ Content retrieved successfully")
        print(f"   📊 Access count: {retrieved['access_count']}")
        print(f"   🏷️  Content type: {retrieved['content_type']}")
    else:
        print("   ❌ Failed to retrieve content by cache key")
        return False
    
    # Test user content retrieval
    print("\n6. Testing user content retrieval...")
    user_content = await db_cache.get_user_content(123, content_type="curriculum")
    if user_content and len(user_content) > 0:
        print(f"   ✅ Found {len(user_content)} items for user 123")
        print(f"   📝 Query: {user_content[0]['query']}")
    else:
        print("   ❌ No content found for user 123")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All database tests passed successfully!")
    print("\nYour database caching is ready to use!")
    return True

if __name__ == "__main__":
    print("AI Language Tutor - Database Test")
    print("Make sure your DATABASE_URL environment variable is set")
    print("Example: export DATABASE_URL='postgresql+asyncpg://ai_tutor:password123@localhost:5432/ai_tutor_db'")
    print()
    
    success = asyncio.run(test_database_functionality())
    if not success:
        sys.exit(1) 