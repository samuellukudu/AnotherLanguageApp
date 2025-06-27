import asyncio
import logging
from typing import Dict, Any
from backend.storage import storage, ContentStatus
from backend.utils.handlers import generate_content_data, INSTRUCTION_TEMPLATES
from backend.models import GenerationRequest
import json

logger = logging.getLogger(__name__)

async def generate_content_background(curriculum_id: str, content_type: str, generation_request: GenerationRequest):
    """Background task to generate content (flashcards, exercises, simulation)"""
    try:
        # Update status to generating
        await storage.update_content_status(curriculum_id, content_type, ContentStatus.GENERATING)
        logger.info(f"Starting background generation of {content_type} for curriculum {curriculum_id}")
        
        # Generate the content
        result = await generate_content_data(
            data=generation_request,
            mode=content_type,
            instructions_template=INSTRUCTION_TEMPLATES[content_type]
        )
        
        logger.info(f"Generation result for {content_type}: {result}")  # Add detailed logging
        
        # Parse the generated content
        if result.get("status") == "success" and result.get("data"):
            try:
                content_data = json.loads(result["data"]) if isinstance(result["data"], str) else result["data"]
                
                # Store the generated content
                await storage.store_generated_content(curriculum_id, content_type, content_data)
                logger.info(f"Successfully generated and stored {content_type} for curriculum {curriculum_id}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error for {content_type} in curriculum {curriculum_id}: {str(e)}")
                logger.error(f"Raw data that failed to parse: {result.get('data')}")
                await storage.update_content_status(curriculum_id, content_type, ContentStatus.FAILED)
            except Exception as e:
                logger.error(f"Storage error for {content_type} in curriculum {curriculum_id}: {str(e)}")
                await storage.update_content_status(curriculum_id, content_type, ContentStatus.FAILED)
        else:
            logger.error(f"Failed to generate {content_type} for curriculum {curriculum_id}: {result}")
            await storage.update_content_status(curriculum_id, content_type, ContentStatus.FAILED)
            
    except Exception as e:
        logger.error(f"Error generating {content_type} for curriculum {curriculum_id}: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        await storage.update_content_status(curriculum_id, content_type, ContentStatus.FAILED)

async def start_background_generations(curriculum_id: str, generation_request: GenerationRequest):
    """Start all background generation tasks for a curriculum"""
    content_types = ["curriculum", "flashcards", "exercises", "simulation"]
    
    # Start all background generations
    tasks = []
    for content_type in content_types:
        task = asyncio.create_task(
            generate_content_background(curriculum_id, content_type, generation_request)
        )
        tasks.append(task)
    
    # Don't wait for completion - let them run in background
    logger.info(f"Started {len(tasks)} background generation tasks for curriculum {curriculum_id}")
    return tasks 