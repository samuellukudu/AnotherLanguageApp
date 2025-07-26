import os
import sqlite3
import json
import uuid
from datetime import datetime
import dspy
from typing import Literal, List, Union
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Import all the classes from dspy_app.py
from dspy_app import (
    LanguageMetadata, ExtractMetadata, SubTopic, Curriculum, GenerateCurriculum,
    Exercise, GenerateExercises, Flashcard, GenerateFlashcards,
    StorySegment, Story, GenerateStory
)

load_dotenv()
lm = dspy.LM(f"openai/{os.getenv('MODEL')}", api_key=os.getenv("API_KEY"), api_base=os.getenv("BASE_URL"))
dspy.configure(lm=lm)

def create_enhanced_database():
    """Create enhanced SQLite database with lesson-level content storage"""
    conn = sqlite3.connect('enhanced_language_learning.db')
    cursor = conn.cursor()
    
    # Main query sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS query_sessions (
            query_id TEXT PRIMARY KEY,
            original_query TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata_json TEXT NOT NULL,
            curriculum_json TEXT NOT NULL
        )
    ''')
    
    # Individual lessons table with indexing
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            query_id TEXT NOT NULL,
            lesson_index INTEGER NOT NULL,
            sub_topic TEXT NOT NULL,
            keywords_json TEXT NOT NULL,
            description TEXT NOT NULL,
            lesson_json TEXT NOT NULL,
            FOREIGN KEY (query_id) REFERENCES query_sessions (query_id),
            PRIMARY KEY (query_id, lesson_index)
        )
    ''')
    
    # Exercises table with lesson linking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lesson_exercises (
            query_id TEXT NOT NULL,
            lesson_index INTEGER NOT NULL,
            exercise_index INTEGER NOT NULL,
            sentence TEXT NOT NULL,
            answer TEXT NOT NULL,
            choices_json TEXT NOT NULL,
            explanation TEXT NOT NULL,
            exercise_json TEXT NOT NULL,
            FOREIGN KEY (query_id) REFERENCES query_sessions (query_id),
            PRIMARY KEY (query_id, lesson_index, exercise_index)
        )
    ''')
    
    # Flashcards table with lesson linking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lesson_flashcards (
            query_id TEXT NOT NULL,
            lesson_index INTEGER NOT NULL,
            flashcard_index INTEGER NOT NULL,
            word TEXT NOT NULL,
            definition TEXT NOT NULL,
            example TEXT NOT NULL,
            flashcard_json TEXT NOT NULL,
            FOREIGN KEY (query_id) REFERENCES query_sessions (query_id),
            PRIMARY KEY (query_id, lesson_index, flashcard_index)
        )
    ''')
    
    # Story segments table with lesson linking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lesson_story_segments (
            query_id TEXT NOT NULL,
            lesson_index INTEGER NOT NULL,
            segment_index INTEGER NOT NULL,
            speaker TEXT NOT NULL,
            target_language_text TEXT NOT NULL,
            base_language_translation TEXT NOT NULL,
            segment_json TEXT NOT NULL,
            FOREIGN KEY (query_id) REFERENCES query_sessions (query_id),
            PRIMARY KEY (query_id, lesson_index, segment_index)
        )
    ''')
    
    # Complete stories table for each lesson
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lesson_stories (
            query_id TEXT NOT NULL,
            lesson_index INTEGER NOT NULL,
            title TEXT NOT NULL,
            setting TEXT NOT NULL,
            story_json TEXT NOT NULL,
            FOREIGN KEY (query_id) REFERENCES query_sessions (query_id),
            PRIMARY KEY (query_id, lesson_index)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Enhanced database created successfully!")

def generate_complete_lesson_content(query):
    """Generate complete content for all lessons in a curriculum"""
    query_id = str(uuid.uuid4())
    print(f"Starting complete lesson generation for query: '{query}'")
    print(f"Query ID: {query_id}")
    
    # Extract metadata
    print("\n=== EXTRACTING METADATA ===")
    metadata_module = dspy.Predict(ExtractMetadata)
    metadata_result = metadata_module(query=query)
    
    print(f"Native Language: {metadata_result.metadata.native_language}")
    print(f"Target Language: {metadata_result.metadata.target_language}")
    print(f"Proficiency: {metadata_result.metadata.proficiency}")
    
    # Generate curriculum
    print("\n=== GENERATING CURRICULUM ===")
    curriculum_module = dspy.Predict(GenerateCurriculum)
    curriculum = curriculum_module(
        query=query, 
        native_language=metadata_result.metadata.native_language, 
        target_language=metadata_result.metadata.target_language, 
        proficiency_level=metadata_result.metadata.proficiency
    )
    
    print(f"Lesson Topic: {curriculum.curriculum.lesson_topic}")
    print(f"Number of Sub-topics: {len(curriculum.curriculum.sub_topics)}")
    
    # Save main session data
    conn = sqlite3.connect('enhanced_language_learning.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO query_sessions 
        (query_id, original_query, metadata_json, curriculum_json)
        VALUES (?, ?, ?, ?)
    ''', (query_id, query, metadata_result.metadata.model_dump_json(), curriculum.curriculum.model_dump_json()))
    
    # Generate content for each lesson
    for lesson_index, sub_topic in enumerate(curriculum.curriculum.sub_topics):
        print(f"\n=== PROCESSING LESSON {lesson_index}: {sub_topic.sub_topic} ===")
        
        # Save lesson info
        cursor.execute('''
            INSERT INTO lessons 
            (query_id, lesson_index, sub_topic, keywords_json, description, lesson_json)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (query_id, lesson_index, sub_topic.sub_topic, 
              json.dumps(sub_topic.keywords), sub_topic.description, sub_topic.model_dump_json()))
        
        # Generate exercises for this lesson
        print(f"  Generating exercises...")
        exercise_module = dspy.Predict(GenerateExercises)
        exercises = exercise_module(
            lesson_content=sub_topic.sub_topic,
            native_language=metadata_result.metadata.native_language,
            target_language=metadata_result.metadata.target_language,
            proficiency_level=metadata_result.metadata.proficiency
        )
        
        # Save exercises
        for exercise_index, exercise in enumerate(exercises.exercises):
            cursor.execute('''
                INSERT INTO lesson_exercises 
                (query_id, lesson_index, exercise_index, sentence, answer, choices_json, explanation, exercise_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (query_id, lesson_index, exercise_index, exercise.sentence, exercise.answer,
                  json.dumps(exercise.choices), exercise.explanation, exercise.model_dump_json()))
        
        print(f"    Saved {len(exercises.exercises)} exercises")
        
        # Generate flashcards for this lesson
        print(f"  Generating flashcards...")
        flashcard_module = dspy.Predict(GenerateFlashcards)
        flashcards = flashcard_module(
            lesson_content=sub_topic.sub_topic,
            native_language=metadata_result.metadata.native_language,
            target_language=metadata_result.metadata.target_language,
            proficiency_level=metadata_result.metadata.proficiency
        )
        
        # Save flashcards
        for flashcard_index, flashcard in enumerate(flashcards.flashcards):
            cursor.execute('''
                INSERT INTO lesson_flashcards 
                (query_id, lesson_index, flashcard_index, word, definition, example, flashcard_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (query_id, lesson_index, flashcard_index, flashcard.word, 
                  flashcard.definition, flashcard.example, flashcard.model_dump_json()))
        
        print(f"    Saved {len(flashcards.flashcards)} flashcards")
        
        # Generate story for this lesson
        print(f"  Generating story...")
        story_module = dspy.Predict(GenerateStory)
        story = story_module(
            topic_or_domain=sub_topic.sub_topic,
            native_language=metadata_result.metadata.native_language,
            target_language=metadata_result.metadata.target_language,
            proficiency_level=metadata_result.metadata.proficiency
        )
        
        # Save complete story
        cursor.execute('''
            INSERT INTO lesson_stories 
            (query_id, lesson_index, title, setting, story_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (query_id, lesson_index, story.story.title, story.story.setting, story.story.model_dump_json()))
        
        # Save story segments
        for segment_index, segment in enumerate(story.story.content):
            cursor.execute('''
                INSERT INTO lesson_story_segments 
                (query_id, lesson_index, segment_index, speaker, target_language_text, base_language_translation, segment_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (query_id, lesson_index, segment_index, segment.speaker,
                  segment.target_language_text, segment.base_language_translation, segment.model_dump_json()))
        
        print(f"    Saved story with {len(story.story.content)} segments")
    
    conn.commit()
    conn.close()
    
    print(f"\n=== COMPLETE! ===")
    print(f"Generated content for {len(curriculum.curriculum.sub_topics)} lessons")
    print(f"Query ID: {query_id}")
    return query_id

def get_lesson_by_index(query_id, lesson_index):
    """Get lesson content by index"""
    conn = sqlite3.connect('enhanced_language_learning.db')
    cursor = conn.cursor()
    
    # Get lesson info
    cursor.execute('SELECT * FROM lessons WHERE query_id = ? AND lesson_index = ?', (query_id, lesson_index))
    lesson = cursor.fetchone()
    
    if not lesson:
        print(f"Lesson {lesson_index} not found for query {query_id}")
        return None
    
    # Get exercises
    cursor.execute('SELECT * FROM lesson_exercises WHERE query_id = ? AND lesson_index = ? ORDER BY exercise_index', 
                   (query_id, lesson_index))
    exercises = cursor.fetchall()
    
    # Get flashcards
    cursor.execute('SELECT * FROM lesson_flashcards WHERE query_id = ? AND lesson_index = ? ORDER BY flashcard_index', 
                   (query_id, lesson_index))
    flashcards = cursor.fetchall()
    
    # Get story
    cursor.execute('SELECT * FROM lesson_stories WHERE query_id = ? AND lesson_index = ?', (query_id, lesson_index))
    story = cursor.fetchone()
    
    # Get story segments
    cursor.execute('SELECT * FROM lesson_story_segments WHERE query_id = ? AND lesson_index = ? ORDER BY segment_index', 
                   (query_id, lesson_index))
    story_segments = cursor.fetchall()
    
    conn.close()
    
    return {
        'lesson': lesson,
        'exercises': exercises,
        'flashcards': flashcards,
        'story': story,
        'story_segments': story_segments
    }

def display_lesson_content(query_id, lesson_index):
    """Display formatted lesson content"""
    content = get_lesson_by_index(query_id, lesson_index)
    if not content:
        return
    
    lesson = content['lesson']
    print(f"\n=== LESSON {lesson_index}: {lesson[2]} ===")
    print(f"Keywords: {json.loads(lesson[3])}")
    print(f"Description: {lesson[4]}")
    
    print(f"\n--- EXERCISES ({len(content['exercises'])}) ---")
    for exercise in content['exercises']:
        print(f"  Exercise {exercise[2]}:")
        print(f"    Sentence: {exercise[3]}")
        print(f"    Answer: {exercise[4]}")
        print(f"    Choices: {json.loads(exercise[5])}")
        print(f"    Explanation: {exercise[6]}")
    
    print(f"\n--- FLASHCARDS ({len(content['flashcards'])}) ---")
    for flashcard in content['flashcards']:
        print(f"  Flashcard {flashcard[2]}:")
        print(f"    Word: {flashcard[3]}")
        print(f"    Definition: {flashcard[4]}")
        print(f"    Example: {flashcard[5]}")
    
    if content['story']:
        story = content['story']
        print(f"\n--- STORY: {story[2]} ---")
        print(f"Setting: {story[3]}")
        print(f"\nSegments ({len(content['story_segments'])}):")
        for segment in content['story_segments']:
            print(f"  {segment[2]}. {segment[3]}: {segment[4]}")
            print(f"     Translation: {segment[5]}")

def list_all_queries():
    """List all query sessions"""
    conn = sqlite3.connect('enhanced_language_learning.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT query_id, original_query, created_at FROM query_sessions ORDER BY created_at DESC')
    queries = cursor.fetchall()
    
    print(f"\nFound {len(queries)} query session(s):")
    for i, (query_id, original_query, created_at) in enumerate(queries):
        print(f"{i}. ID: {query_id[:8]}... | Query: '{original_query}' | Created: {created_at}")
    
    conn.close()
    return queries

if __name__ == "__main__":
    # Create enhanced database
    create_enhanced_database()
    
    # Generate complete content for example query
    query = "learning Spanish for a business trip to Madrid"
    query_id = generate_complete_lesson_content(query)
    
    # Display all lessons
    print("\n" + "="*80)
    print("DISPLAYING ALL GENERATED LESSONS")
    print("="*80)
    
    for lesson_index in range(5):  # We know there are 5 lessons
        display_lesson_content(query_id, lesson_index)
        print("\n" + "-"*60)
    
    # List all queries
    list_all_queries()