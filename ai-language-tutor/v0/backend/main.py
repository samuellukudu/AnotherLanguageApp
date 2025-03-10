import json
import os
from openai import OpenAI
from backend import config

client = OpenAI(
    api_key=config.API_KEY,
    base_url=config.BASE_URL,
)

def get_completion(prompt: str):
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[
            {"role": "system", "content": config.SYSTEM_INSTRUCTION},
            {"role": "user", "content": "I would like to improve my chinese so as i can talk to investors"},
        ],
        # max_tokens=512,
        response_format={"type": "json_object"},
    )

    data = None
    try:
        data = json.dumps(response.choices[0].message.content, indent=4)
    except Exception as e:
        print(f"Error decoding JSON: {e}")
        data = None
        
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{output_dir}/curriculum.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"JSON data saved to {filename}")

if __name__ == "__main__":
    prompt = """
    I would like to improve my chinese so as i can talk to investors. 

    I can communicate with people about daily stuff and i would consider myself as an intermediate chinese learner
    """
    get_completion(prompt)