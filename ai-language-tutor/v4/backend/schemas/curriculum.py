from pydantic import BaseModel
from typing import Any, Dict

class CurriculumCreate(BaseModel):
    title: str
    metadata: Dict[str, Any]

class CurriculumResponse(BaseModel):
    id: int
    title: str
    metadata: Dict[str, Any] 