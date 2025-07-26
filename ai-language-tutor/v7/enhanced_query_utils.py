#!/usr/bin/env python3
"""
Enhanced Query Utilities for Language Learning Database
Provides indexed access to lessons, exercises, flashcards, and story segments
"""

import sqlite3
import json
import argparse
from datetime import datetime
from enhanced_database_system import (
    create_enhanced_database, generate_complete_lesson_content, 
    get_lesson_by_index, display_lesson_content, list_all_queries
)

def get_query_metadata(query_id):
    """Get metadata for a query session"""
    conn = sqlite3.connect('enhanced_language_learning.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM query_sessions WHERE query_id = ?', (query_id,))
    result = cursor.fetchone()
    
    if result:
        query_id, original_query, created_at, metadata_json, curriculum_json = result
        metadata = json.loads(metadata_json)
        curriculum = json.loads(curriculum_json)
        
        print(f"Query ID: {query_id}")
        print(f"Original Query: {original_query}")
        print(f"Created: {created_at}")
        print(f"\nMetadata:")
        print(f"  Native Language: {metadata['native_language']}")
        print(f"  Target Language: {metadata['target_language']}")
        print(f"  Proficiency: {metadata['proficiency']}")
        print(f"  Title: {metadata['title']}")
        print(f"  Description: {metadata['description']}")
        print(f"\nCurriculum:")
        print(f"  Topic: {curriculum['lesson_topic']}")
        print(f"  Number of Lessons: {len(curriculum['sub_topics'])}")
        
        return result
    else:
        print(f"Query {query_id} not found")
        return None
    
    conn.close()

def list_lessons(query_id):
    """List all lessons for a query"""
    conn = sqlite3.connect('enhanced_language_learning.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT lesson_index, sub_topic, description FROM lessons WHERE query_id = ? ORDER BY lesson_index', 
                   (query_id,))
    lessons = cursor.fetchall()
    
    if lessons:
        print(f"\nLessons for Query {query_id[:8]}...:\n")
        for lesson_index, sub_topic, description in lessons:
            print(f"  [{lesson_index}] {sub_topic}")
            print(f"      {description}")
    else:
        print(f"No lessons found for query {query_id}")
    
    conn.close()
    return lessons

def get_exercises_by_lesson(query_id, lesson_index):
    """Get exercises for a specific lesson"""
    conn = sqlite3.connect('enhanced_language_learning.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT exercise_index, sentence, answer, choices_json, explanation 
        FROM lesson_exercises 
        WHERE query_id = ? AND lesson_index = ? 
        ORDER BY exercise_index
    ''', (query_id, lesson_index))
    
    exercises = cursor.fetchall()
    
    if exercises:
        print(f"\nExercises for Lesson {lesson_index}:\n")
        for exercise_index, sentence, answer, choices_json, explanation in exercises:
            choices = json.loads(choices_json)
            print(f"  [{exercise_index}] {sentence}")
            print(f"      Answer: {answer}")
            print(f"      Choices: {', '.join(choices)}")
            print(f"      Explanation: {explanation}")
            print()
    else:
        print(f"No exercises found for lesson {lesson_index}")
    
    conn.close()
    return exercises

def get_flashcards_by_lesson(query_id, lesson_index):
    """Get flashcards for a specific lesson"""
    conn = sqlite3.connect('enhanced_language_learning.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT flashcard_index, word, definition, example 
        FROM lesson_flashcards 
        WHERE query_id = ? AND lesson_index = ? 
        ORDER BY flashcard_index
    ''', (query_id, lesson_index))
    
    flashcards = cursor.fetchall()
    
    if flashcards:
        print(f"\nFlashcards for Lesson {lesson_index}:\n")
        for flashcard_index, word, definition, example in flashcards:
            print(f"  [{flashcard_index}] {word}")
            print(f"      Definition: {definition}")
            print(f"      Example: {example}")
            print()
    else:
        print(f"No flashcards found for lesson {lesson_index}")
    
    conn.close()
    return flashcards

def get_story_by_lesson(query_id, lesson_index):
    """Get story for a specific lesson"""
    conn = sqlite3.connect('enhanced_language_learning.db')
    cursor = conn.cursor()
    
    # Get story info
    cursor.execute('''
        SELECT title, setting 
        FROM lesson_stories 
        WHERE query_id = ? AND lesson_index = ?
    ''', (query_id, lesson_index))
    
    story_info = cursor.fetchone()
    
    if not story_info:
        print(f"No story found for lesson {lesson_index}")
        return None
    
    title, setting = story_info
    
    # Get story segments
    cursor.execute('''
        SELECT segment_index, speaker, target_language_text, base_language_translation 
        FROM lesson_story_segments 
        WHERE query_id = ? AND lesson_index = ? 
        ORDER BY segment_index
    ''', (query_id, lesson_index))
    
    segments = cursor.fetchall()
    
    print(f"\nStory for Lesson {lesson_index}: {title}\n")
    print(f"Setting: {setting}\n")
    print("Segments:")
    for segment_index, speaker, target_text, translation in segments:
        print(f"  [{segment_index}] {speaker}: {target_text}")
        print(f"      Translation: {translation}")
        print()
    
    conn.close()
    return {'title': title, 'setting': setting, 'segments': segments}

def export_lesson_data(query_id, lesson_index, filename=None):
    """Export complete lesson data to JSON"""
    content = get_lesson_by_index(query_id, lesson_index)
    if not content:
        return
    
    # Format the data for export
    lesson_data = {
        'query_id': query_id,
        'lesson_index': lesson_index,
        'lesson_info': {
            'sub_topic': content['lesson'][2],
            'keywords': json.loads(content['lesson'][3]),
            'description': content['lesson'][4]
        },
        'exercises': [],
        'flashcards': [],
        'story': None
    }
    
    # Add exercises
    for exercise in content['exercises']:
        lesson_data['exercises'].append({
            'index': exercise[2],
            'sentence': exercise[3],
            'answer': exercise[4],
            'choices': json.loads(exercise[5]),
            'explanation': exercise[6]
        })
    
    # Add flashcards
    for flashcard in content['flashcards']:
        lesson_data['flashcards'].append({
            'index': flashcard[2],
            'word': flashcard[3],
            'definition': flashcard[4],
            'example': flashcard[5]
        })
    
    # Add story
    if content['story']:
        story = content['story']
        segments = []
        for segment in content['story_segments']:
            segments.append({
                'index': segment[2],
                'speaker': segment[3],
                'target_language_text': segment[4],
                'base_language_translation': segment[5]
            })
        
        lesson_data['story'] = {
            'title': story[2],
            'setting': story[3],
            'segments': segments
        }
    
    if not filename:
        filename = f"lesson_{lesson_index}_query_{query_id[:8]}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(lesson_data, f, indent=2, ensure_ascii=False)
    
    print(f"Lesson {lesson_index} exported to: {filename}")

def main():
    parser = argparse.ArgumentParser(description='Enhanced Language Learning Database Query Utilities')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate new content
    gen_parser = subparsers.add_parser('generate', help='Generate complete lesson content')
    gen_parser.add_argument('query', help='Learning query/context')
    
    # List queries
    list_parser = subparsers.add_parser('list-queries', help='List all query sessions')
    
    # Get query metadata
    meta_parser = subparsers.add_parser('metadata', help='Get query metadata')
    meta_parser.add_argument('query_id', help='Query ID')
    
    # List lessons
    lessons_parser = subparsers.add_parser('lessons', help='List lessons for a query')
    lessons_parser.add_argument('query_id', help='Query ID')
    
    # Get lesson content
    lesson_parser = subparsers.add_parser('lesson', help='Get complete lesson content')
    lesson_parser.add_argument('query_id', help='Query ID')
    lesson_parser.add_argument('lesson_index', type=int, help='Lesson index (0-4)')
    
    # Get exercises
    ex_parser = subparsers.add_parser('exercises', help='Get exercises for a lesson')
    ex_parser.add_argument('query_id', help='Query ID')
    ex_parser.add_argument('lesson_index', type=int, help='Lesson index (0-4)')
    
    # Get flashcards
    fc_parser = subparsers.add_parser('flashcards', help='Get flashcards for a lesson')
    fc_parser.add_argument('query_id', help='Query ID')
    fc_parser.add_argument('lesson_index', type=int, help='Lesson index (0-4)')
    
    # Get story
    story_parser = subparsers.add_parser('story', help='Get story for a lesson')
    story_parser.add_argument('query_id', help='Query ID')
    story_parser.add_argument('lesson_index', type=int, help='Lesson index (0-4)')
    
    # Export lesson
    export_parser = subparsers.add_parser('export', help='Export lesson to JSON')
    export_parser.add_argument('query_id', help='Query ID')
    export_parser.add_argument('lesson_index', type=int, help='Lesson index (0-4)')
    export_parser.add_argument('--filename', help='Output filename (optional)')
    
    # Initialize database
    init_parser = subparsers.add_parser('init', help='Initialize enhanced database')
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        query_id = generate_complete_lesson_content(args.query)
        print(f"\nGenerated content with Query ID: {query_id}")
    elif args.command == 'list-queries':
        list_all_queries()
    elif args.command == 'metadata':
        get_query_metadata(args.query_id)
    elif args.command == 'lessons':
        list_lessons(args.query_id)
    elif args.command == 'lesson':
        display_lesson_content(args.query_id, args.lesson_index)
    elif args.command == 'exercises':
        get_exercises_by_lesson(args.query_id, args.lesson_index)
    elif args.command == 'flashcards':
        get_flashcards_by_lesson(args.query_id, args.lesson_index)
    elif args.command == 'story':
        get_story_by_lesson(args.query_id, args.lesson_index)
    elif args.command == 'export':
        export_lesson_data(args.query_id, args.lesson_index, args.filename)
    elif args.command == 'init':
        create_enhanced_database()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()