from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.utils import generate_completions
from backend import config
from typing import Union, List, Literal, Optional
import logging
import json
from backend.cache import cache

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

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

# Global metadata variables
native_language: Optional[str] = None
target_language: Optional[str] = None
proficiency: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Learning Assistant API!"}

@app.post("/extract/metadata")
async def extract_metadata(data: MetadataRequest):
    logging.info(f"Query: {data.query}")
    try:
        response_str = await cache.get_or_set(
            (str(data.query), config.language_metadata_extraction_prompt),
            generate_completions.get_completions,
            data.query,
            config.language_metadata_extraction_prompt
        )
        metadata_dict = json.loads(response_str)
        # Update globals for other endpoints
        globals()['native_language'] = metadata_dict.get('native_language', 'unknown')
        globals()['target_language'] = metadata_dict.get('target_language', 'unknown')
        globals()['proficiency'] = metadata_dict.get('proficiency', 'unknown')
        return JSONResponse(
            content={
                "data": metadata_dict,
                "type": "language_metadata",
                "status": "success"
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/curriculum")
async def generate_curriculum(data: GenerationRequest):
    try:
        # Use metadata from request or fallback to globals
        nl = data.native_language or native_language or "unknown"
        tl = data.target_language or target_language or "unknown"
        prof = data.proficiency or proficiency or "unknown"
        instructions = (
            config.curriculum_instructions
            .replace("{native_language}", nl)
            .replace("{target_language}", tl)
            .replace("{proficiency}", prof)
        )
        response = await cache.get_or_set(
            (str(data.query), instructions),
            generate_completions.get_completions,
            data.query,
            instructions
        )
        return JSONResponse(
            content={
                "data": response,
                "type": "curriculum",
                "status": "success"
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/flashcards")
async def generate_flashcards(data: GenerationRequest):
    try:
        nl = data.native_language or native_language or "unknown"
        tl = data.target_language or target_language or "unknown"
        prof = data.proficiency or proficiency or "unknown"
        instructions = (
            config.flashcard_mode_instructions
            .replace("{native_language}", nl)
            .replace("{target_language}", tl)
            .replace("{proficiency}", prof)
        )
        response = await cache.get_or_set(
            (str(data.query), instructions),
            generate_completions.get_completions,
            data.query,
            instructions
        )
        return JSONResponse(
            content={
                "data": response,
                "type": "flashcards",
                "status": "success"
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/exercises")
async def generate_exercises(data: GenerationRequest):
    try:
        nl = data.native_language or native_language or "unknown"
        tl = data.target_language or target_language or "unknown"
        prof = data.proficiency or proficiency or "unknown"
        instructions = (
            config.exercise_mode_instructions
            .replace("{native_language}", nl)
            .replace("{target_language}", tl)
            .replace("{proficiency}", prof)
        )
        response = await cache.get_or_set(
            (str(data.query), instructions),
            generate_completions.get_completions,
            data.query,
            instructions
        )
        return JSONResponse(
            content={
                "data": response,
                "type": "exercises",
                "status": "success"
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/simulation")
async def generate_simulation(data: GenerationRequest):
    try:
        nl = data.native_language or native_language or "unknown"
        tl = data.target_language or target_language or "unknown"
        prof = data.proficiency or proficiency or "unknown"
        instructions = (
            config.simulation_mode_instructions
            .replace("{native_language}", nl)
            .replace("{target_language}", tl)
            .replace("{proficiency}", prof)
        )
        response = await cache.get_or_set(
            (str(data.query), instructions),
            generate_completions.get_completions,
            data.query,
            instructions
        )
        return JSONResponse(
            content={
                "data": response,
                "type": "simulation",
                "status": "success"
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))