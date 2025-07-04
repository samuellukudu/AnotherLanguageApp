from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.utils import generate_completions
from backend.utils.handlers import handle_generation_request, INSTRUCTION_TEMPLATES
from backend import config
from backend.content_service import content_service
from backend.database import create_tables
from typing import Union, List, Literal, Optional
import logging
import json

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AI Language Tutor API", version="1.0.0")

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
    user_id: Optional[int] = None  # Make user_id optional for anonymous extractions

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    await create_tables()
    logging.info("SQLite database tables initialized")

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Learning Assistant API!"}

@app.post("/extract/metadata")
async def extract_metadata(data: MetadataRequest):
    logging.info(f"Extracting metadata for query: {data.query[:50]}...")
    try:
        # Generate metadata using AI
        response_str = await generate_completions.get_completions(
            data.query,
            config.language_metadata_extraction_prompt
        )
        metadata_dict = json.loads(response_str)
        
        # Save metadata to database
        content_id = await content_service.save_metadata(
            query=data.query,
            metadata=metadata_dict,
            user_id=data.user_id
        )
        
        return JSONResponse(
            content={
                "data": metadata_dict,
                "type": "language_metadata",
                "status": "success",
                "content_id": content_id,
                "saved": True
            },
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error extracting metadata: {e}")
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

# GET ENDPOINTS FOR RETRIEVING SAVED CONTENT

@app.get("/content/{content_id}")
async def get_saved_content(content_id: str):
    """Retrieve saved content by content ID"""
    try:
        content = await content_service.get_content_by_id(content_id)
        if content:
            return JSONResponse(
                content={
                    "data": json.loads(content["content"]) if content["content_type"] != "raw" else content["content"],
                    "content_type": content["content_type"],
                    "query": content["query"],
                    "native_language": content["native_language"],
                    "target_language": content["target_language"],
                    "proficiency": content["proficiency"],
                    "created_at": content["created_at"],
                    "status": "success"
                },
                status_code=200
            )
        else:
            raise HTTPException(status_code=404, detail="Content not found")
    except Exception as e:
        logging.error(f"Error retrieving content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/metadata")
async def get_user_metadata_history(
    user_id: int,
    limit: int = Query(20, description="Maximum number of metadata extractions to return")
):
    """Get user's metadata extraction history"""
    try:
        metadata_list = await content_service.get_user_metadata_history(user_id, limit)
        return JSONResponse(
            content={
                "data": metadata_list,
                "total": len(metadata_list),
                "user_id": user_id,
                "status": "success"
            },
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error retrieving user metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/content")
async def get_user_content(
    user_id: int,
    content_type: Optional[str] = Query(None, description="Filter by content type (metadata, curriculum, flashcards, exercises, simulation)"),
    limit: int = Query(50, description="Maximum number of items to return")
):
    """Get all saved content for a specific user"""
    try:
        content_list = await content_service.get_user_content(
            user_id=user_id,
            content_type=content_type,
            limit=limit
        )
        return JSONResponse(
            content={
                "data": content_list,
                "total": len(content_list),
                "user_id": user_id,
                "content_type_filter": content_type,
                "status": "success"
            },
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error retrieving user content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/content/{content_id}")
async def delete_saved_content(content_id: str):
    """Delete saved content by content ID"""
    try:
        deleted = await content_service.delete_content(content_id)
        if deleted:
            return JSONResponse(
                content={
                    "message": "Content deleted successfully",
                    "content_id": content_id,
                    "status": "success"
                },
                status_code=200
            )
        else:
            raise HTTPException(status_code=404, detail="Content not found")
    except Exception as e:
        logging.error(f"Error deleting content: {e}")
        raise HTTPException(status_code=500, detail=str(e))