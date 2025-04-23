import json, logging, asyncio
import aioredis
from backend.db.repositories import bulk_insert_query_logs
from backend.settings import REDIS_URL, QUERY_LOG_FLUSH_INTERVAL_SECONDS

# Global Redis client
redis = aioredis.from_url(REDIS_URL)

# Key templates per user
BUFFER_KEY_TMPL = "query_logs_buffer:{user_id}"
COUNT_KEY_TMPL = "query_logs_count:{user_id}"
BATCH_SIZE = 100
INITIAL_KEY_TMPL = "query_logs_initial:{user_id}"

async def buffered_log_query(session, user_id: int, query_type: str, query: str):
    if not user_id or user_id <= 0:
        return
    record = {"user_id": user_id, "query_type": query_type, "query": query}
    init_key = INITIAL_KEY_TMPL.format(user_id=user_id)
    # First log: write immediately
    first_logged = await redis.get(init_key)
    if not first_logged:
        try:
            await bulk_insert_query_logs(session, [record])
            logging.info(f"Stored first log for user {user_id}")
            await redis.set(init_key, 1)
        except Exception as e:
            logging.error(f"Error storing first log for user {user_id}: {e}")
        return
    buff_key = BUFFER_KEY_TMPL.format(user_id=user_id)
    count_key = COUNT_KEY_TMPL.format(user_id=user_id)
    # Buffer record
    await redis.lpush(buff_key, json.dumps(record))
    count = await redis.incr(count_key)
    if count >= BATCH_SIZE:
        await flush_buffered_logs(session, user_id)

async def flush_buffered_logs(session, user_id: int):
    buff_key = BUFFER_KEY_TMPL.format(user_id=user_id)
    count_key = COUNT_KEY_TMPL.format(user_id=user_id)
    items = await redis.lrange(buff_key, 0, -1)
    if not items:
        return
    # Decode bytes to str
    records = [json.loads(item.decode() if isinstance(item, bytes) else item) for item in items]
    try:
        await bulk_insert_query_logs(session, records)
        logging.info(f"Flushed {len(records)} logs for user {user_id}")
    except Exception as e:
        logging.error(f"Error flushing logs for user {user_id}: {e}")
    finally:
        await redis.delete(buff_key)
        await redis.set(count_key, 0)

async def flush_all_buffered_logs(session):
    keys = await redis.keys("query_logs_buffer:*")
    for key in keys:
        uid = int(key.decode().split(":")[1])
        await flush_buffered_logs(session, uid)

async def periodic_flush_task(session):
    while True:
        await asyncio.sleep(QUERY_LOG_FLUSH_INTERVAL_SECONDS)
        await flush_all_buffered_logs(session)
