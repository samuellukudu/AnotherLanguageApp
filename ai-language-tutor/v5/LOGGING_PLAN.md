# Logging Fix Plan

We need to address inconsistent database logging and remove debug leaks.

## 1. Audit Logging Calls in Generation Services
- Ensure `buffered_log_query(session, user_id, type, data)` is invoked for both input _and_ output in:
  - `generate_flashcards_service`
  - `generate_exercises_service`
  - `generate_simulation_service`
- Compare with `extract_metadata_service` which logs correctly.

## 2. Simplify Buffered Logging Logic
- Bypass deduplication completely (already removed `bulk_insert_query_logs`).
- Confirm `create_query_log` is used for every record insert.
- Remove or disable `remove_duplicate_query_logs` at startup to avoid interfering.

## 3. Adjust Logging Levels
- Silence `aiocache` and `openai` debug logs:
  - In `backend/main.py`, set logger level to INFO or WARNING for these modules.
  - Optionally configure `logging.getLogger('aiocache').setLevel(logging.INFO)` and same for `openai`.

## 4. Update Startup Hooks
- Comment out or remove `remove_duplicate_query_logs(session)` in `main.py`.

## 5. Testing and Verification
- Create new test user, invoke `/generate/flashcards`, `/generate/exercises`, `/generate/simulation`, `/extract/metadata`.
- Query `query_logs` table to verify consistent entries for each call.
- Confirm debug logs no longer leak internal objects to console.
