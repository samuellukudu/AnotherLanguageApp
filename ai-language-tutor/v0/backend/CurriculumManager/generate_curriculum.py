import json
import os
from openai import OpenAI

with open("/home/samu2505/AnotherLanguageApp/ai-language-tutor/v0/backend/config.json", "r") as f:
    config = json.load(f)

client = OpenAI(
    api_key=config['api_key'],
    base_url=config['base_url'],
)

def get_completion(prompt: str):
    response = client.chat.completions.create(
        model=config['model'],
        messages=[
            {"role": "system", "content": config['system_instruction']},
            {"role": "user", "content": prompt},
        ],
        # max_tokens=512,
        response_format={"type": "json_object"},
    )

    data = None
    try:
        # Now we are parsing the string into a dictionary
        data = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        data = None
        
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{output_dir}/curriculum.json"
    if data is not None:
      with open(filename, "w", encoding="utf-8") as f:
          # Now save the dictionary into the json file
          json.dump(data, f, ensure_ascii=False, indent=4)
      print(f"JSON data saved to {filename}")
    else:
      print("No data to save")
