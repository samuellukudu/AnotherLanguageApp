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

def create_database():
    """Create SQLite database with tables for storing language learning content as JSON"""
    conn = sqlite3.connect('language_learning_content.db')
    cursor = conn.cursor()
    
    # Create table for storing all generated content
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_sessions (
            id TEXT PRIMARY KEY,
            query TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata_json TEXT NOT NULL,
            curriculum_json TEXT NOT NULL,
            exercises_json TEXT NOT NULL,
            flashcards_json TEXT NOT NULL,
            story_json TEXT NOT NULL
        )
    ''')
    
    # Create individual tables for each content type (optional, for easier querying)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            native_language TEXT,
            target_language TEXT,
            proficiency TEXT,
            title TEXT,
            description TEXT,
            json_data TEXT,
            FOREIGN KEY (session_id) REFERENCES learning_sessions (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS curricula (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            lesson_topic TEXT,
            json_data TEXT,
            FOREIGN KEY (session_id) REFERENCES learning_sessions (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            lesson_content TEXT,
            json_data TEXT,
            FOREIGN KEY (session_id) REFERENCES learning_sessions (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            lesson_content TEXT,
            json_data TEXT,
            FOREIGN KEY (session_id) REFERENCES learning_sessions (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stories (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            topic_or_domain TEXT,
            title TEXT,
            json_data TEXT,
            FOREIGN KEY (session_id) REFERENCES learning_sessions (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database created successfully!")

def generate_and_save_content(query):
    """Generate language learning content and save to database as JSON"""
    session_id = str(uuid.uuid4())
    
    # Extract metadata
    metadata_module = dspy.Predict(ExtractMetadata)
    metadata_result = metadata_module(query=query)
    
    # Generate curriculum
    curriculum_module = dspy.Predict(GenerateCurriculum)
    curriculum = curriculum_module(
        query=query, 
        native_language=metadata_result.metadata.native_language, 
        target_language=metadata_result.metadata.target_language, 
        proficiency_level=metadata_result.metadata.proficiency
    )
    
    # Use the 4th lesson (index 3) for exercises and flashcards
    lesson = curriculum.curriculum.sub_topics[3]
    
    # Generate exercises
    exercise_module = dspy.Predict(GenerateExercises)
    exercises = exercise_module(
        lesson_content=lesson.sub_topic,
        native_language=metadata_result.metadata.native_language,
        target_language=metadata_result.metadata.target_language,
        proficiency_level=metadata_result.metadata.proficiency
    )
    
    # Generate flashcards
    flashcard_module = dspy.Predict(GenerateFlashcards)
    flashcards = flashcard_module(
        lesson_content=lesson.sub_topic,
        native_language=metadata_result.metadata.native_language,
        target_language=metadata_result.metadata.target_language,
        proficiency_level=metadata_result.metadata.proficiency
    )
    
    # Generate story
    story_module = dspy.Predict(GenerateStory)
    story = story_module(
        topic_or_domain="greetings and introductions in Beijing",
        native_language=metadata_result.metadata.native_language,
        target_language=metadata_result.metadata.target_language,
        proficiency_level=metadata_result.metadata.proficiency
    )
    
    # Convert to JSON
    metadata_json = metadata_result.metadata.model_dump_json()
    curriculum_json = curriculum.curriculum.model_dump_json()
    exercises_json = json.dumps([ex.model_dump() for ex in exercises.exercises])
    flashcards_json = json.dumps([fc.model_dump() for fc in flashcards.flashcards])
    story_json = story.story.model_dump_json()
    
    # Save to database
    conn = sqlite3.connect('language_learning_content.db')
    cursor = conn.cursor()
    
    # Insert into main sessions table
    cursor.execute('''
        INSERT INTO learning_sessions 
        (id, query, metadata_json, curriculum_json, exercises_json, flashcards_json, story_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (session_id, query, metadata_json, curriculum_json, exercises_json, flashcards_json, story_json))
    
    # Insert into individual tables
    cursor.execute('''
        INSERT INTO metadata 
        (id, session_id, native_language, target_language, proficiency, title, description, json_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), session_id, metadata_result.metadata.native_language,
          metadata_result.metadata.target_language, metadata_result.metadata.proficiency,
          metadata_result.metadata.title, metadata_result.metadata.description, metadata_json))
    
    cursor.execute('''
        INSERT INTO curricula 
        (id, session_id, lesson_topic, json_data)
        VALUES (?, ?, ?, ?)
    ''', (str(uuid.uuid4()), session_id, curriculum.curriculum.lesson_topic, curriculum_json))
    
    cursor.execute('''
        INSERT INTO exercises 
        (id, session_id, lesson_content, json_data)
        VALUES (?, ?, ?, ?)
    ''', (str(uuid.uuid4()), session_id, lesson.sub_topic, exercises_json))
    
    cursor.execute('''
        INSERT INTO flashcards 
        (id, session_id, lesson_content, json_data)
        VALUES (?, ?, ?, ?)
    ''', (str(uuid.uuid4()), session_id, lesson.sub_topic, flashcards_json))
    
    cursor.execute('''
        INSERT INTO stories 
        (id, session_id, topic_or_domain, title, json_data)
        VALUES (?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), session_id, "greetings and introductions in Beijing", 
          story.story.title, story_json))
    
    conn.commit()
    conn.close()
    
    print(f"Content saved to database with session ID: {session_id}")
    return session_id

def retrieve_content(session_id=None):
    """Retrieve content from database"""
    conn = sqlite3.connect('language_learning_content.db')
    cursor = conn.cursor()
    
    if session_id:
        cursor.execute('SELECT * FROM learning_sessions WHERE id = ?', (session_id,))
        result = cursor.fetchone()
        if result:
            print(f"Session ID: {result[0]}")
            print(f"Query: {result[1]}")
            print(f"Created: {result[2]}")
            print(f"Metadata: {json.loads(result[3])}")
            print(f"Curriculum: {json.loads(result[4])}")
            print(f"Exercises: {json.loads(result[5])}")
            print(f"Flashcards: {json.loads(result[6])}")
            print(f"Story: {json.loads(result[7])}")
    else:
        cursor.execute('SELECT id, query, created_at FROM learning_sessions ORDER BY created_at DESC')
        results = cursor.fetchall()
        print("All sessions:")
        for result in results:
            print(f"ID: {result[0]}, Query: {result[1]}, Created: {result[2]}")
    
    conn.close()

if __name__ == "__main__":
    # Create database
    create_database()
    
    # Generate and save content for the example query
    query = "looking for a job as a structural engineer in Berlin"
    session_id = generate_and_save_content(query)
    
    # Retrieve and display the saved content
    print("\n=== RETRIEVED CONTENT ===")
    retrieve_content(session_id)