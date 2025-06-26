from backend.utils.supabase_client import supabase
from backend.schemas.flashcard import FlashcardResponse
from fastapi import HTTPException
from typing import List

def get_flashcards_for_curriculum(curriculum_id: int) -> List[FlashcardResponse]:
    result = supabase.table("flashcards").select("*").eq("curriculum_id", curriculum_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="No flashcards found for this curriculum.")
    return [FlashcardResponse(**flashcard) for flashcard in result.data] 