from fastapi import APIRouter, Depends, HTTPException
from backend.schemas.curriculum import CurriculumCreate, CurriculumResponse
from backend.services.curriculum_service import create_curriculum, get_user_curriculums
from backend.utils.auth import get_current_user
from typing import List

router = APIRouter(prefix="/curriculum", tags=["curriculum"])

@router.post("/", response_model=CurriculumResponse)
async def create_curriculum_endpoint(
    payload: CurriculumCreate, 
    current_user: dict = Depends(get_current_user)
):
    """Create a new curriculum and trigger related content generation (authenticated)."""
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    # Pass user_id to the service so curriculum can be associated with the user
    return create_curriculum(payload, user_id=user_id)

@router.get("/", response_model=List[dict])
async def get_my_curriculums(current_user: dict = Depends(get_current_user)):
    """Get all curriculums for the authenticated user."""
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    return get_user_curriculums(user_id) 