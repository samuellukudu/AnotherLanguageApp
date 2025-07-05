#!/usr/bin/env python3
"""
Test script for AI Language Tutor API v2.0
Demonstrates the workflow of metadata extraction, content generation, and retrieval
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

# API base URL - adjust if running on different host/port
BASE_URL = "http://localhost:8000"


async def test_metadata_extraction():
    """Test metadata extraction and automatic content generation"""
    print("\n1. Testing metadata extraction...")
    
    async with httpx.AsyncClient() as client:
        # Extract metadata
        response = await client.post(
            f"{BASE_URL}/extract/metadata",
            json={
                "query": "I want to learn Spanish for my upcoming trip to Barcelona",
                "user_id": 123
            }
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        return data


async def check_content_status(curriculum_id: str):
    """Check content generation status"""
    print(f"\n2. Checking content generation status for curriculum {curriculum_id}...")
    
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(f"{BASE_URL}/content/status/{curriculum_id}")
            status = response.json()
            
            print(f"Completion: {status['completion_percentage']}%")
            
            if status['is_complete']:
                print("Content generation complete!")
                break
            
            print("Waiting for content generation...")
            await asyncio.sleep(5)
        
        return status


async def get_curriculum(curriculum_id: str):
    """Get curriculum details"""
    print(f"\n3. Getting curriculum {curriculum_id}...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/curriculum/{curriculum_id}")
        curriculum = response.json()
        
        print(f"Lesson Topic: {curriculum['lesson_topic']}")
        print(f"Total Lessons: {len(curriculum['curriculum']['sub_topics'])}")
        print("\nFirst 3 lessons:")
        for i, lesson in enumerate(curriculum['curriculum']['sub_topics'][:3]):
            print(f"  {i+1}. {lesson['sub_topic']}")
            print(f"     Keywords: {', '.join(lesson['keywords'])}")
            print(f"     {lesson['description']}")
        
        return curriculum


async def get_lesson_content(curriculum_id: str, lesson_index: int = 0):
    """Get all content for a specific lesson"""
    print(f"\n4. Getting content for lesson {lesson_index}...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/curriculum/{curriculum_id}/lesson/{lesson_index}")
        lesson = response.json()
        
        print(f"Lesson Topic: {lesson.get('flashcards', {}).get('lesson_topic', 'N/A')}")
        
        # Show sample flashcards
        if lesson.get('flashcards'):
            print("\nSample Flashcards (first 2):")
            flashcards = json.loads(lesson['flashcards']['content']) if isinstance(lesson['flashcards']['content'], str) else lesson['flashcards']['content']
            for card in flashcards[:2]:
                print(f"  • {card['word']}")
                print(f"    Definition: {card['definition']}")
                print(f"    Example: {card['example']}")
        
        # Show sample exercise
        if lesson.get('exercises'):
            print("\nSample Exercise:")
            exercises = json.loads(lesson['exercises']['content']) if isinstance(lesson['exercises']['content'], str) else lesson['exercises']['content']
            if exercises:
                ex = exercises[0]
                print(f"  Sentence: {ex['sentence']}")
                print(f"  Choices: {', '.join(ex['choices'])}")
                print(f"  Answer: {ex['answer']}")
        
        return lesson


async def get_user_history(user_id: int):
    """Get user's learning history"""
    print(f"\n5. Getting history for user {user_id}...")
    
    async with httpx.AsyncClient() as client:
        # Get metadata extractions
        response = await client.get(f"{BASE_URL}/user/{user_id}/metadata")
        metadata_history = response.json()
        print(f"Total metadata extractions: {metadata_history['total']}")
        
        # Get curricula
        response = await client.get(f"{BASE_URL}/user/{user_id}/curricula")
        curricula = response.json()
        print(f"Total curricula: {curricula['total']}")
        
        return metadata_history, curricula


async def search_curricula():
    """Search for existing curricula"""
    print("\n6. Searching for Spanish beginner curricula...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/search/curricula",
            params={
                "native_language": "english",
                "target_language": "spanish",
                "proficiency": "beginner"
            }
        )
        
        results = response.json()
        print(f"Found {results['total']} curricula")
        
        for curr in results['curricula'][:3]:
            print(f"  • {curr['title']} (ID: {curr['id']})")
        
        return results


async def main():
    """Run all tests"""
    print("AI Language Tutor API v2.0 Test Script")
    print("=" * 50)
    
    try:
        # Test 1: Extract metadata (this starts content generation)
        extraction_result = await test_metadata_extraction()
        
        if 'curriculum_id' not in extraction_result:
            print("Error: No curriculum_id in response")
            return
        
        curriculum_id = extraction_result['curriculum_id']
        
        # Test 2: Check content generation status
        # Note: Content generation may take several minutes depending on API rate limits
        print("\nNote: Content generation may take several minutes...")
        # await check_content_status(curriculum_id)
        
        # For demo purposes, let's skip waiting and just show what we can get
        print("\nSkipping wait for demo purposes...")
        
        # Test 3: Get curriculum
        await get_curriculum(curriculum_id)
        
        # Test 4: Get lesson content (may be empty if still generating)
        await get_lesson_content(curriculum_id, 0)
        
        # Test 5: Get user history
        await get_user_history(123)
        
        # Test 6: Search curricula
        await search_curricula()
        
        print("\n" + "=" * 50)
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure the API is running on http://localhost:8000")


if __name__ == "__main__":
    asyncio.run(main()) 