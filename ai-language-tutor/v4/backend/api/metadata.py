from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.utils import generate_completions
from backend import config
from backend.cache import cache
from backend.utils.auth import get_current_user
import json

router = APIRouter(prefix="/metadata", tags=["metadata"])

class MetadataRequest(BaseModel):
    query: str

@router.post("/extract")
async def extract_metadata(
    data: MetadataRequest, 
    current_user: dict = Depends(get_current_user)
):
    """Extract language learning metadata from user query (authenticated)."""
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    try:
        response_str = await cache.get_or_set(
            (str(data.query), config.language_metadata_extraction_prompt),
            generate_completions.get_completions,
            data.query,
            config.language_metadata_extraction_prompt
        )
        metadata_dict = json.loads(response_str)
        return {
            "data": metadata_dict,
            "type": "language_metadata",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 