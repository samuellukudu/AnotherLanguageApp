import os
import socket
from fastapi import FastAPI, HTTPException
from .models import CurriculumRequest, LessonRequest, DailyLessonRequest
from backend.CurriculumManager.generate_curriculum import get_completion as generate_curriculum
from backend.LessonManager.generate_lesson import get_completion as generate_lesson
from backend.LessonManager.generate_daily_lesson import get_completion as generate_daily_lesson
from backend.config_manager import Config
from backend.utils import read_json_file, ensure_directory

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
    API_KEY
)

def find_available_port(start_port=8000, max_port=8020):
    """Find first available port in range"""
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('', port))
                return port
            except OSError:
                continue
    return None

# Get port from environment or find available one
PORT = int(os.getenv('API_PORT', 8000))
if PORT == 8000:  # If using default port, check availability
    available_port = find_available_port()
    if available_port:
        PORT = available_port

app = FastAPI(title="AI Language Tutor API")
config = Config(CONFIG_PATH)

# Initialize config with default values if not exists
if not config.data:
    config.set("curriculum_instruction", CURRICULUM_INSTRUCTION)
    config.set("model", MODEL)
    config.set("base_url", BASE_URL)
    config.set("api_key", API_KEY)
    config.save()

@app.post("/curriculum")
async def create_curriculum(request: CurriculumRequest):
    try:
        return generate_curriculum(request.prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/lesson")
async def create_lesson(request: LessonRequest):
    try:
        # Simulate args object for compatibility
        class Args:
            def __init__(self, week):
                self.week = week
        
        args = Args(request.week)
        from backend.main import setup_lesson_instruction
        
        setup_lesson_instruction(args)
        return generate_lesson(config.get("lesson_prompt"))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/daily-lesson")
async def create_daily_lesson(request: DailyLessonRequest):
    try:
        class Args:
            def __init__(self, week, day):
                self.week = week
                self.day = day
        
        args = Args(request.week, request.day)
        from backend.main import setup_daily_lesson
        
        return setup_daily_lesson(args)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Lesson plan not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Add Args class at module level
class Args:
    def __init__(self, week=0, day=0):
        self.week = week
        self.day = day
