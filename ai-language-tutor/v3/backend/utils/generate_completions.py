from openai import AsyncOpenAI, OpenAI
import asyncio
import json
from typing import AsyncIterator
from typing import Union, List, Dict
from dotenv import load_dotenv
import os
load_dotenv()

# Initialize the async client
client = AsyncOpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)

def process_input(data: Union[str, List[Dict[str, str]]]) -> Union[str, List[Dict[str, str]]]:
    """
    Processes input to either uppercase a string or modify the 'content' field
    of a list of dictionaries.
    """
    if isinstance(data, str):
        return data.strip()  # Ensures prompt is cleaned up (optional)

    elif isinstance(data, list):
        # Ensure each item in the list is a dictionary with a 'content' key
        return [
            {**item, "content": item["content"].strip()}  # Trims whitespace in 'content'
            for item in data if isinstance(item, dict) and "content" in item
        ]
    
    else:
        raise TypeError("Input must be a string or a list of dictionaries with a 'content' field")


async def get_completions(
    prompt: Union[str, List[Dict[str, str]]],
    instructions: str
) -> str:
    processed_prompt = process_input(prompt)  # Ensures the input format is correct

    if isinstance(processed_prompt, str):
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": processed_prompt}
        ]
    elif isinstance(processed_prompt, list):
        messages = [{"role": "system", "content": instructions}] + processed_prompt
    else:
        raise TypeError("Unexpected processed input type.")

    response = await client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages,
        response_format={"type": "json_object"}
    )

    output: str = response.choices[0].message.content
    return output
