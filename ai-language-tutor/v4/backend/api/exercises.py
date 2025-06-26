from fastapi import APIRouter, Depends, HTTPException
from backend.schemas.exercise import ExerciseResponse
from backend.services.exercise_service import get_exercises_for_curriculum
from backend.utils.auth import get_current_user, verify_curriculum_ownership
from typing import List

router = APIRouter(prefix="/exercises", tags=["exercises"])

@router.get("/{curriculum_id}", response_model=List[ExerciseResponse])
async def get_exercises(
    curriculum_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Retrieve exercises for a given curriculum (authenticated)."""
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    # Verify user owns this curriculum
    await verify_curriculum_ownership(curriculum_id, user_id)
    
    return get_exercises_for_curriculum(curriculum_id) 