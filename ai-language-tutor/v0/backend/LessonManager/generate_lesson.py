import json
from openai import OpenAI
from backend.config import config
from backend.db_manager.db_manager import DatabaseManager

client = OpenAI(
    api_key=config.get('api_key'),
    base_url=config.get('base_url'),
)

def get_completion(prompt: str, curriculum_id: int = None, week_number: int = None):
    if not curriculum_id or week_number is None:
        raise ValueError("curriculum_id and week_number are required")

    response = client.chat.completions.create(
        model=config.get('model'),
        messages=[
            {"role": "system", "content": config.get('lesson_instruction')},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )

    try:
        data = json.loads(response.choices[0].message.content)
        db = DatabaseManager()
        
        # Save lesson to database
        lesson_id = db.save_lesson(curriculum_id, week_number, data)
        
        # Add lesson_id to response data
        data['lesson_id'] = lesson_id
        
        return data
            
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
