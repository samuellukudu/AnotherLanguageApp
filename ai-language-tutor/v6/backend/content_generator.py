import json
import asyncio
from typing import Dict, Any, Optional, List
from backend.utils import generate_completions
from backend import config
from backend.db import db
import logging

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Service for generating and storing all learning content"""
    
    async def generate_curriculum_from_metadata(
        self,
        metadata_extraction_id: str,
        query: str,
        metadata: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> str:
        """Generate curriculum based on extracted metadata"""
        # Format curriculum instructions with metadata
        instructions = (
            config.curriculum_instructions
            .replace("{native_language}", metadata['native_language'])
            .replace("{target_language}", metadata['target_language'])
            .replace("{proficiency}", metadata['proficiency'])
        )
        
        # Generate curriculum
        logger.info(f"Generating curriculum for {metadata['target_language']} ({metadata['proficiency']})")
        curriculum_response = await generate_completions.get_completions(query, instructions)
        
        try:
            # Parse curriculum response
            curriculum = json.loads(curriculum_response)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse curriculum response: {curriculum_response[:200]}...")
            curriculum = {"lesson_topic": "Language Learning Journey", "sub_topics": []}
        
        # Save curriculum to database
        curriculum_id = await db.save_curriculum(
            metadata_extraction_id=metadata_extraction_id,
            curriculum=curriculum,
            user_id=user_id
        )
        
        return curriculum_id
    
    async def generate_content_for_lesson(
        self,
        curriculum_id: str,
        lesson_index: int,
        lesson: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate all content types for a single lesson"""
        content_ids = {}
        lesson_topic = lesson.get('sub_topic', f'Lesson {lesson_index + 1}')
        lesson_context = f"{lesson_topic}: {lesson.get('description', '')}"
        
        # Generate flashcards
        try:
            flashcards_instructions = (
                config.flashcard_mode_instructions
                .replace("{native_language}", metadata['native_language'])
                .replace("{target_language}", metadata['target_language'])
                .replace("{proficiency}", metadata['proficiency'])
            )
            
            flashcards_response = await generate_completions.get_completions(
                lesson_context,
                flashcards_instructions
            )
            
            # Save flashcards
            content_ids['flashcards'] = await db.save_learning_content(
                curriculum_id=curriculum_id,
                content_type='flashcards',
                lesson_index=lesson_index,
                lesson_topic=lesson_topic,
                content=flashcards_response
            )
        except Exception as e:
            logger.error(f"Failed to generate flashcards for lesson {lesson_index}: {e}")
        
        # Generate exercises
        try:
            exercises_instructions = (
                config.exercise_mode_instructions
                .replace("{native_language}", metadata['native_language'])
                .replace("{target_language}", metadata['target_language'])
                .replace("{proficiency}", metadata['proficiency'])
            )
            
            exercises_response = await generate_completions.get_completions(
                lesson_context,
                exercises_instructions
            )
            
            # Save exercises
            content_ids['exercises'] = await db.save_learning_content(
                curriculum_id=curriculum_id,
                content_type='exercises',
                lesson_index=lesson_index,
                lesson_topic=lesson_topic,
                content=exercises_response
            )
        except Exception as e:
            logger.error(f"Failed to generate exercises for lesson {lesson_index}: {e}")
        
        # Generate simulation
        try:
            simulation_instructions = (
                config.simulation_mode_instructions
                .replace("{native_language}", metadata['native_language'])
                .replace("{target_language}", metadata['target_language'])
                .replace("{proficiency}", metadata['proficiency'])
            )
            
            simulation_response = await generate_completions.get_completions(
                lesson_context,
                simulation_instructions
            )
            
            # Save simulation
            content_ids['simulation'] = await db.save_learning_content(
                curriculum_id=curriculum_id,
                content_type='simulation',
                lesson_index=lesson_index,
                lesson_topic=lesson_topic,
                content=simulation_response
            )
        except Exception as e:
            logger.error(f"Failed to generate simulation for lesson {lesson_index}: {e}")
        
        return content_ids
    
    async def generate_all_content_for_curriculum(
        self,
        curriculum_id: str,
        max_concurrent_lessons: int = 3
    ):
        """Generate all learning content for a curriculum"""
        # Get curriculum details
        curriculum_data = await db.get_curriculum(curriculum_id)
        if not curriculum_data:
            logger.error(f"Curriculum not found: {curriculum_id}")
            return
        
        # Parse curriculum JSON
        try:
            curriculum = json.loads(curriculum_data['curriculum_json'])
            lessons = curriculum.get('sub_topics', [])
        except json.JSONDecodeError:
            logger.error(f"Failed to parse curriculum JSON for {curriculum_id}")
            return
        
        # Prepare metadata
        metadata = {
            'native_language': curriculum_data['native_language'],
            'target_language': curriculum_data['target_language'],
            'proficiency': curriculum_data['proficiency']
        }
        
        logger.info(f"Starting content generation for {len(lessons)} lessons")
        
        # Process lessons in batches to avoid overwhelming the API
        for i in range(0, len(lessons), max_concurrent_lessons):
            batch = lessons[i:i + max_concurrent_lessons]
            batch_indices = list(range(i, min(i + max_concurrent_lessons, len(lessons))))
            
            # Generate content for batch concurrently
            tasks = [
                self.generate_content_for_lesson(
                    curriculum_id=curriculum_id,
                    lesson_index=idx,
                    lesson=lesson,
                    metadata=metadata
                )
                for idx, lesson in zip(batch_indices, batch)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for idx, result in zip(batch_indices, results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to generate content for lesson {idx}: {result}")
                else:
                    logger.info(f"Generated content for lesson {idx}: {result}")
        
        # Mark curriculum as content generated
        await db.mark_curriculum_content_generated(curriculum_id)
        logger.info(f"Completed content generation for curriculum {curriculum_id}")
    
    async def process_metadata_extraction(
        self,
        extraction_id: str,
        query: str,
        metadata: Dict[str, Any],
        user_id: Optional[int] = None,
        generate_content: bool = True
    ) -> Dict[str, Any]:
        """Process a metadata extraction by generating curriculum and optionally all content"""
        # Generate curriculum
        curriculum_id = await self.generate_curriculum_from_metadata(
            metadata_extraction_id=extraction_id,
            query=query,
            metadata=metadata,
            user_id=user_id
        )
        
        result = {
            'extraction_id': extraction_id,
            'curriculum_id': curriculum_id,
            'content_generation_started': False
        }
        
        if generate_content:
            # Start content generation in background
            asyncio.create_task(self.generate_all_content_for_curriculum(curriculum_id))
            result['content_generation_started'] = True
        
        return result


# Global content generator instance
content_generator = ContentGenerator() 