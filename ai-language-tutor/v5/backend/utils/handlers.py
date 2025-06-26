from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import Callable, Dict, Any
from backend import config
from backend.cache import cache
from backend.utils import generate_completions

async def generate_content_data(
    data: Any,
    mode: str,
    instructions_template: str
) -> Dict[str, Any]:
    """
    Generate content and return raw data (for internal use/background tasks).
    
    Args:
        data: The GenerationRequest object containing query and metadata
        mode: The type of generation (curriculum, flashcards, exercises, simulation)
        instructions_template: The template string from config to use
    
    Returns:
        Dictionary with the generated content
        
    Raises:
        HTTPException: If required metadata is missing or other errors occur
    """
    # Validate required metadata
    if not (data.native_language and data.target_language and data.proficiency):
        raise HTTPException(
            status_code=400,
            detail="native_language, target_language, and proficiency are required. Please extract metadata first."
        )

    # Format instructions with metadata
    instructions = (
        instructions_template
        .replace("{native_language}", data.native_language)
        .replace("{target_language}", data.target_language)
        .replace("{proficiency}", data.proficiency)
    )

    # Get response from cache or generate new
    response = await cache.get_or_set(
        (str(data.query), instructions),
        generate_completions.get_completions,
        data.query,
        instructions
    )

    return {
        "data": response,
        "type": mode,
        "status": "success"
    }

async def handle_generation_request(
    data: Any,
    mode: str,
    instructions_template: str
) -> JSONResponse:
    """
    Shared handler for all generation endpoints (curriculum, flashcards, exercises, simulation).
    
    Args:
        data: The GenerationRequest object containing query and metadata
        mode: The type of generation (curriculum, flashcards, exercises, simulation)
        instructions_template: The template string from config to use
    
    Returns:
        JSONResponse with the generated content
        
    Raises:
        HTTPException: If required metadata is missing or other errors occur
    """
    content = await generate_content_data(data, mode, instructions_template)
    return JSONResponse(content=content, status_code=200)

# Mapping of modes to their instruction templates
INSTRUCTION_TEMPLATES: Dict[str, str] = {
    "curriculum": config.curriculum_instructions,
    "flashcards": config.flashcard_mode_instructions,
    "exercises": config.exercise_mode_instructions,
    "simulation": config.simulation_mode_instructions
} 