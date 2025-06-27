from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from backend.models import MetadataRequest, GenerationRequest
from backend.utils import generate_completions
from backend import config
from backend.storage import storage
from backend.background_tasks import start_background_generations
import logging
import json
import uuid
from backend.cache import cache

router = APIRouter()

@router.post("/metadata")
async def extract_metadata(data: MetadataRequest, background_tasks: BackgroundTasks, user_id: int = 1):
    logging.info(f"Query: {data.query}")
    try:
        # Extract metadata
        response_str = await cache.get_or_set(
            (str(data.query), config.language_metadata_extraction_prompt),
            generate_completions.get_completions,
            data.query,
            config.language_metadata_extraction_prompt
        )
        metadata_dict = json.loads(response_str)
        
        # Try to create curriculum record for background generation (optional)
        curriculum_id = str(uuid.uuid4())  # Generate ID upfront for response
        
        try:
            # Attempt curriculum creation (don't fail the endpoint if this fails)
            actual_curriculum_id = await storage.create_curriculum_record(
                user_id=user_id,
                metadata=metadata_dict
            )
            curriculum_id = actual_curriculum_id  # Use actual ID if creation succeeded
            
            # Create generation request for background tasks
            generation_request = GenerationRequest(
                user_id=user_id,
                query=f"{metadata_dict['title']}: {metadata_dict['description']}",
                native_language=metadata_dict['native_language'],
                target_language=metadata_dict['target_language'],
                proficiency=metadata_dict['proficiency']
            )
            
            # Start all background generation tasks
            background_tasks.add_task(start_background_generations, curriculum_id, generation_request)
            
        except Exception as e:
            # Log the error but don't fail the endpoint
            logging.error(f"Curriculum creation failed (non-fatal): {e}")
            # Continue with just metadata extraction - the main purpose of this endpoint
        
        return JSONResponse(
            content={
                "data": metadata_dict,
                "curriculum_id": curriculum_id,
                "type": "language_metadata",
                "status": "success",
                "message": "Metadata extracted. Curriculum, flashcards, exercises, and simulation are being generated in the background."
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 