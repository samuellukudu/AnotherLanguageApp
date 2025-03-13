import os
import argparse
from backend.CurriculumManager.generate_curriculum import get_completion as generate_curriculum
from backend.LessonManager.generate_lesson import get_completion as generate_lesson
from backend.LessonManager.generate_daily_lesson import get_completion as generate_daily_lesson
from backend.config_manager import Config
from backend.utils import read_json_file, ensure_directory

# Set up paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "backend", "config.json")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
CURRICULUM_PATH = os.path.join(OUTPUT_DIR, "curriculum.json")
LESSON_PATH = os.path.join(OUTPUT_DIR, "lesson.json")

# Ensure output directory exists
ensure_directory(OUTPUT_DIR)

config = Config(CONFIG_PATH)

def setup_lesson_instruction():
    """Setup lesson instruction from curriculum data"""
    curriculum_data = read_json_file(CURRICULUM_PATH)
    if curriculum_data is None:
        raise FileNotFoundError("Curriculum file not found. Please generate curriculum first.")

    language = curriculum_data["language"]
    learning_goal = curriculum_data["learning_goal"]
    current_level = curriculum_data["current_level"]
    week = curriculum_data["weeks"][0]  # Using first week by default

    lesson_instruction = """
    You are an advanced AI language tutor specializing in personalized language instruction. Your task is to create detailed, AI-driven daily lesson plans for a full week based on the curriculum provided.

    Student Profile:
    - Target Language: {language}
    - Learning Goal: {learning_goal}
    - Current Level: {current_level}

    Instructions:
    1. Create engaging, AI-driven activities for each day of the week (7 days)
    2. Focus on interactive, personalized learning experiences
    3. Avoid suggesting external resources or tools
    4. Ensure activities align with the week's theme and learning objectives
    5. Include specific examples and practice scenarios for each day
    6. Format your response as a valid JSON object

    Output Format:
    {{
        "week": number,
        "theme": "string",
        "estimated_duration": "string",
        "daily_lessons": [
            {{
                "day": number,
                "focus": "string",
                "duration": "string",
                "activities": [
                    {{
                        "type": "string",
                        "description": "string"
                    }}
                ]
            }},
            // Repeat for all 7 days
        ]
    }}

    Notes:
    - Create lessons for all 7 days of the week
    - Each day should have a specific focus while maintaining the week's theme
    - Weekend lessons (days 6-7) can be lighter but should maintain learning momentum
    - All activities should be completable through AI interaction
    """.format(
        language=language,
        learning_goal=learning_goal,
        current_level=current_level
    )

    lesson_prompt = """
    Based on the curriculum week:
    {curriculum}

    Generate a detailed, AI-driven lesson plan following the instruction format.
    """.format(curriculum=week)

    config.set("target_language", language)
    config.set("lesson_instruction", lesson_instruction)
    config.set("lesson_prompt", lesson_prompt)
    return True

setup_lesson_instruction()
# generate_lesson(config.get("lesson_prompt"))

lesson_data = read_json_file(LESSON_PATH)
theme = lesson_data["theme"]
lessons = lesson_data["daily_lessons"]
# print("Theme:", theme)
# print("Lessons: ", lessons[0])

daily_lesson_instruction = """
You are an AI assistant tasked with curating today's lesson to help the user improve their skills in the target language.

Instructions:
1. Determine the target language based on the user's input.
2. Create a bilingual lesson (English and the target language) to enable the user to achieve their learning goal.
3. For vocabulary sections:
   - Provide terms in English, their translations in the target language, and example sentences in both languages.
   - For character-based languages (e.g., Chinese, Japanese, Korean, Arabic), include phonetic aids alongside the target language:
     - Chinese: Include Pinyin for Mandarin terms.
     - Japanese: Include Romaji for Japanese terms.
     - Korean: Include Romanized Korean (Revised Romanization).
     - Arabic: Include transliteration using the Latin alphabet.
   - Example format:
     - Term: "prototype"
     - Translation: "原型" (Chinese), Pinyin: "yuánxíng"
     - Example Sentence: 
       - English: "We've developed a prototype for the new app."
       - Target Language: "我们为新应用开发了一个原型。" (Chinese), Pinyin: "Wǒmen wèi xīn yìngyòng kāifāle yígè yuánxíng."
4. For practice activities:
   - Include prompts in both English and the target language.
   - Provide example responses in both languages, including phonetic aids for character-based languages.
5. Provide feedback on the user's input, focusing on grammar, vocabulary, and fluency. If applicable, include corrections with phonetic aids.
6. Always remember to include both English and the target language for all cases, along with phonetic aids for character-based languages.

The lesson should be engaging, interactive, and tailored to the user's proficiency level.
"""

lesson_prompt = """
Theme: {theme}

Based on today's lesson plan, create a bilingual lesson (English and {target_language}) with the following structure:

Lesson Plan: {lesson_plan}
""".format(theme=theme, target_language=config.get("target_language"), lesson_plan=lessons[0])

config.set("daily_lesson_instruction", daily_lesson_instruction)
config.set("daily_lesson_prompt", lesson_prompt)

# print(config.get("daily_lesson_instruction"))
# print(config.get("daily_lesson_prompt"))
generate_daily_lesson(lesson_prompt)
# generate_lesson(config.get("daily_lesson_prompt"))