from backend.utils.supabase_client import supabase
from backend.schemas.curriculum import CurriculumCreate, CurriculumResponse
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

def create_curriculum(payload: CurriculumCreate, user_id: str) -> CurriculumResponse:
    """
    Create a new curriculum associated with the authenticated user
    """
    try:
        data = {
            "title": payload.title,
            "metadata": payload.metadata,
            "user_id": user_id  # Associate curriculum with the authenticated user
        }
        
        logger.info(f"Creating curriculum for user {user_id}: {payload.title}")
        result = supabase.table("curriculums").insert(data).execute()
        
        if not result.data or len(result.data) == 0:
            logger.error(f"Failed to create curriculum: {result}")
            raise HTTPException(status_code=500, detail="Failed to create curriculum")
        
        inserted = result.data[0]
        logger.info(f"Curriculum created successfully: {inserted['id']}")
        
        return CurriculumResponse(
            id=inserted["id"], 
            title=inserted["title"], 
            metadata=inserted["metadata"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Curriculum creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create curriculum: {str(e)}")

def get_user_curriculums(user_id: str):
    """
    Get all curriculums for a specific user
    """
    try:
        result = supabase.table("curriculums").select("*").eq("user_id", user_id).execute()
        return result.data
    except Exception as e:
        logger.error(f"Error fetching user curriculums: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch curriculums") 