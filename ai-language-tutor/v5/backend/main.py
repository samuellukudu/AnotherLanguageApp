from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiocache import caches
from backend.settings import settings
import logging
from backend.routers.generation import router as gen_router
from backend.routers.auth import router as auth_router
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError

logging.basicConfig(level=logging.INFO)
# Reduce chatty debug logs
logging.getLogger("aiocache").setLevel(logging.INFO)
logging.getLogger("openai").setLevel(logging.INFO)
logging.getLogger("httpcore").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO)

app = FastAPI(debug=True)

# Configure default Redis cache
caches.set_config({"default": {"cache": "aiocache.RedisCache", "endpoint": settings.redis_url}})

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

from backend.db.supabase_client import get_supabase

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