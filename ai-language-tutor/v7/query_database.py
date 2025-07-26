import sqlite3
import json
from datetime import datetime

def query_all_sessions():
    """Query and display all learning sessions from the database"""
    conn = sqlite3.connect('language_learning_content.db')
    cursor = conn.cursor()
    
    # Get all sessions
    cursor.execute('SELECT * FROM learning_sessions ORDER BY created_at DESC')
    sessions = cursor.fetchall()
    
    print(f"Found {len(sessions)} learning session(s) in the database:\n")
    
    for session in sessions:
        session_id, query, created_at, metadata_json, curriculum_json, exercises_json, flashcards_json, story_json = session
        
        print(f"=== SESSION {session_id} ===")
        print(f"Query: {query}")
        print(f"Created: {created_at}")
        print()
        
        # Parse and display metadata
        metadata = json.loads(metadata_json)
        print("METADATA:")
        print(f"  Native Language: {metadata['native_language']}")
        print(f"  Target Language: {metadata['target_language']}")
        print(f"  Proficiency: {metadata['proficiency']}")
        print(f"  Title: {metadata['title']}")
        print(f"  Description: {metadata['description']}")
        print()
        
        # Parse and display curriculum
        curriculum = json.loads(curriculum_json)
        print("CURRICULUM:")
        print(f"  Lesson Topic: {curriculum['lesson_topic']}")
        print("  Sub-topics:")
        for i, sub_topic in enumerate(curriculum['sub_topics'], 1):
            print(f"    {i}. {sub_topic['sub_topic']}")
            print(f"       Keywords: {', '.join(sub_topic['keywords'])}")
            print(f"       Description: {sub_topic['description']}")
        print()
        
        # Parse and display exercises
        exercises = json.loads(exercises_json)
        print("EXERCISES:")
        for i, exercise in enumerate(exercises, 1):
            print(f"  Exercise {i}:")
            print(f"    Sentence: {exercise['sentence']}")
            print(f"    Answer: {exercise['answer']}")
            print(f"    Choices: {', '.join(exercise['choices'])}")
            print(f"    Explanation: {exercise['explanation']}")
        print()
        
        # Parse and display flashcards
        flashcards = json.loads(flashcards_json)
        print("FLASHCARDS:")
        for i, flashcard in enumerate(flashcards, 1):
            print(f"  Flashcard {i}:")
            print(f"    Word: {flashcard['word']}")
            print(f"    Definition: {flashcard['definition']}")
            print(f"    Example: {flashcard['example']}")
        print()
        
        # Parse and display story
        story = json.loads(story_json)
        print("STORY:")
        print(f"  Title: {story['title']}")
        print(f"  Setting: {story['setting']}")
        print("  Content:")
        for i, segment in enumerate(story['content'], 1):
            print(f"    {i}. {segment['speaker']}: {segment['target_language_text']}")
            print(f"       Translation: {segment['base_language_translation']}")
        print()
        print("=" * 80)
        print()
    
    conn.close()

def query_json_structure():
    """Display the JSON structure of stored data"""
    conn = sqlite3.connect('language_learning_content.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT metadata_json, curriculum_json, exercises_json, flashcards_json, story_json FROM learning_sessions LIMIT 1')
    result = cursor.fetchone()
    
    if result:
        metadata_json, curriculum_json, exercises_json, flashcards_json, story_json = result
        
        print("=== JSON STRUCTURE EXAMPLES ===")
        print("\nMETADATA JSON:")
        print(json.dumps(json.loads(metadata_json), indent=2))
        
        print("\nCURRICULUM JSON:")
        print(json.dumps(json.loads(curriculum_json), indent=2))
        
        print("\nEXERCISES JSON (first exercise):")
        exercises = json.loads(exercises_json)
        if exercises:
            print(json.dumps(exercises[0], indent=2))
        
        print("\nFLASHCARDS JSON (first flashcard):")
        flashcards = json.loads(flashcards_json)
        if flashcards:
            print(json.dumps(flashcards[0], indent=2))
        
        print("\nSTORY JSON (structure):")
        story = json.loads(story_json)
        # Show structure without all content
        story_structure = {
            "title": story["title"],
            "setting": story["setting"],
            "content_count": len(story["content"]),
            "first_segment": story["content"][0] if story["content"] else None
        }
        print(json.dumps(story_structure, indent=2))
    
    conn.close()

def show_database_schema():
    """Display the database schema"""
    conn = sqlite3.connect('language_learning_content.db')
    cursor = conn.cursor()
    
    print("=== DATABASE SCHEMA ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for column in columns:
            print(f"  {column[1]} ({column[2]})")
    
    conn.close()

if __name__ == "__main__":
    print("=== LANGUAGE LEARNING DATABASE QUERY ===")
    print()
    
    # Show database schema
    show_database_schema()
    print()
    
    # Show JSON structure examples
    query_json_structure()
    print()
    
    # Show all sessions
    query_all_sessions()