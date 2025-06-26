from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi

from backend.api import curriculum, lessons, flashcards, exercises, simulation, users, metadata

# Create FastAPI app with custom OpenAPI configuration
app = FastAPI(
    title="AI Learning Assistant API",
    description="A comprehensive API for AI-powered language learning",
    version="1.0.0"
)

# Security scheme for OpenAPI (this will show the authorize button)
security = HTTPBearer()

# Custom OpenAPI schema with security
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="AI Learning Assistant API",
        version="1.0.0",
        description="A comprehensive API for AI-powered language learning with authentication",
        routes=app.routes,
    )
    
    # Add security scheme definition
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token"
        }
    }
    
    # Apply security to all protected endpoints
    for path_data in openapi_schema["paths"].values():
        for operation in path_data.values():
            # Skip if it's not an operation or if it's a public endpoint
            if not isinstance(operation, dict) or "tags" not in operation:
                continue
                
            # Add security to all endpoints except register and login
            if operation.get("operationId") not in ["register", "login", "root"]:
                operation["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Apply custom OpenAPI schema
app.openapi = custom_openapi

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Learning Assistant API!"}

# Include routers for modular endpoints
app.include_router(users.router)
app.include_router(metadata.router)
app.include_router(curriculum.router)
app.include_router(lessons.router)
app.include_router(flashcards.router)
app.include_router(exercises.router)
app.include_router(simulation.router)