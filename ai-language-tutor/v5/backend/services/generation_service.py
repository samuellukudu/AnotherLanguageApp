from backend.utils.generate_completions import get_completions
from backend.config import (
    language_metadata_extraction_prompt,
    flashcard_mode_instructions,
    exercise_mode_instructions,
    simulation_mode_instructions,
)
from supabase import Client
from backend.services.logging_service import buffered_log_query
import json
from backend.db.repositories import create_flashcard_set, create_exercise_set, create_simulation
import logging


async def extract_metadata_service(session: Client, user_id: int, query: str) -> str:
    # Only log if user exists (skip for anonymous or invalid IDs)
    if user_id and user_id > 0:
        await buffered_log_query(session, user_id, 'metadata', query)
    return await get_completions(query, language_metadata_extraction_prompt)


async def generate_flashcards_service(session: Client, user_id: int, query: str) -> str:
    if user_id and user_id > 0:
        await buffered_log_query(session, user_id, 'flashcards', query)
    # Generate output
    output = await get_completions(query, flashcard_mode_instructions)
    if user_id and user_id > 0:
        # Store generated flashcards
        try:
            data = json.loads(output)
            await create_flashcard_set(session, user_id, query, data)
        except Exception as e:
            logging.error(f"Error storing flashcards for user {user_id}: {e}")
    return output


async def generate_exercises_service(session: Client, user_id: int, query: str) -> str:
    if user_id and user_id > 0:
        await buffered_log_query(session, user_id, 'exercises', query)
    # Generate output
    output = await get_completions(query, exercise_mode_instructions)
    if user_id and user_id > 0:
        # Store generated exercises
        try:
            data = json.loads(output)
            await create_exercise_set(session, user_id, query, data)
        except Exception as e:
            logging.error(f"Error storing exercises for user {user_id}: {e}")
    return output


async def generate_simulation_service(session: Client, user_id: int, query: str) -> str:
    if user_id and user_id > 0:
        await buffered_log_query(session, user_id, 'simulation', query)
    # Generate output
    output = await get_completions(query, simulation_mode_instructions)
    if user_id and user_id > 0:
        # Store generated simulation
        try:
            data = json.loads(output)
            scenario = data.get('setting', '')
            dialog = data.get('content', [])
            await create_simulation(session, user_id, query, scenario, dialog)
        except Exception as e:
            logging.error(f"Error storing simulation for user {user_id}: {e}")
    return output
