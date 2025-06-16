from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import json
import logging
from typing import Dict, Any

from backend.api.models import MetadataRequest, ResponseModel
from backend.services.ai_service import ai_service
from backend.core.config import settings
from backend.core.exceptions import handle_exception, BaseAppException

router = APIRouter(prefix="/extract", tags=["metadata"])
logger = logging.getLogger(__name__)

# Global metadata variables
_metadata_store = {
    "native_language": None,
    "target_language": None,
    "proficiency": None
}

# Dependency for getting current metadata
def get_current_metadata():
    """Returns the current global metadata."""
    return {
        "native_language": _metadata_store["native_language"] or "unknown",
        "target_language": _metadata_store["target_language"] or "unknown",
        "proficiency": _metadata_store["proficiency"] or "unknown"
    }

@router.post("/metadata", response_model=ResponseModel)
async def extract_metadata(data: MetadataRequest):
    """Extracts language metadata from user input."""
    logger.info(f"Query: {data.query}")
    try:
        # Use the AI service to extract metadata
        metadata_dict = await ai_service.extract_metadata(data.query)
        
        # Update global metadata store
        _metadata_store["native_language"] = metadata_dict.get('native_language', 'unknown')
        _metadata_store["target_language"] = metadata_dict.get('target_language', 'unknown')
        _metadata_store["proficiency"] = metadata_dict.get('proficiency', 'unknown')
        
        return ResponseModel(
            data=metadata_dict,
            type="language_metadata"
        )
    except BaseAppException as e:
        # Handle application-specific exceptions
        raise e.to_http_exception()
    except Exception as e:
        # Handle unexpected exceptions
        logger.error(f"Error extracting metadata: {e}")
        raise handle_exception(e)