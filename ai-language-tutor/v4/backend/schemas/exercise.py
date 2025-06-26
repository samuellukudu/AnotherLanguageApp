from pydantic import BaseModel
from typing import Any, Dict

class ExerciseResponse(BaseModel):
    id: int
    curriculum_id: int
    question: str
    answer: str
    metadata: Dict[str, Any] = {} 