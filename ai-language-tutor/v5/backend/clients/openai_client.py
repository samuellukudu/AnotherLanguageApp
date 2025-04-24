import os
from backend.settings import settings
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url=settings.base_url,
    api_key=settings.api_key,
)
