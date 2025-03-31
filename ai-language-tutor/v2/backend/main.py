import asyncio  # <-- Import asyncio
from backend.utils import get_completion
from backend.config import CURRICULUM_INSTRUCTIONS

# Define an async function to hold the await call
async def main():
    query = "need to improve my chinese so as to propose to my girlfriend"
    print("Getting completion...") # Optional: Indicate progress
    try:
        response = await get_completion(prompt=query, instruction=CURRICULUM_INSTRUCTIONS)
        print("\nResponse:")
        print(response)
    except Exception as e:
        print(f"An error occurred: {e}") # Basic error handling

# Use asyncio.run() to execute the async main function
# The if __name__ == "__main__": block ensures this runs only when
# the script is executed directly (e.g., python -m backend.main)
if __name__ == "__main__":
    asyncio.run(main())