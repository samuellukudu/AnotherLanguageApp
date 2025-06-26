from backend.utils.supabase_client import supabase
from backend.schemas.lesson import LessonResponse
from fastapi import HTTPException
from typing import List

def get_lessons_for_curriculum(curriculum_id: int) -> List[LessonResponse]:
    result = supabase.table("lessons").select("*").eq("curriculum_id", curriculum_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="No lessons found for this curriculum.")
    return [LessonResponse(id=lesson["id"], curriculum_id=lesson["curriculum_id"], title=lesson["title"], content=lesson["content"]) for lesson in result.data] 