#!/usr/bin/env python3
"""
Test script for SQLite database functionality
Focus on testing the metadata extraction API
"""

import asyncio
import json
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import create_tables
from backend.content_service import content_service

async def test_metadata_functionality():
    """Test the metadata extraction and saving functionality"""
    print("🔧 Testing SQLite Database & Metadata Extraction")
    print("=" * 60)
    
    # Initialize database
    print("1. Initializing SQLite database tables...")
    try:
        await create_tables()
        print("   ✅ SQLite database tables created successfully")
    except Exception as e:
        print(f"   ❌ Error creating tables: {e}")
        return False
    
    # Test metadata saving
    print("\n2. Testing metadata saving...")
    test_query = "I want to learn Spanish for my upcoming trip to Mexico"
    test_metadata = {
        "native_language": "english",
        "target_language": "spanish",
        "proficiency": "beginner",
        "title": "Spanish for Travel",
        "description": "Learning Spanish basics for a trip to Mexico"
    }
    
    try:
        content_id = await content_service.save_metadata(
            query=test_query,
            metadata=test_metadata,
            user_id=123
        )
        print(f"   ✅ Metadata saved with content_id: {content_id[:16]}...")
    except Exception as e:
        print(f"   ❌ Error saving metadata: {e}")
        return False
    
    # Test metadata retrieval
    print("\n3. Testing metadata retrieval...")
    try:
        retrieved = await content_service.get_content_by_id(content_id)
        if retrieved:
            print("   ✅ Metadata retrieved successfully")
            print(f"   📝 Query: {retrieved['query'][:50]}...")
            print(f"   🏷️  Content type: {retrieved['content_type']}")
            
            # Parse the content to verify metadata
            parsed_content = json.loads(retrieved['content'])
            print(f"   🌐 Native language: {parsed_content['native_language']}")
            print(f"   🎯 Target language: {parsed_content['target_language']}")
            print(f"   📊 Proficiency: {parsed_content['proficiency']}")
        else:
            print("   ❌ Failed to retrieve metadata")
            return False
    except Exception as e:
        print(f"   ❌ Error retrieving metadata: {e}")
        return False
    
    # Test user metadata history
    print("\n4. Testing user metadata history...")
    try:
        history = await content_service.get_user_metadata_history(123)
        if history and len(history) > 0:
            print(f"   ✅ Found {len(history)} metadata entries for user 123")
            print(f"   📝 Latest query: {history[0]['query'][:50]}...")
            print(f"   🎯 Target language: {history[0]['target_language']}")
        else:
            print("   ❌ No metadata history found for user 123")
            return False
    except Exception as e:
        print(f"   ❌ Error retrieving user metadata history: {e}")
        return False
    
    # Test user content retrieval
    print("\n5. Testing user content retrieval...")
    try:
        user_content = await content_service.get_user_content(123, content_type="metadata")
        if user_content and len(user_content) > 0:
            print(f"   ✅ Found {len(user_content)} metadata items for user 123")
            print(f"   📝 Query: {user_content[0]['query'][:50]}...")
        else:
            print("   ❌ No content found for user 123")
            return False
    except Exception as e:
        print(f"   ❌ Error retrieving user content: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All SQLite database tests passed successfully!")
    print("\n📁 Database file location: ./ai_tutor.db")
    print("🚀 Your metadata extraction API is ready to use!")
    return True

async def test_content_saving():
    """Test saving different types of content"""
    print("\n" + "=" * 60)
    print("🔧 Testing Content Saving Functionality")
    print("=" * 60)
    
    # Test curriculum content saving
    print("1. Testing curriculum content saving...")
    curriculum_content = json.dumps({
        "lesson_topic": "Basic Spanish Greetings",
        "sub_topics": [
            {
                "sub_topic": "Hello and Goodbye",
                "keywords": ["greetings", "basics"],
                "description": "Learn basic Spanish greetings and farewells"
            }
        ]
    })
    
    try:
        curriculum_id = await content_service.save_content(
            query="teach me spanish greetings",
            content=curriculum_content,
            content_type="curriculum",
            user_id=123,
            native_language="english",
            target_language="spanish",
            proficiency="beginner"
        )
        print(f"   ✅ Curriculum saved with content_id: {curriculum_id[:16]}...")
    except Exception as e:
        print(f"   ❌ Error saving curriculum: {e}")
        return False
    
    # Test retrieval of curriculum
    print("\n2. Testing curriculum retrieval...")
    try:
        retrieved_curriculum = await content_service.get_content_by_id(curriculum_id)
        if retrieved_curriculum:
            print("   ✅ Curriculum retrieved successfully")
            parsed = json.loads(retrieved_curriculum['content'])
            print(f"   📚 Lesson topic: {parsed['lesson_topic']}")
        else:
            print("   ❌ Failed to retrieve curriculum")
            return False
    except Exception as e:
        print(f"   ❌ Error retrieving curriculum: {e}")
        return False
    
    print("\n🎉 Content saving tests passed!")
    return True

if __name__ == "__main__":
    print("AI Language Tutor - SQLite Database Test")
    print("Testing metadata extraction and content saving functionality")
    print()
    
    async def run_all_tests():
        success1 = await test_metadata_functionality()
        if not success1:
            return False
        
        success2 = await test_content_saving()
        return success1 and success2
    
    success = asyncio.run(run_all_tests())
    if not success:
        sys.exit(1)
    
    print("\n🎯 Next steps:")
    print("1. Start your API: uvicorn backend.main:app --reload")
    print("2. Test metadata extraction: POST /extract/metadata")
    print("3. Check saved content: GET /user/{user_id}/metadata")
    print("4. View SQLite database with any SQLite browser") 