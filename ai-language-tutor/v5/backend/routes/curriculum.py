from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from backend.storage import storage
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# POST endpoint removed - curriculum creation now happens automatically after metadata extraction

@router.get("/curriculum/{curriculum_id}")
async def get_curriculum(curriculum_id: str):
    """Get curriculum by ID"""
    curriculum = await storage.get_curriculum(curriculum_id)
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    
    status = curriculum["status"]["curriculum"]
    content = curriculum["content"]["curriculum"]
    
    if status == "completed" and content:
        return JSONResponse(content={
            "curriculum_id": curriculum["id"],
            "curriculum": content,
            "metadata": curriculum["metadata"],
            "created_at": curriculum["created_at"],
            "status": "completed"
        })
    elif status == "generating":
        return JSONResponse(content={
            "curriculum_id": curriculum["id"],
            "metadata": curriculum["metadata"],
            "created_at": curriculum["created_at"],
            "message": "Curriculum is being generated",
            "status": "generating"
        })
    elif status == "failed":
        return JSONResponse(content={
            "curriculum_id": curriculum["id"],
            "metadata": curriculum["metadata"],
            "created_at": curriculum["created_at"],
            "message": "Curriculum generation failed",
            "status": "failed"
        }, status_code=500)
    else:
        return JSONResponse(content={
            "curriculum_id": curriculum["id"],
            "metadata": curriculum["metadata"],
            "created_at": curriculum["created_at"],
            "message": "Curriculum is pending generation",
            "status": "pending"
        })

@router.get("/curriculum/{curriculum_id}/flashcards")
async def get_flashcards(curriculum_id: str):
    """Get flashcards for a curriculum"""
    curriculum = await storage.get_curriculum(curriculum_id)
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    
    status = curriculum["status"]["flashcards"]
    content = curriculum["content"]["flashcards"]
    
    if status == "completed" and content:
        return JSONResponse(content={"data": content, "status": "completed"})
    elif status == "generating":
        return JSONResponse(content={"message": "Flashcards are being generated", "status": "generating"})
    elif status == "failed":
        return JSONResponse(content={"message": "Flashcard generation failed", "status": "failed"}, status_code=500)
    else:
        return JSONResponse(content={"message": "Flashcards are pending generation", "status": "pending"})

@router.get("/curriculum/{curriculum_id}/exercises")
async def get_exercises(curriculum_id: str):
    """Get exercises for a curriculum"""
    curriculum = await storage.get_curriculum(curriculum_id)
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    
    status = curriculum["status"]["exercises"]
    content = curriculum["content"]["exercises"]
    
    if status == "completed" and content:
        return JSONResponse(content={"data": content, "status": "completed"})
    elif status == "generating":
        return JSONResponse(content={"message": "Exercises are being generated", "status": "generating"})
    elif status == "failed":
        return JSONResponse(content={"message": "Exercise generation failed", "status": "failed"}, status_code=500)
    else:
        return JSONResponse(content={"message": "Exercises are pending generation", "status": "pending"})

@router.get("/curriculum/{curriculum_id}/simulation")
async def get_simulation(curriculum_id: str):
    """Get simulation for a curriculum"""
    curriculum = await storage.get_curriculum(curriculum_id)
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    
    status = curriculum["status"]["simulation"]
    content = curriculum["content"]["simulation"]
    
    if status == "completed" and content:
        return JSONResponse(content={"data": content, "status": "completed"})
    elif status == "generating":
        return JSONResponse(content={"message": "Simulation is being generated", "status": "generating"})
    elif status == "failed":
        return JSONResponse(content={"message": "Simulation generation failed", "status": "failed"}, status_code=500)
    else:
        return JSONResponse(content={"message": "Simulation is pending generation", "status": "pending"})

@router.get("/curriculum/{curriculum_id}/status")
async def get_curriculum_status(curriculum_id: str):
    """Get the status of all content for a curriculum"""
    curriculum = await storage.get_curriculum(curriculum_id)
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    
    return JSONResponse(content={
        "curriculum_id": curriculum["id"],
        "status": curriculum["status"],
        "created_at": curriculum["created_at"],
        "updated_at": curriculum.get("updated_at")
    })

@router.get("/user/{user_id}/curricula")
async def get_user_curricula(user_id: int):
    """Get all curricula for a user"""
    curricula = await storage.get_user_curricula(user_id)
    
    # Return summary information
    summary = []
    for curriculum in curricula:
        summary.append({
            "curriculum_id": curriculum["id"],
            "title": curriculum["metadata"]["title"],
            "description": curriculum["metadata"]["description"],
            "target_language": curriculum["metadata"]["target_language"],
            "proficiency": curriculum["metadata"]["proficiency"],
            "created_at": curriculum["created_at"],
            "status": curriculum["status"]
        })
    
    return JSONResponse(content={"curricula": summary}) 