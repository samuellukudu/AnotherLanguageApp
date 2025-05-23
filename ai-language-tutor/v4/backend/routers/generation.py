from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.session import get_db_session
from backend.schemas import GenerationRequest, MetadataRequest, User as UserSchema
from backend.services.generation_service import (
    extract_metadata_service,
    generate_flashcards_service,
    generate_exercises_service,
    generate_simulation_service,
)
from backend.auth import get_current_active_user
from aiocache.decorators import cached
from backend.settings import CACHE_TTL

router = APIRouter(prefix="", tags=["generation"])

@router.get("/")
async def root():
    return {"message": "Welcome to the AI Learning Assistant API!"}

@router.post("/extract/metadata")
@cached(ttl=CACHE_TTL)
async def extract_metadata(
    data: MetadataRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: UserSchema = Depends(get_current_active_user)
):
    try:
        response = await extract_metadata_service(session, current_user.user_id, data.query)
        return JSONResponse({"data": response, "type": "language_metadata", "status": "success"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/flashcards")
@cached(ttl=CACHE_TTL)
async def generate_flashcards(
    data: GenerationRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: UserSchema = Depends(get_current_active_user)
):
    try:
        response = await generate_flashcards_service(session, current_user.user_id, data.query)
        return JSONResponse({"data": response, "type": "flashcards", "status": "success"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/exercises")
@cached(ttl=CACHE_TTL)
async def generate_exercises(
    data: GenerationRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: UserSchema = Depends(get_current_active_user)
):
    try:
        response = await generate_exercises_service(session, current_user.user_id, data.query)
        return JSONResponse({"data": response, "type": "exercises", "status": "success"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/simulation")
@cached(ttl=CACHE_TTL)
async def generate_simulation(
    data: GenerationRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: UserSchema = Depends(get_current_active_user)
):
    try:
        response = await generate_simulation_service(session, current_user.user_id, data.query)
        return JSONResponse({"data": response, "type": "simulation", "status": "success"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
