import json
import os
from openai import OpenAI
from backend.config import config, CURRICULUM_INSTRUCTION
from backend.utils import write_json_file, ensure_directory

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
output_dir = os.path.join(PROJECT_ROOT, "output")
ensure_directory(output_dir)

client = OpenAI(
    api_key=config.get('api_key'),
    base_url=config.get('base_url'),
)

def get_completion(prompt: str):
    response = client.chat.completions.create(
        model=config.get('model'),
        messages=[
            {"role": "system", "content": CURRICULUM_INSTRUCTION},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )

    try:
        data = json.loads(response.choices[0].message.content)
        filename = os.path.join(output_dir, "curriculum.json")
        
        if write_json_file(filename, data):
            print(f"JSON data saved to {filename}")
            # Reset the config when new curriculum is generated
            config.set("current_week", 0)
            config.save()
            return data  # Return the data instead of True
        print("Failed to save data")
        return None
            
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
