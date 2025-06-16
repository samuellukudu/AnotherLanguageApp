from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging
from backend.api.models import GenerationRequest, ResponseModel
from backend.services.ai_service import ai_service
from backend.core.config import settings
from backend.api.routers.metadata import get_current_metadata

router = APIRouter(prefix="/generate", tags=["exercises"])
logger = logging.getLogger(__name__)

@router.post("/exercises", response_model=ResponseModel)
async def generate_exercises(data: GenerationRequest):
    """
    Generates exercises based on user input and language metadata.
    """
    try:
        # Get current metadata
        metadata = get_current_metadata()
        
        # Use metadata from request or fallback to globals
        nl = data.native_language or metadata["native_language"]
        tl = data.target_language or metadata["target_language"]
        prof = data.proficiency or metadata["proficiency"]
        
        # Format instructions with metadata
        instructions = (
            settings.exercise_mode_instructions
            .replace("{native_language}", nl)
            .replace("{target_language}", tl)
            .replace("{proficiency}", prof)
        )
        
        # Generate exercises
        response = await ai_service.get_completions(
            data.query,
            instructions
        )
        
        return ResponseModel(
            data=response,
            type="exercises"
        )
    except Exception as e:
        logger.error(f"Error generating exercises: {e}")
        raise HTTPException(status_code=500, detail=str(e))