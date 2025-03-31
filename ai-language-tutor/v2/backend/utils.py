import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
)

async def get_completion(prompt: str, instruction: str) -> str:
    response = await client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content