import os
import socket
from fastapi import FastAPI, HTTPException
from .models import CurriculumRequest, LessonRequest, DailyLessonRequest
from backend.CurriculumManager.generate_curriculum import get_completion as generate_curriculum
from backend.LessonManager.generate_lesson import get_completion as generate_lesson
from backend.LessonManager.generate_daily_lesson import get_completion as generate_daily_lesson
from backend.config_manager import Config
from backend.utils import read_json_file, ensure_directory
from backend.db_manager.db_manager import DatabaseManager
import json

# Set up paths correctly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CONFIG_DIR = os.path.join(PROJECT_ROOT, "backend")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

# Ensure config directory exists
ensure_directory(CONFIG_DIR)

# Import and run config setup
from backend.config import (
    CURRICULUM_INSTRUCTION,
    MODEL,
    BASE_URL,
    API_KEY,
    API_PORT
)

app = FastAPI(title="AI Language Tutor API")
config = Config(CONFIG_PATH)

# Initialize config with default values if not exists
if not config.data:
    config.set("curriculum_instruction", CURRICULUM_INSTRUCTION)
    config.set("model", MODEL)
    config.set("base_url", BASE_URL)
    config.set("api_key", API_KEY)
    config.save()

@app.get("/")
def root():
    try:
        # Test database connection
        db = DatabaseManager()
        db.cur.execute("SELECT 1")
        return {"message": "Welcome to LinguaAI Backend! Database connection successful."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/curriculum")
async def create_curriculum(request: CurriculumRequest):
    try:
        return generate_curriculum(request.prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/lesson")
async def create_lesson(request: LessonRequest):
    try:
        # Create args with curriculum_id
        class Args:
            def __init__(self, curriculum_id, week):
                self.curriculum_id = curriculum_id
                self.week = week
        
        # Get the latest curriculum_id
        db = DatabaseManager()
        curriculums = db.list_curriculums()
        if not curriculums:
            raise HTTPException(status_code=404, detail="No curriculum found")
        
        curriculum_id = curriculums[0]['id']
        args = Args(curriculum_id=curriculum_id, week=request.week)
        
        from backend.main import setup_lesson_instruction
        result = setup_lesson_instruction(args)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to generate lesson")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/daily-lesson")
async def create_daily_lesson(request: DailyLessonRequest):
    try:
        class Args:
            def __init__(self, curriculum_id, week, day):
                self.curriculum_id = curriculum_id
                self.week = week
                self.day = day
        
        # Get the latest curriculum_id
        db = DatabaseManager()
        curriculums = db.list_curriculums()
        if not curriculums:
            raise HTTPException(status_code=404, detail="No curriculum found")
        
        curriculum_id = curriculums[0]['id']
        args = Args(curriculum_id=curriculum_id, week=request.week, day=request.day)
        
        from backend.main import setup_daily_lesson
        result = setup_daily_lesson(args)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to generate daily lesson")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/curriculums")
async def list_curriculums():
    """Get all curriculums"""
    try:
        db = DatabaseManager()
        return {"curriculums": db.list_curriculums()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/curriculums/{curriculum_id}")
async def get_curriculum(curriculum_id: int):
    """Get a specific curriculum with its data"""
    try:
        db = DatabaseManager()
        curriculum = db.get_curriculum(curriculum_id)
        if not curriculum:
            raise HTTPException(status_code=404, detail="Curriculum not found")
        return curriculum
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/curriculums/{curriculum_id}/lessons")
async def list_curriculum_lessons(curriculum_id: int):
    """Get all lessons for a curriculum"""
    try:
        db = DatabaseManager()
        lessons = db.list_curriculum_lessons(curriculum_id)
        return {"lessons": lessons}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lessons/{lesson_id}/daily")
async def get_daily_lessons(lesson_id: int):
    """Get all daily lessons for a lesson"""
    try:
        db = DatabaseManager()
        daily_lessons = db.get_daily_lessons(lesson_id)
        return {"daily_lessons": daily_lessons}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add Args class at module level
class Args:
    def __init__(self, week=0, day=0):
        self.week = week
        self.day = day
