from backend.utils.supabase_client import supabase
from backend.schemas.exercise import ExerciseResponse
from fastapi import HTTPException
from typing import List

def get_exercises_for_curriculum(curriculum_id: int) -> List[ExerciseResponse]:
    result = supabase.table("exercises").select("*").eq("curriculum_id", curriculum_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="No exercises found for this curriculum.")
    return [ExerciseResponse(**exercise) for exercise in result.data] 