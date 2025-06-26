from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import health, extraction, curriculum
import logging

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

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(extraction.router, prefix="/extract", tags=["extraction"])
app.include_router(curriculum.router, tags=["curriculum"])