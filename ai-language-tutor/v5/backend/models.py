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

# New models for metadata-based curriculum generation
class LanguageMetadata(BaseModel):
    native_language: str
    target_language: str
    proficiency: str
    title: str
    description: str

class MetadataBasedRequest(BaseModel):
    user_id: int
    data: LanguageMetadata 