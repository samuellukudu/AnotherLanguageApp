from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiocache import caches
from backend.settings import REDIS_URL
import logging
from backend.routers.generation import router as gen_router
from backend.routers.auth import router as auth_router
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(debug=True)

# Configure default Redis cache
caches.set_config({"default": {"cache": "aiocache.RedisCache", "endpoint": REDIS_URL}})

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(gen_router)

from backend.services.logging_service import periodic_flush_task
import asyncio
from backend.db.supabase_client import get_supabase

@app.on_event("startup")
async def start_periodic_log_flush():
    """Launch background task to flush buffered query logs."""
    # No aiocache config needed; logging_service uses aioredis directly
    # Start periodic flush
    session = get_supabase()
    asyncio.create_task(periodic_flush_task(session))

# Centralized error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse({"error": exc.errors()}, status_code=422)

"""Remove generic exception handler to expose stack traces."""
# @app.exception_handler(Exception)
# async def generic_exception_handler(request, exc: Exception):
#     return JSONResponse({"error": "Internal server error"}, status_code=500)

# Health & readiness probes
@app.get('/health')
async def health_check():
    return {"status": "ok"}

@app.get('/ready')
async def readiness_check():
    # optionally check DB or caches here
    return {"status": "ready"}