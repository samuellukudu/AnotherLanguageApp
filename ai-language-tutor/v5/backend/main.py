from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import health, extraction, curriculum
import logging
from contextlib import asynccontextmanager

# Import database functionality
try:
    from backend.database import database
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if DATABASE_AVAILABLE:
        try:
            await database.initialize_database()
            logging.info("Database initialized successfully")
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
    else:
        logging.warning("Database not available, using file storage only")
    
    yield
    
    # Shutdown
    logging.info("Application shutting down")

app = FastAPI(lifespan=lifespan)

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