# Backend Directory Structure

This backend is organized for scalability and maintainability. Each major feature is separated into its own module, making it easy to add new features and maintain existing ones.

## Structure

```
backend/
│
├── api/                # FastAPI route definitions (split by feature)
├── models/             # Database models (ORM classes)
├── schemas/            # Pydantic schemas for request/response validation
├── services/           # Business logic, background tasks, and helpers
├── utils/              # Utility functions (e.g., cache, LLM, etc.)
├── config.py           # Configuration and settings
├── main.py             # FastAPI app entry point
└── requirements.txt
```

## Folder Descriptions
- **api/**: All API route definitions, grouped by feature (e.g., curriculum, users, lessons).
- **models/**: Database models (SQLAlchemy or other ORM classes).
- **schemas/**: Pydantic schemas for request/response validation.
- **services/**: Business logic, background tasks, and helpers for each feature.
- **utils/**: Utility functions and shared helpers (e.g., cache, LLM integration).

## Adding a New Feature
1. Add a new route file in `api/`.
2. Add corresponding models, schemas, and services.
3. Register the new router in `main.py`.

## Notes
- Keep `main.py` focused on app creation and router inclusion.
- Update imports as you move code into the new structure. 