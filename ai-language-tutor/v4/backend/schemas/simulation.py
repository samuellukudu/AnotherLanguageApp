from pydantic import BaseModel
from typing import Any, Dict

class SimulationResponse(BaseModel):
    id: int
    curriculum_id: int
    scenario: str
    metadata: Dict[str, Any] = {} 