from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from supabase import Client
from backend.db.supabase_client import get_supabase
from backend.schemas import GenerationRequest, MetadataRequest, User as UserSchema
from backend.services.generation_service import (
    extract_metadata_service,
    generate_flashcards_service,
    generate_exercises_service,
    generate_simulation_service,
)
from backend.auth import get_current_active_user
from aiocache.decorators import cached
from backend.settings import settings

router = APIRouter(prefix="", tags=["generation"])

@router.get("/")
async def root():
    return {"message": "Welcome to the AI Learning Assistant API!"}

@router.post("/extract/metadata")
@cached(ttl=settings.cache_ttl)
async def extract_metadata(
    data: MetadataRequest,
    session: Client = Depends(get_supabase),
    current_user: UserSchema = Depends(get_current_active_user)
):
    try:
        response = await extract_metadata_service(session, current_user.user_id, data.query)
        return JSONResponse({"data": response, "type": "language_metadata", "status": "success"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/flashcards")
@cached(ttl=settings.cache_ttl)
async def generate_flashcards(
    data: GenerationRequest,
    session: Client = Depends(get_supabase),
    current_user: UserSchema = Depends(get_current_active_user)
):
    try:
        response = await generate_flashcards_service(session, current_user.user_id, data.query)
        return JSONResponse({"data": response, "type": "flashcards", "status": "success"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/exercises")
@cached(ttl=settings.cache_ttl)
async def generate_exercises(
    data: GenerationRequest,
    session: Client = Depends(get_supabase),
    current_user: UserSchema = Depends(get_current_active_user)
):
    try:
        response = await generate_exercises_service(session, current_user.user_id, data.query)
        return JSONResponse({"data": response, "type": "exercises", "status": "success"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/simulation")
@cached(ttl=settings.cache_ttl)
async def generate_simulation(
    data: GenerationRequest,
    session: Client = Depends(get_supabase),
    current_user: UserSchema = Depends(get_current_active_user)
):
    try:
        response = await generate_simulation_service(session, current_user.user_id, data.query)
        return JSONResponse({"data": response, "type": "simulation", "status": "success"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
