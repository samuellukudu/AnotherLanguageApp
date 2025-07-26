#!/usr/bin/env python3
"""
Database utilities for the Language Learning AI Tutor
This script provides easy-to-use functions for saving and retrieving language learning content as JSON.
"""

import sqlite3
import json
import uuid
import argparse
from datetime import datetime
from save_to_database import create_database, generate_and_save_content, retrieve_content

def add_new_session(query):
    """Add a new learning session to the database"""
    print(f"Generating content for query: '{query}'")
    session_id = generate_and_save_content(query)
    print(f"\nContent successfully saved with session ID: {session_id}")
    return session_id

def list_all_sessions():
    """List all sessions in the database"""
    conn = sqlite3.connect('language_learning_content.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, query, created_at FROM learning_sessions ORDER BY created_at DESC')
    sessions = cursor.fetchall()
    
    if not sessions:
        print("No sessions found in the database.")
        return
    
    print(f"Found {len(sessions)} session(s):\n")
    for i, (session_id, query, created_at) in enumerate(sessions, 1):
        print(f"{i}. ID: {session_id[:8]}... | Query: '{query}' | Created: {created_at}")
    
    conn.close()

def get_session_json(session_id, content_type='all'):
    """Get JSON content for a specific session"""
    conn = sqlite3.connect('language_learning_content.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM learning_sessions WHERE id = ?', (session_id,))
    result = cursor.fetchone()
    
    if not result:
        print(f"Session {session_id} not found.")
        return None
    
    session_id, query, created_at, metadata_json, curriculum_json, exercises_json, flashcards_json, story_json = result
    
    content_map = {
        'metadata': metadata_json,
        'curriculum': curriculum_json,
        'exercises': exercises_json,
        'flashcards': flashcards_json,
        'story': story_json
    }
    
    if content_type == 'all':
        return {
            'session_id': session_id,
            'query': query,
            'created_at': created_at,
            'metadata': json.loads(metadata_json),
            'curriculum': json.loads(curriculum_json),
            'exercises': json.loads(exercises_json),
            'flashcards': json.loads(flashcards_json),
            'story': json.loads(story_json)
        }
    elif content_type in content_map:
        return json.loads(content_map[content_type])
    else:
        print(f"Invalid content type: {content_type}. Valid types: metadata, curriculum, exercises, flashcards, story, all")
        return None
    
    conn.close()

def export_session_to_file(session_id, filename=None):
    """Export a session to a JSON file"""
    content = get_session_json(session_id)
    if not content:
        return
    
    if not filename:
        filename = f"session_{session_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    
    print(f"Session exported to: {filename}")

def search_sessions(keyword):
    """Search sessions by query keyword"""
    conn = sqlite3.connect('language_learning_content.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, query, created_at FROM learning_sessions WHERE query LIKE ? ORDER BY created_at DESC', 
                   (f'%{keyword}%',))
    sessions = cursor.fetchall()
    
    if not sessions:
        print(f"No sessions found containing keyword: '{keyword}'")
        return
    
    print(f"Found {len(sessions)} session(s) containing '{keyword}':\n")
    for i, (session_id, query, created_at) in enumerate(sessions, 1):
        print(f"{i}. ID: {session_id[:8]}... | Query: '{query}' | Created: {created_at}")
    
    conn.close()

def main():
    parser = argparse.ArgumentParser(description='Language Learning Database Utilities')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add new session
    add_parser = subparsers.add_parser('add', help='Add a new learning session')
    add_parser.add_argument('query', help='Learning query/context')
    
    # List sessions
    list_parser = subparsers.add_parser('list', help='List all sessions')
    
    # Get session content
    get_parser = subparsers.add_parser('get', help='Get session content')
    get_parser.add_argument('session_id', help='Session ID')
    get_parser.add_argument('--type', choices=['metadata', 'curriculum', 'exercises', 'flashcards', 'story', 'all'], 
                           default='all', help='Content type to retrieve')
    
    # Export session
    export_parser = subparsers.add_parser('export', help='Export session to JSON file')
    export_parser.add_argument('session_id', help='Session ID')
    export_parser.add_argument('--filename', help='Output filename (optional)')
    
    # Search sessions
    search_parser = subparsers.add_parser('search', help='Search sessions by keyword')
    search_parser.add_argument('keyword', help='Keyword to search for')
    
    # Initialize database
    init_parser = subparsers.add_parser('init', help='Initialize database')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        add_new_session(args.query)
    elif args.command == 'list':
        list_all_sessions()
    elif args.command == 'get':
        content = get_session_json(args.session_id, args.type)
        if content:
            print(json.dumps(content, indent=2, ensure_ascii=False))
    elif args.command == 'export':
        export_session_to_file(args.session_id, args.filename)
    elif args.command == 'search':
        search_sessions(args.keyword)
    elif args.command == 'init':
        create_database()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()