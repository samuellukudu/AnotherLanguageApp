from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.utils import generate_completions
from backend.utils.handlers import handle_generation_request, INSTRUCTION_TEMPLATES
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
    return await handle_generation_request(
        data=data,
        mode="curriculum",
        instructions_template=INSTRUCTION_TEMPLATES["curriculum"]
    )

@app.post("/generate/flashcards")
async def generate_flashcards(data: GenerationRequest):
    return await handle_generation_request(
        data=data,
        mode="flashcards",
        instructions_template=INSTRUCTION_TEMPLATES["flashcards"]
    )

@app.post("/generate/exercises")
async def generate_exercises(data: GenerationRequest):
    return await handle_generation_request(
        data=data,
        mode="exercises",
        instructions_template=INSTRUCTION_TEMPLATES["exercises"]
    )

@app.post("/generate/simulation")
async def generate_simulation(data: GenerationRequest):
    return await handle_generation_request(
        data=data,
        mode="simulation",
        instructions_template=INSTRUCTION_TEMPLATES["simulation"]
    )