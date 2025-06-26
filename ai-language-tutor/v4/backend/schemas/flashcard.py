from pydantic import BaseModel
from typing import Any, Dict

class FlashcardResponse(BaseModel):
    id: int
    curriculum_id: int
    front: str
    back: str
    metadata: Dict[str, Any] = {} 