# from backend.utils import generate_completions 
# from backend import config

# query = "Need to pitch my startup idea to investors"

# # instructions = config.flashcard_mode_instructions
# # instructions = config.exercise_mode_instructions
# instructions = config.simulation_mode_instructions
# async def main():
#     # Example usage
#     response = await generate_completions.get_completions(query, instructions)
#     print(response)

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())

from fastapi import FastAPI, HTTPException
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


@app.post("/generate/flashcards")
async def generate_flashcards(data: GenerationRequest):
    try:
        response = await generate_completions.get_completions(
            data.query,
            config.flashcard_mode_instructions
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/exercises")
async def generate_exercises(data: GenerationRequest):
    try:
        response = await generate_completions.get_completions(
            data.query,
            config.exercise_mode_instructions
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/simulation")
async def generate_simulation(data: GenerationRequest):
    try:
        response = await generate_completions.get_completions(
            data.query,
            config.simulation_mode_instructions
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))