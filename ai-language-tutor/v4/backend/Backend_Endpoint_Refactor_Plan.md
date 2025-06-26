# Backend Endpoint Refactor Plan

## Problem
Currently, all endpoints are POST and content is generated on-the-fly for every query, leading to slow response times and unnecessary recomputation.

## Proposed Solution
- **Curriculum Generation:**
  - Keep as a POST endpoint (`/curriculum`).
  - When a curriculum is generated, save it to the database **along with all relevant metadata** (e.g., user, languages, proficiency, etc.).
  - Trigger automatic generation of related content (flashcards, exercises, simulations) and save these to the database as well.
- **Content Retrieval:**
  - Expose GET endpoints for flashcards, exercises, simulations, and lessons.
  - When a GET request is made, fetch pre-generated content from the database, ensuring fast response times.
- **User Profile Management:**
  - Add endpoints and database tables/models for user registration, authentication, and profile management.
  - Link all generated content and metadata to the user profile.

## Endpoint Design

### 1. POST /curriculum
- **Request:** User submits query and metadata.
- **Action:**
  - Generate curriculum.
  - Save curriculum and metadata (user, languages, proficiency, etc.) to database.
  - Trigger background jobs to generate and save related content (flashcards, exercises, simulations).
- **Response:** Curriculum data (and optionally, job status for related content).

### 2. GET /lessons/{curriculum_id}
- **Request:** User requests lessons for a given curriculum.
- **Action:** Fetch lessons from database.
- **Response:** List of lessons.

### 3. GET /flashcards/{curriculum_id}
- **Request:** User requests flashcards for a given curriculum.
- **Action:** Fetch flashcards from database.
- **Response:** List of flashcards.

### 4. GET /exercises/{curriculum_id}
- **Request:** User requests exercises for a given curriculum.
- **Action:** Fetch exercises from database.
- **Response:** List of exercises.

### 5. GET /simulation/{curriculum_id}
- **Request:** User requests simulation content for a given curriculum.
- **Action:** Fetch simulation from database.
- **Response:** Simulation data.

### 6. User Profile Endpoints
- **POST /users/register:** Register a new user.
- **POST /users/login:** Authenticate user and return token/session.
- **GET /users/profile:** Retrieve user profile and metadata.
- **PUT /users/profile:** Update user profile and preferences.

## Implementation Suggestions

1. **Database Schema:**
   - Design tables/models for User, Curriculum, Lesson, Flashcard, Exercise, Simulation.
   - Ensure all content tables reference `user_id` and store relevant metadata (native language, target language, proficiency, etc.).
2. **Metadata Storage:**
   - Store all metadata submitted with curriculum and content generation (languages, proficiency, timestamps, etc.).
   - Link metadata to both user and content records.
3. **Background Processing:**
   - Use a task queue (e.g., Celery, RQ, or FastAPI background tasks) to generate related content after curriculum creation.
4. **Endpoint Refactor:**
   - Change flashcards, exercises, and simulation endpoints to GET.
   - Accept `curriculum_id` as a path or query parameter.
5. **Content Retrieval Logic:**
   - On GET, check if content exists in the database; if not, return an error or trigger generation.
6. **User Experience:**
   - Optionally, provide job status or notifications if related content is still being generated.
7. **Caching:**
   - Optionally, cache frequently accessed content for even faster retrieval.

## Benefits
- **Performance:** GET endpoints return content instantly from the database.
- **Scalability:** Content is generated once and reused, reducing compute load.
- **User Experience:** Faster, more reliable responses for most endpoints.
- **Personalization:** User profiles and metadata enable personalized content and progress tracking.

## Next Steps
1. Design and implement the database schema, including user and metadata tables.
2. Refactor endpoints as described.
3. Implement background job processing for content generation.
4. Update frontend to use new GET endpoints for content retrieval.
5. Add user registration, authentication, and profile management features. 