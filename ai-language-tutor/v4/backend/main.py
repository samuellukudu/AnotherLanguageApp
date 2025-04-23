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
from backend.db.session import engine
from backend.db.models import Base

logging.basicConfig(level=logging.INFO)

app = FastAPI()

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

# Create tables on startup
@app.on_event("startup")
async def create_tables():
    import asyncio, logging as _logging
    for attempt in range(10):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            _logging.info("Database tables created")
            return
        except Exception as err:
            _logging.warning(f"Database not ready (attempt {attempt+1}/10): {err}")
            await asyncio.sleep(2)
    _logging.error("Failed to create tables after multiple attempts")

# Centralized error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse({"error": exc.errors()}, status_code=422)

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception):
    return JSONResponse({"error": "Internal server error"}, status_code=500)

# Health & readiness probes
@app.get('/health')
async def health_check():
    return {"status": "ok"}

@app.get('/ready')
async def readiness_check():
    # optionally check DB or caches here
    return {"status": "ready"}