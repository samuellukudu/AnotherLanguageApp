from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import json
from backend.utils import get_completion
from backend.config import CURRICULUM_INSTRUCTIONS
from backend.database import get_db_connection
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database connection
async def get_db():
    conn = await get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

# Request Models
class QueryRequest(BaseModel):
    user_query: str
    user_id: Optional[int] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password_hash: str
    native_language: str

# Response Models
class CurriculumResponse(BaseModel):
    curriculum_id: int
    target_language: str
    current_level: str
    learning_goal: str
    interests: List[str]
    duration_weeks: int
    intensity_per_week: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/users", response_model=dict)
async def create_user(user: UserCreate, db: psycopg2.extensions.connection = Depends(get_db)):
    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO users (username, email, password_hash, native_language)
                VALUES (%s, %s, %s, %s)
                RETURNING user_id, username, email, native_language
            """, (user.username, user.email, user.password_hash, user.native_language))
            db.commit()
            new_user = cur.fetchone()
        return new_user
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/curriculum", response_model=Dict)
async def create_curriculum(request: QueryRequest, db: psycopg2.extensions.connection = Depends(get_db)):
    try:
        # Get AI-generated curriculum
        curriculum_json = await get_completion(prompt=request.user_query, instruction=CURRICULUM_INSTRUCTIONS)
        curriculum_data = json.loads(curriculum_json)
        
        # If no user_id is provided, return the raw AI response
        if request.user_id is None:
            return curriculum_data
            
        # Extract curriculum settings
        settings = curriculum_data["curriculum_settings"]
        
        # If user_id is provided, verify user exists and store in database
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT user_id FROM users WHERE user_id = %s", (request.user_id,))
            if not cur.fetchone():
                db.rollback()
                raise HTTPException(status_code=404, detail=f"User with ID {request.user_id} not found")

        # Store curriculum in database
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            # Insert curriculum
            cur.execute("""
                INSERT INTO curriculums (
                    user_id, target_language, current_level, learning_goal,
                    interests, duration_weeks, intensity_per_week
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING curriculum_id
            """, (
                request.user_id,
                settings["target_language"],
                settings["current_level"],
                settings["learning_goal"],
                json.dumps(settings["interests"]),
                settings["duration_weeks"],
                settings["intensity_per_week"]
            ))
            
            curriculum_result = cur.fetchone()
            curriculum_id = curriculum_result["curriculum_id"]
            
            # Insert weekly modules
            for module in curriculum_data["weekly_modules"]:
                cur.execute("""
                    INSERT INTO weekly_modules (
                        curriculum_id, week_number, theme_title_native,
                        theme_title_target, theme_description_native,
                        estimated_duration_text, learning_objectives_native,
                        module_order
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING module_id
                """, (
                    curriculum_id,
                    module["week"],
                    module["theme"]["title_native"],
                    module["theme"]["title_target"],
                    module["theme"]["description_native"],
                    module["estimated_duration"],
                    json.dumps(module["learning_objectives_native"]),
                    module["week"]
                ))
                
                module_id = cur.fetchone()["module_id"]
                
                # Insert activities for each module
                for idx, activity in enumerate(module["activities"]):
                    cur.execute("""
                        INSERT INTO activities (
                            module_id, blueprint_activity_id, title_native,
                            title_target, activity_type, skill_focus,
                            estimated_time_minutes, description_native,
                            ai_helper_role, content_generation_prompt,
                            success_metric_native, activity_order
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        module_id,
                        activity["activity_id"],
                        activity["title_native"],
                        activity["title_target"],
                        activity["activity_type"],
                        json.dumps(activity["skill_focus"]),
                        activity["estimated_time_minutes"],
                        activity["description_native"],
                        activity["ai_helper_role"],
                        activity["content_generation_prompt"],
                        activity["success_metric_native"],
                        idx + 1
                    ))
            
            db.commit()
            
            # Return the created curriculum with its full data
            return curriculum_data
            
    except HTTPException as http_ex:
        # Re-raise HTTP exceptions to preserve their status codes
        raise http_ex
    except psycopg2.errors.ForeignKeyViolation:
        db.rollback()
        raise HTTPException(status_code=404, detail=f"User with ID {request.user_id} not found")
    except json.JSONDecodeError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid curriculum data format")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/curriculum/{curriculum_id}", response_model=Dict)
async def get_curriculum(curriculum_id: int, db: psycopg2.extensions.connection = Depends(get_db)):
    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            # Get curriculum data
            cur.execute("""
                SELECT c.*, 
                       json_agg(DISTINCT wm.*) as weekly_modules,
                       json_agg(DISTINCT a.*) as all_activities
                FROM curriculums c
                LEFT JOIN weekly_modules wm ON c.curriculum_id = wm.curriculum_id
                LEFT JOIN activities a ON wm.module_id = a.module_id
                WHERE c.curriculum_id = %s
                GROUP BY c.curriculum_id
            """, (curriculum_id,))
            
            result = cur.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Curriculum not found")
            
            # Organize activities by module
            modules = result['weekly_modules']
            activities = result['all_activities']
            
            # Remove these from the main result since we'll restructure them
            del result['weekly_modules']
            del result['all_activities']
            
            # Organize the data hierarchically
            for module in modules:
                module['activities'] = [
                    activity for activity in activities
                    if activity['module_id'] == module['module_id']
                ]
                module['activities'].sort(key=lambda x: x['activity_order'])
            
            modules.sort(key=lambda x: x['week_number'])
            result['weekly_modules'] = modules
            
            return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/curriculums", response_model=List[Dict])
async def get_user_curriculums(user_id: int, db: psycopg2.extensions.connection = Depends(get_db)):
    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT curriculum_id, target_language, current_level,
                       learning_goal, interests, duration_weeks,
                       intensity_per_week, is_active, created_at
                FROM curriculums
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))
            curriculums = cur.fetchall()
            return curriculums
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))