import asyncio
import json
import os
from backend.database import database
from backend.storage import storage
import logging

logging.basicConfig(level=logging.INFO)

class DatabaseUtils:
    """Utility functions for database management and migration"""
    
    @staticmethod
    async def migrate_file_to_database():
        """Migrate existing file data to database"""
        logging.info("Starting migration from file storage to database")
        
        # Initialize database
        await database.initialize_database()
        
        # Get all JSON files from curricula directory
        curricula_dir = "data/curricula"
        if not os.path.exists(curricula_dir):
            logging.info("No curricula directory found, nothing to migrate")
            return
        
        migrated_count = 0
        error_count = 0
        
        for filename in os.listdir(curricula_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(curricula_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        curriculum_data = json.load(f)
                    
                    curriculum_id = curriculum_data.get('id')
                    user_id = curriculum_data.get('user_id')
                    metadata = curriculum_data.get('metadata', {})
                    
                    if curriculum_id and user_id and metadata:
                        # Check if already exists in database
                        existing = await database.get_curriculum(curriculum_id)
                        if existing:
                            logging.info(f"Curriculum {curriculum_id} already exists in database, skipping")
                            continue
                        
                        # Create curriculum record with the same ID
                        curriculum_content = curriculum_data.get('content', {}).get('curriculum')
                        await database.store_curriculum(user_id, metadata, curriculum_content)
                        
                        # Get the lessons that were created
                        lessons = await database.get_lessons(curriculum_id)
                        
                        if lessons:
                            # Store additional content for each lesson
                            content = curriculum_data.get('content', {})
                            
                            # For migration, we'll associate all content with the first lesson
                            # In a real scenario, you'd want to distribute content across appropriate lessons
                            first_lesson_id = lessons[0]['id']
                            
                            if content.get('flashcards'):
                                await database.store_flashcards(first_lesson_id, content['flashcards'])
                                logging.info(f"Migrated {len(content['flashcards'])} flashcards")
                            
                            if content.get('exercises'):
                                await database.store_exercises(first_lesson_id, content['exercises'])
                                logging.info(f"Migrated {len(content['exercises'])} exercises")
                            
                            if content.get('simulation'):
                                await database.store_simulation(first_lesson_id, content['simulation'])
                                logging.info(f"Migrated simulation")
                        
                        # Update curriculum status
                        status = curriculum_data.get('status', {})
                        if status.get('curriculum'):
                            await database.update_curriculum_status(curriculum_id, status['curriculum'])
                        
                        migrated_count += 1
                        logging.info(f"Migrated curriculum {curriculum_id}")
                    else:
                        logging.warning(f"Invalid curriculum data in {filename}")
                        error_count += 1
                        
                except Exception as e:
                    logging.error(f"Error migrating {filename}: {e}")
                    error_count += 1
        
        logging.info(f"Migration completed: {migrated_count} curricula migrated, {error_count} errors")

async def main():
    """CLI interface for database utilities"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m backend.db_utils <command>")
        print("Commands:")
        print("  migrate    - Migrate file data to database")
        return
    
    command = sys.argv[1]
    utils = DatabaseUtils()
    
    if command == "migrate":
        await utils.migrate_file_to_database()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    asyncio.run(main()) 