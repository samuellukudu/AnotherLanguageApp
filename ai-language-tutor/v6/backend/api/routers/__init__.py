# Import all routers for easy access
from backend.api.routers.metadata import router as metadata_router
from backend.api.routers.curriculum import router as curriculum_router
from backend.api.routers.flashcards import router as flashcards_router
from backend.api.routers.exercises import router as exercises_router
from backend.api.routers.simulation import router as simulation_router

# Export routers
metadata = metadata_router
curriculum = curriculum_router
flashcards = flashcards_router
exercises = exercises_router
simulation = simulation_router