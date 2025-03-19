from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict

class CurriculumRequest(BaseModel):
    prompt: str

class LessonRequest(BaseModel):
    week: int = 0

class DailyLessonRequest(BaseModel):
    week: int = 0
    day: int = 0

class CurriculumList(BaseModel):
    id: int
    prompt: str
    language: Optional[str]
    learning_goal: Optional[str]
    current_level: Optional[str]
    created_at: datetime

class LessonList(BaseModel):
    id: int
    week_number: int
    content: Dict
    created_at: datetime

class DailyLessonList(BaseModel):
    id: int
    day_number: int
    content: Dict
    created_at: datetime
