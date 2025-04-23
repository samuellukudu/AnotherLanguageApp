from supabase import Client
from backend.db.supabase_client import supabase as client
import logging

# User operations
async def get_user(session: Client, user_id: int) -> dict | None:
    res = session.table("users").select("*").eq("user_id", user_id).limit(1).execute()
    data = getattr(res, 'data', None)
    if data:
        return data[0]
    return None

async def create_user(session: Client, username: str, email: str, password_hash: str) -> dict:
    """Insert new user and return created record."""
    payload = {"username": username, "email": email, "password_hash": password_hash}
    try:
        res = session.table("users").insert(payload).execute()
        logging.info(f"create_user response status: {getattr(res,'status_code',None)}, data: {getattr(res,'data',None)}")
        data = getattr(res, 'data', None)
        if not data:
            raise Exception(f"create_user: no data returned, status: {getattr(res,'status_code',None)}")
        return data[0] if isinstance(data, list) else data
    except Exception as e:
        logging.error(f"create_user exception: {e}, full response: {res if 'res' in locals() else None}")
        raise

async def get_user_by_username(session: Client, username: str) -> dict | None:
    res = session.table("users").select("*").eq("username", username).limit(1).execute()
    data = getattr(res, 'data', None)
    if data:
        return data[0]
    return None

async def get_user_by_email(session: Client, email: str) -> dict | None:
    """Fetch user by email for social login."""
    res = session.table("users").select("*").eq("email", email).limit(1).execute()
    data = getattr(res, 'data', None)
    if data:
        return data[0]
    return None

# Flashcards
async def create_flashcard_set(session: Client, user_id: int, query: str, flashcards_json: dict) -> dict:
    payload = {"user_id": user_id, "query": query, "flashcards": flashcards_json}
    res = session.table("flashcard_sets").insert(payload).execute()
    return res.data

# Exercises
async def create_exercise_set(session: Client, user_id: int, query: str, exercises_json: dict) -> dict:
    payload = {"user_id": user_id, "query": query, "exercises": exercises_json}
    res = session.table("exercise_sets").insert(payload).execute()
    return res.data

# Simulations
async def create_simulation(session: Client, user_id: int, query: str, scenario: str, dialog_json: dict) -> dict:
    payload = {"user_id": user_id, "query": query, "scenario": scenario, "dialog": dialog_json}
    res = session.table("simulations").insert(payload).execute()
    return res.data

# Query logging
async def create_query_log(session: Client, user_id: int, query_type: str, query: str) -> dict:
    """Log each user query without storing output."""
    payload = {"user_id": user_id, "query_type": query_type, "query": query}
    res = session.table("query_logs").insert(payload).execute()
    return res.data

async def bulk_insert_query_logs(session: Client, records: list[dict]) -> list[dict]:
    """Bulk insert query logs to DB."""
    if not records:
        return []
    res = session.table("query_logs").insert(records).execute()
    return getattr(res, 'data', [])
