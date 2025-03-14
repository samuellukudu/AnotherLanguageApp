from pydantic import BaseModel

class CurriculumRequest(BaseModel):
    prompt: str

class LessonRequest(BaseModel):
    week: int = 0

class DailyLessonRequest(BaseModel):
    week: int = 0
    day: int = 0
