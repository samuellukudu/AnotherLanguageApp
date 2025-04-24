import logging
from backend.db.repositories import create_query_log

async def buffered_log_query(session, user_id: int, query_type: str, query: str):
    """Directly log each query without deduplication."""
    if not user_id or user_id <= 0:
        return
    try:
        await create_query_log(session, user_id, query_type, query)
    except Exception as e:
        logging.error(f"Error logging query for user {user_id}: {e}")
