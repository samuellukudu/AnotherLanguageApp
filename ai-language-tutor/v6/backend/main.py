from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.utils import generate_completions
from backend import config
from backend.db import db
from backend.db_init import db_initializer
from backend.content_generator import content_generator
from backend.db_cache import api_cache
from typing import Union, List, Literal, Optional
from datetime import datetime
import logging
import json

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AI Language Tutor API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MetadataRequest(BaseModel):
    query: str
    user_id: Optional[int] = None

class GenerationRequest(BaseModel):
    user_id: int
    query: Union[str, List[dict]]
    native_language: Optional[str] = None
    target_language: Optional[str] = None
    proficiency: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup with comprehensive checks"""
    logging.info("Starting database initialization...")
    
    # Initialize database with health checks
    init_result = await db_initializer.initialize_database()
    
    if init_result["success"]:
        logging.info(f"Database initialization successful: {init_result['action_taken']}")
        
        # Log database statistics
        health = init_result["health_check"]
        if health.get("record_count"):
            logging.info(f"Database records: {health['record_count']}")
    else:
        logging.error(f"Database initialization failed: {init_result['errors']}")
        # Try to repair
        logging.info("Attempting database repair...")
        repair_result = await db_initializer.repair_database()
        if repair_result["success"]:
            logging.info("Database repair successful")
        else:
            logging.error(f"Database repair failed: {repair_result['errors']}")
            raise RuntimeError("Failed to initialize database")

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Language Tutor API v2.0!"}

@app.get("/health")
async def health_check():
    """Comprehensive health check including database status"""
    try:
        # Check database health
        db_health = await db_initializer.check_database_health()
        
        # Overall health status
        is_healthy = (
            db_health["database_exists"] and
            db_health["schema_loaded"] and
            db_health["can_write"]
        )
        
        return JSONResponse(
            content={
                "status": "healthy" if is_healthy else "unhealthy",
                "api_version": "2.0.0",
                "database": db_health,
                "timestamp": datetime.now().isoformat()
            },
            status_code=200 if is_healthy else 503
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            },
            status_code=500
        )

@app.post("/admin/database/repair")
async def repair_database():
    """Repair database issues (admin endpoint)"""
    try:
        # repair_result = await db.repair_database() # This method doesn't exist on the Database class
        
        return JSONResponse(
            content={
                "success": repair_result["success"],
                "repairs_attempted": repair_result["repairs_attempted"],
                "errors": repair_result["errors"],
                "timestamp": datetime.now().isoformat()
            },
            status_code=200 if repair_result["success"] else 500
        )
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            },
            status_code=500
        )

@app.post("/admin/database/recreate")
async def recreate_database():
    """Recreate database from scratch (admin endpoint)"""
    try:
        init_result = await db_initializer.initialize_database(force_recreate=True)
        
        return JSONResponse(
            content={
                "success": init_result["success"],
                "action_taken": init_result["action_taken"],
                "health_check": init_result["health_check"],
                "errors": init_result["errors"],
                "timestamp": datetime.now().isoformat()
            },
            status_code=200 if init_result["success"] else 500
        )
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            },
            status_code=500
        )

# ========== POST ENDPOINTS (Generation) ==========

@app.post("/extract/metadata")
async def extract_metadata(data: MetadataRequest):
    """Extract language learning metadata from user query"""
    logging.info(f"Extracting metadata for query: {data.query[:50]}...")
    try:
        # Generate metadata using AI, with caching
        metadata_dict = await api_cache.get_or_set(
            category="metadata",
            key_text=data.query,
            coro=generate_completions.get_completions,
            prompt=data.query,
            instructions=config.language_metadata_extraction_prompt
        )

        # Save metadata to database
        extraction_id = await db.save_metadata_extraction(
            query=data.query,
            metadata=metadata_dict,
            user_id=data.user_id
        )

        # Process extraction (generate curriculum and start content generation)
        processing_result = await content_generator.process_metadata_extraction(
            extraction_id=extraction_id,
            query=data.query,
            metadata=metadata_dict,
            user_id=data.user_id,
            generate_content=True  # Automatically generate all content
        )

        curriculum_id = processing_result['curriculum_id']

        return JSONResponse(
            content={
                "message": "Content generation has been initiated.",
                "curriculum_id": curriculum_id,
                "status_endpoint": f"/content/status/{curriculum_id}"
            },
            status_code=202
        )
    except Exception as e:
        logging.error(f"Error extracting metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========== GET ENDPOINTS (Retrieval) ==========

@app.get("/curriculum/{curriculum_id}/metadata")
async def get_curriculum_metadata(curriculum_id: str = Path(..., description="Curriculum ID")):
    """Get metadata for a curriculum"""
    curriculum = await db.get_curriculum(curriculum_id)
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    
    # Get the full metadata extraction record
    extraction = await db.get_metadata_extraction(curriculum['metadata_extraction_id'])
    if not extraction:
        raise HTTPException(status_code=404, detail="Metadata extraction not found")
    
    # Parse JSON fields
    extraction['metadata'] = json.loads(extraction['metadata_json'])
    del extraction['metadata_json']
    
    return JSONResponse(content=extraction, status_code=200)

@app.get("/curriculum/{curriculum_id}")
async def get_curriculum(curriculum_id: str = Path(..., description="Curriculum ID")):
    """Get curriculum by ID"""
    curriculum = await db.get_full_curriculum_details(curriculum_id, include_content=False)
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    
    # Get content generation status
    status = await db.get_curriculum_content_status(curriculum_id)
    if status:
        curriculum['content_status'] = status
    
    return JSONResponse(content=curriculum, status_code=200)


async def _get_lesson_content_by_type(
    curriculum_id: str,
    lesson_index: int,
    content_type: str
):
    """Helper to get specific content type for a lesson"""
    content_list = await db.get_learning_content(
        curriculum_id=curriculum_id,
        lesson_index=lesson_index,
        content_type=content_type
    )
    if not content_list:
        raise HTTPException(
            status_code=404,
            detail=f"{content_type.capitalize()} content not found for lesson {lesson_index}"
        )

    # Assuming one content item per type per lesson
    content = content_list[0]
    try:
        parsed_content = json.loads(content['content_json'])
    except json.JSONDecodeError:
        parsed_content = content['content_json']

    return JSONResponse(
        content={
            "curriculum_id": curriculum_id,
            "lesson_index": lesson_index,
            "content_type": content_type,
            "id": content['id'],
            "lesson_topic": content['lesson_topic'],
            "content": parsed_content,
            "created_at": content['created_at']
        },
        status_code=200
    )

@app.get("/curriculum/{curriculum_id}/lesson/{lesson_index}/flashcards")
async def get_lesson_flashcards(
    curriculum_id: str = Path(..., description="Curriculum ID"),
    lesson_index: int = Path(..., ge=0, le=24, description="Lesson index (0-24)")
):
    """Get flashcards for a specific lesson"""
    return await _get_lesson_content_by_type(curriculum_id, lesson_index, "flashcards")

@app.get("/curriculum/{curriculum_id}/lesson/{lesson_index}/exercises")
async def get_lesson_exercises(
    curriculum_id: str = Path(..., description="Curriculum ID"),
    lesson_index: int = Path(..., ge=0, le=24, description="Lesson index (0-24)")
):
    """Get exercises for a specific lesson"""
    return await _get_lesson_content_by_type(curriculum_id, lesson_index, "exercises")

@app.get("/curriculum/{curriculum_id}/lesson/{lesson_index}/simulation")
async def get_lesson_simulation(
    curriculum_id: str = Path(..., description="Curriculum ID"),
    lesson_index: int = Path(..., ge=0, le=24, description="Lesson index (0-24)")
):
    """Get simulation for a specific lesson"""
    return await _get_lesson_content_by_type(curriculum_id, lesson_index, "simulation")
@app.get("/user/{user_id}/metadata")
async def get_user_metadata_history(
    user_id: int = Path(..., description="User ID"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results")
):
    """Get user's metadata extraction history"""
    extractions = await db.get_user_metadata_extractions(user_id, limit)
    
    # Parse JSON fields
    for extraction in extractions:
        extraction['metadata'] = json.loads(extraction['metadata_json'])
        del extraction['metadata_json']
    
    return JSONResponse(
        content={
            "user_id": user_id,
            "extractions": extractions,
            "total": len(extractions)
        },
        status_code=200
    )

@app.get("/user/{user_id}/curricula")
async def get_user_curricula(
    user_id: int = Path(..., description="User ID"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results")
):
    """Get user's curricula"""
    curricula = await db.get_user_curricula(user_id, limit)
    
    # Parse JSON fields and get content status
    for curriculum in curricula:
        curriculum['curriculum'] = json.loads(curriculum['curriculum_json'])
        del curriculum['curriculum_json']
        
        # Get content status
        status = await db.get_curriculum_content_status(curriculum['id'])
        if status:
            curriculum['content_status'] = status
    
    return JSONResponse(
        content={
            "user_id": user_id,
            "curricula": curricula,
            "total": len(curricula)
        },
        status_code=200
    )

@app.get("/user/{user_id}/journeys")
async def get_user_learning_journeys(
    user_id: int = Path(..., description="User ID"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results")
):
    """Get user's complete learning journeys (metadata + curriculum info)"""
    journeys = await db.get_user_learning_journeys(user_id, limit)
    
    return JSONResponse(
        content={
            "user_id": user_id,
            "journeys": journeys,
            "total": len(journeys)
        },
        status_code=200
    )

@app.get("/search/curricula")
async def search_curricula(
    native_language: str = Query(..., description="Native language"),
    target_language: str = Query(..., description="Target language"),
    proficiency: Optional[str] = Query(None, description="Proficiency level"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results")
):
    """Search for existing curricula by language combination"""
    curricula = await db.search_curricula_by_languages(
        native_language=native_language,
        target_language=target_language,
        proficiency=proficiency,
        limit=limit
    )
    
    # Parse JSON fields
    for curriculum in curricula:
        curriculum['curriculum'] = json.loads(curriculum['curriculum_json'])
        del curriculum['curriculum_json']
    
    return JSONResponse(
        content={
            "search_params": {
                "native_language": native_language,
                "target_language": target_language,
                "proficiency": proficiency
            },
            "curricula": curricula,
            "total": len(curricula)
        },
        status_code=200
    )

@app.get("/content/status/{curriculum_id}")
async def get_content_generation_status(
    curriculum_id: str = Path(..., description="Curriculum ID")
):
    """Check content generation status for a curriculum"""
    status = await db.get_curriculum_content_status(curriculum_id)
    if not status:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    
    # Calculate completion percentage
    total_lessons = 25
    total_content_types = 3  # flashcards, exercises, simulation
    total_expected = total_lessons * total_content_types
    
    total_generated = (
        status['lessons_with_flashcards'] +
        status['lessons_with_exercises'] +
        status['lessons_with_simulations']
    )
    
    completion_percentage = (total_generated / total_expected) * 100 if total_expected > 0 else 0
    
    return JSONResponse(
        content={
            "curriculum_id": curriculum_id,
            "status": status,
            "completion_percentage": round(completion_percentage, 2),
            "is_complete": completion_percentage >= 100
        },
        status_code=200
    )

