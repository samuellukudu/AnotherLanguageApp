from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import uvicorn
from pydantic import BaseModel, Field
from typing import Union, List, Dict
import json
import asyncio
from backend.utils import get_completion
from backend.config import CURRICULUM_INSTRUCTIONS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a request model
class QueryRequest(BaseModel):
    user_query: str

# Define a response model
class QueryResponse(BaseModel):
    answer: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/curriculum")
async def get_curriculum(request: QueryRequest):
    query = request.user_query
    response = await get_completion(prompt=query, instruction=CURRICULUM_INSTRUCTIONS)
    return JSONResponse(response, media_type="application/json")