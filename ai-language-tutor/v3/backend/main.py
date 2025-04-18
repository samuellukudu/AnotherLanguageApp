from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.utils import generate_completions
from backend import config
from backend.database import get_db_connection
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

# Dependency to get database connection
async def get_db():
    conn = await get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

class GenerationRequest(BaseModel):
    user_id: int
    query: str

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Learning Assistant API!"}

@app.post("/generate/flashcards")
async def generate_flashcards(data: GenerationRequest):
    try:
        response = await generate_completions.get_completions(
            data.query,
            config.flashcard_mode_instructions
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
        response = await generate_completions.get_completions(
            data.query,
            config.exercise_mode_instructions
        )
        # adjust the response similar to generate_flashcards
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
        response = await generate_completions.get_completions(
            data.query,
            config.simulation_mode_instructions
        )
        # adjust the response similar to generate_flashcards
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