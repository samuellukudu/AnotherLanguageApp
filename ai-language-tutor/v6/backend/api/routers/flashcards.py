from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging
from backend.api.models import GenerationRequest, ResponseModel
from backend.services.ai_service import ai_service
from backend.core.config import settings
from backend.api.routers.metadata import get_current_metadata

router = APIRouter(prefix="/generate", tags=["flashcards"])
logger = logging.getLogger(__name__)

@router.post("/flashcards", response_model=ResponseModel)
async def generate_flashcards(data: GenerationRequest):
    """
    Generates flashcards based on user input and language metadata.
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
            settings.flashcard_mode_instructions
            .replace("{native_language}", nl)
            .replace("{target_language}", tl)
            .replace("{proficiency}", prof)
        )
        
        # Generate flashcards
        response = await ai_service.get_completions(
            data.query,
            instructions
        )
        
        return ResponseModel(
            data=response,
            type="flashcards"
        )
    except Exception as e:
        logger.error(f"Error generating flashcards: {e}")
        raise HTTPException(status_code=500, detail=str(e))