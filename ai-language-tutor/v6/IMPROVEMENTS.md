
# Backend Improvements for AI Language Tutor

This document outlines the steps to improve the backend by adopting a fully asynchronous content generation workflow and providing more efficient data retrieval endpoints.

## 1. Asynchronous Content Generation Workflow

To prevent long-running API requests, the backend will adopt an asynchronous workflow. Content generation will be initiated by a single API call that returns immediately, allowing the frontend to track progress via a status endpoint.

### 1.1. Update `/extract/metadata` Endpoint Response

The `POST /extract/metadata` endpoint is the primary entry point for creating a new learning curriculum. Its response should be modified to reflect the asynchronous nature of the operation.

**Proposed Change:**

Instead of returning a `200 OK` with the full metadata, the endpoint should return a `202 Accepted`. The response body will contain the `curriculum_id` and a `status_endpoint` that the frontend can poll to check the content generation progress.

**Current Response (`200 OK`):**
```json
{
  "data": { ... metadata ... },
  "extraction_id": "...",
  "curriculum_id": "...",
  "content_generation_started": true,
  "type": "language_metadata",
  "status": "success"
}
```

**Proposed New Response (`202 Accepted`):**
```json
{
  "message": "Content generation has been initiated.",
  "curriculum_id": "...",
  "status_endpoint": "/content/status/..."
}
```
This change requires a minor modification in the `extract_metadata` function in `main.py` to format the response correctly. The underlying background task logic in `content_generator.py` is already in place and can be reused.

### 1.2. Polling for Status

The frontend can use the existing `GET /content/status/{curriculum_id}` endpoint to poll for updates on the content generation process. This endpoint already provides detailed progress.

## 2. Efficient Content Retrieval with Improved GET Endpoints

To reduce the number of API calls required from the frontend, the GET endpoints for retrieving curriculum data should be enhanced to return all necessary information in a single request.

### 2.1. Consolidate Curriculum Data Retrieval

Currently, fetching a curriculum and all its lesson content (flashcards, exercises, simulations) requires multiple API calls: one for the curriculum structure, and then N calls for the N lessons. This should be consolidated.

**Proposed Improvement:**

Modify the `GET /curriculum/{curriculum_id}` endpoint to return the complete curriculum object, with all lesson content nested within it.

1.  **Create a new database function in `db.py`**: Implement a function like `get_full_curriculum_details(curriculum_id)` that efficiently fetches the curriculum and all its associated learning content and assembles it into a single, nested Python dictionary.

2.  **Update the endpoint in `main.py`**: The `GET /curriculum/{curriculum_id}` endpoint will now call this new database function and return the complete data structure. This provides the frontend with all the data needed to display a full curriculum with a single API call.

**Example of the new nested response structure:**
```json
{
  "id": "curriculum_id",
  "lesson_topic": "Beginner Spanish",
  "curriculum": {
    "lesson_topic": "Beginner Spanish",
    "sub_topics": [
      {
        "sub_topic": "Greetings and Introductions",
        "description": "Learn basic greetings...",
        "content": {
          "flashcards": [ ... ],
          "exercises": [ ... ],
          "simulation": { ... }
        }
      },
      {
        "sub_topic": "Numbers and Colors",
        "description": "Learn to count and name colors...",
        "content": {
          "flashcards": [ ... ],
          "exercises": [ ... ],
          "simulation": { ... }
        }
      }
    ]
  },
  "is_content_generated": true,
  // ... other metadata ...
}
```
The existing endpoint `GET /curriculum/{curriculum_id}/lesson/{lesson_index}` can remain for cases where only a single lesson's content is needed.

## 3. Refactoring and Cleanup

### 3.1. Integrate Database Cache

The `db_cache.py` module provides a persistent caching layer that can reduce redundant calls to the LLM API, saving costs and speeding up generation for repeated requests. This should be integrated into the content generation process.

**Proposed Improvement:**

-   In `content_generator.py`, within the `generate_content_for_lesson` function, wrap the calls to `generate_completions.get_completions` with `db_cache.get_or_set`. This will cache the generated content in the database.

### 3.2. Remove Legacy Endpoints

The old POST endpoints for generating specific content types (`/generate/curriculum`, `/generate/flashcards`, etc.) are now obsolete under the new asynchronous workflow. They should be removed from `main.py` to simplify the API surface.
