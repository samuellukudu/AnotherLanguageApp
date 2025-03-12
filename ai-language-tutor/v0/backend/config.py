from dotenv import load_dotenv
from backend.config_manager import Config
from backend.utils import ensure_directory
import os

load_dotenv()

# Set up base paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(PROJECT_ROOT, "backend")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

# Ensure directories exist
ensure_directory(CONFIG_DIR)
ensure_directory(OUTPUT_DIR)

config_path = os.path.join(CONFIG_DIR, "config.json")
config = Config(config_path)

# Default values - update API key handling
API_KEY = os.getenv('OPENAI_API_KEY') or os.getenv('GEMINI_API_KEY')
if not API_KEY:
    raise ValueError("No API key found. Please set OPENAI_API_KEY or GEMINI_API_KEY environment variable")

MODEL = "gemini-1.5-flash-8b"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

CURRICULUM_INSTRUCTION = """
You are an expert AI language learning curriculum designer. Your task is to create a one-month intensive language learning curriculum tailored to user's specific learning objectives and preferences. The curriculum should be divided into four weeks, with each week building upon the previous one.

**Curriculum Design Principles:**

1.  **AI-Driven:** The curriculum leverages AI for personalized learning experiences.
2.  **Intensive:** The curriculum should be designed for significant weekly study time.
3.  **Structured:** The curriculum should be divided into four weeks, with each week building upon the previous one.
4.  **Comprehensive:** Include a variety of learning activities, such as vocabulary building, grammar study, reading, writing, listening, and speaking practice.
5.  **Personalized:** Adapt the curriculum to the user's learning goals, current level, and interests.
6.  **Measurable:** Suggest ways the user can track their progress.
7.  **Output Format:** Provide the curriculum in a valid JSON format.
8.  **Weekly Content:** Instead of daily content, focus on providing a theme and a set of activities for each week. Include the approximate time the user should invest in that week.

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
          "description": "activity_description"
        },
        {
          "type": "activity_type",
          "description": "activity_description"
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
          "description": "activity_description"
        },
        ...
      ]
    },
    ...
  ]
}
"""

# Export CURRICULUM_INSTRUCTION
__all__ = ['config', 'CURRICULUM_INSTRUCTION']

# Initialize config with default values if not exists
if not config.data:
    config.set("curriculum_instruction", CURRICULUM_INSTRUCTION)
    config.set("model", MODEL)
    config.set("base_url", BASE_URL)
    config.set("api_key", API_KEY)
    config.save()