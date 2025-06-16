from pydantic import BaseModel
from typing import Union, List, Literal, Optional

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class GenerationRequest(BaseModel):
    user_id: int
    query: Union[str, List[Message]]
    native_language: Optional[str] = None
    target_language: Optional[str] = None
    proficiency: Optional[str] = None

class MetadataRequest(BaseModel):
    query: str

class ResponseModel(BaseModel):
    data: Union[str, dict]
    type: str
    status: str = "success"