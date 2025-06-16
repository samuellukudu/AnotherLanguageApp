# AI Language Tutor - Layered Architecture Implementation

## Project Overview
AI Language Tutor is an application designed to help users learn new languages through AI-powered interactions. This implementation follows a layered/hexagonal architecture to improve maintainability, testability, and scalability.

## Architecture

The application is structured using a layered architecture with the following components:

### Core Layer
- **Configuration**: Centralized settings management using Pydantic's BaseSettings
- **Exceptions**: Custom exception hierarchy for better error handling

### Repository Layer
- Database access abstractions
- Connection pooling and management
- SQL query execution

### Service Layer
- Business logic implementation
- Error handling and logging
- Integration with external services (AI models)

### API Layer
- FastAPI routes and endpoints
- Request/response models
- Input validation

## Key Components

### Database Management
- Connection pooling for efficient database access
- Repository pattern for data access abstraction
- Centralized error handling for database operations

### AI Service
- Integration with OpenAI/Gemini models
- Structured prompt management
- Error handling for AI service operations

### Error Handling
- Custom exception hierarchy
- Centralized exception handling
- Detailed error logging

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL database
- API key for OpenAI/Gemini

### Environment Setup
Create a `.env` file with the following variables:
```
API_PORT=8001
POSTGRES_DB=linguaai
POSTGRES_USER=linguaai_user
POSTGRES_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
API_KEY=your_api_key
MODEL=gemini-2.0-flash
```

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Start the application: `uvicorn backend.main:app --reload`

## API Endpoints

- **GET /**: Welcome message
- **GET /health**: Health check endpoint
- **POST /extract/metadata**: Extract language learning metadata from user input
- **POST /curriculum**: Generate a personalized curriculum
- **POST /flashcards**: Generate flashcards
- **POST /exercises**: Generate exercises
- **POST /simulation**: Generate conversation simulations

## Development Guidelines

### Adding New Features
1. Define models in `backend/api/models.py`
2. Implement repository methods in appropriate repository classes
3. Implement business logic in service classes
4. Create API endpoints in router modules
5. Update configuration if needed

### Error Handling
Use the custom exception classes defined in `backend/core/exceptions.py` for consistent error handling across the application.

### Logging
Use the logger configured in each module for consistent logging:
```python
logger = logging.getLogger(__name__)
logger.info("Your log message")
```

## Testing
The layered architecture makes it easier to test individual components:
- Repository tests: Test database operations
- Service tests: Test business logic with mocked repositories
- API tests: Test endpoints with mocked services