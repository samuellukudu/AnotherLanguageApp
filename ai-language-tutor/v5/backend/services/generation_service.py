from backend.utils.generate_completions import get_completions
from backend.config import (
    language_metadata_extraction_prompt,
    flashcard_mode_instructions,
    exercise_mode_instructions,
    simulation_mode_instructions,
)
from supabase import Client
from backend.services.logging_service import buffered_log_query


async def extract_metadata_service(session: Client, user_id: int, query: str) -> str:
    # Only log if user exists (skip for anonymous or invalid IDs)
    if user_id and user_id > 0:
        await buffered_log_query(session, user_id, 'metadata', query)
    return await get_completions(query, language_metadata_extraction_prompt)


async def generate_flashcards_service(session: Client, user_id: int, query: str) -> str:
    if user_id and user_id > 0:
        await buffered_log_query(session, user_id, 'flashcards', query)
    return await get_completions(query, flashcard_mode_instructions)


async def generate_exercises_service(session: Client, user_id: int, query: str) -> str:
    if user_id and user_id > 0:
        await buffered_log_query(session, user_id, 'exercises', query)
    return await get_completions(query, exercise_mode_instructions)


async def generate_simulation_service(session: Client, user_id: int, query: str) -> str:
    if user_id and user_id > 0:
        await buffered_log_query(session, user_id, 'simulation', query)
    return await get_completions(query, simulation_mode_instructions)
