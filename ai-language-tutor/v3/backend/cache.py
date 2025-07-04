import asyncio
from typing import Any, Callable, Tuple
from collections import OrderedDict
import json

class AsyncLRUCache:
    def __init__(self, maxsize=100_000):  # Optimized for 16GB RAM
        self.cache = OrderedDict()
        self.maxsize = maxsize
        self.lock = asyncio.Lock()

    def _serialize_key(self, key: Tuple) -> str:
        # Serialize each element in the tuple for robust, unique keys
        return json.dumps(key, sort_keys=True, default=str)

    async def get_or_set(self, key: Tuple, coro: Callable, *args, **kwargs):
        skey = self._serialize_key(key)
        async with self.lock:
            if skey in self.cache:
                self.cache.move_to_end(skey)
                return self.cache[skey]
        # Not cached, compute result
        result = await coro(*args, **kwargs)
        async with self.lock:
            self.cache[skey] = result
            self.cache.move_to_end(skey)
            if len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)
        return result

# Initialize cache with optimized size for 16GB RAM
cache = AsyncLRUCache()  # Uses default maxsize=100_000 