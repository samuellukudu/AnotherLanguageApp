from pydantic import BaseModel
from typing import Any, Dict

class LessonResponse(BaseModel):
    id: int
    curriculum_id: int
    title: str
    content: Dict[str, Any] 