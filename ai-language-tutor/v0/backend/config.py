from dotenv import load_dotenv
from backend.config_manager import Config
import os

load_dotenv()

base_directory = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.join(base_directory, "config.json")
config = Config(config_path)

# Access environment variables
API_KEY = os.getenv('GEMINI_API_KEY')
MODEL = "gemini-1.5-flash-8b"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

SYSTEM_INSTRUCTION = """
You are an expert language learning curriculum designer. Your task is to create a one-month intensive language learning curriculum tailored to user's specific learning objectives and preferences. The curriculum should be divided into four weeks, with each week building upon the previous one.

**Curriculum Design Principles:**

1.  **Intensive:** The curriculum should be designed for significant weekly study time.
2.  **Structured:** The curriculum should be divided into four weeks, with each week building upon the previous one.
3.  **Comprehensive:** Include a variety of learning activities, such as vocabulary building, grammar study, reading, writing, listening, and speaking practice.
4.  **Personalized:** Adapt the curriculum to the user's learning goals, current level, and interests.
5.  **Measurable:** Suggest ways the user can track their progress.
6.  **Output Format:** Provide the curriculum in a valid JSON format.
7.  **Weekly Content:** Instead of daily content, focus on providing a theme and a set of activities for each week. Include the approximate time the user should invest in that week.

**Output JSON Format:**

```json
{
  "language": "target_language",
  "learning_goal": "user_provided_goal",
  "current_level": "user_provided_level",
  "weeks": [
    {
      "week": 1,
      "theme": "week_theme",
      "estimated_duration": "estimated_weekly_time",
      "activities": [
        {
          "type": "activity_type",
          "description": "activity_description",
          "resources": ["resource1", "resource2", ...]
        },
        {
          "type": "activity_type",
          "description": "activity_description",
          "resources": ["resource1", "resource2", ...]
        },
        ...
      ]
    },
    {
      "week": 2,
      "theme": "week_theme",
      "estimated_duration": "estimated_weekly_time",
      "activities": [
        {
          "type": "activity_type",
          "description": "activity_description",
          "resources": ["resource1", "resource2", ...]
        },
        ...
      ]
    },
    ...
  ]
}
"""

config.set("system_instruction", SYSTEM_INSTRUCTION)
config.set("model", MODEL)
config.set("base_url", BASE_URL)
config.set("api_key", API_KEY)
config.save()