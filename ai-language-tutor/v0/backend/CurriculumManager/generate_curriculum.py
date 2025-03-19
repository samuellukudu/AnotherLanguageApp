import json
from openai import OpenAI
from backend.config import config, CURRICULUM_INSTRUCTION
from backend.db_manager.db_manager import DatabaseManager

client = OpenAI(
    api_key=config.get('api_key'),
    base_url=config.get('base_url'),
)

def get_completion(prompt: str, user_id: str = None):
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
        db = DatabaseManager()
        
        # Save curriculum to database (user_id is now optional)
        curriculum_id = db.save_curriculum(None, prompt, data)
        
        # Add curriculum_id to response data
        data['curriculum_id'] = curriculum_id
        
        # Reset the config when new curriculum is generated
        config.set("current_week", 0)
        config.save()
        
        return data
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
