from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from typing import Callable

# Import configuration
from backend.core.config import settings

# Import centralized logging
from backend.core.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Import routers
from backend.api.routers import metadata, curriculum, flashcards, exercises, simulation

# Import services
from backend.services.database_service import database_service

# Import exception handling
from backend.core.exceptions import BaseAppException, handle_exception

# Initialize FastAPI app
app = FastAPI(title="AI Language Tutor API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request started: {request.method} {request.url.path}")
    
    # Process the request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log response details
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Time: {process_time:.4f}s"
        )
        return response
    except Exception as exc:
        # Log exception details
        logger.error(
            f"Request failed: {request.method} {request.url.path} "
            f"- Error: {str(exc)}"
        )
        raise

# Exception handler for application exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, BaseAppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.message,
                "details": exc.details,
                "status": "error"
            }
        )
    else:
        # Handle unexpected exceptions
        http_exception = handle_exception(exc)
        return JSONResponse(
            status_code=http_exception.status_code,
            content={
                "message": http_exception.detail.get("message", "An unexpected error occurred"),
                "details": http_exception.detail.get("details", {}),
                "status": "error"
            }
        )

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the AI Learning Assistant API!"}

# Health check endpoint
@app.get("/health")
async def health_check():
    # Check database connection
    db_status = await database_service.check_database_connection()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "api": "running"
    }

# Include routers
app.include_router(metadata)
app.include_router(curriculum)
app.include_router(flashcards)
app.include_router(exercises)
app.include_router(simulation)

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the API...")
    try:
        # Initialize database
        await database_service.initialize_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # Don't raise the exception to allow the API to start even if DB init fails

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the API...")
    # Close database connections
    from backend.repositories.base_repository import DatabaseConnectionManager
    DatabaseConnectionManager.close_all_connections()