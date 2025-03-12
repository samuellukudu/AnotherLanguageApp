import os
import argparse
from backend.CurriculumManager.generate_curriculum import get_completion as generate_curriculum
from backend.LessonManager.generate_lesson import get_completion as generate_lesson
from backend.config_manager import Config
from backend.utils import read_json_file, ensure_directory

# Set up paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "backend", "config.json")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
CURRICULUM_PATH = os.path.join(OUTPUT_DIR, "curriculum.json")

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

    config.set("lesson_instruction", lesson_instruction)
    config.set("lesson_prompt", lesson_prompt)
    return True

setup_lesson_instruction()
generate_lesson(config.get("lesson_prompt"))

# def test_curriculum_generation(user_prompt: str):
#     """Test curriculum generation with a user prompt"""
#     print("Generating curriculum...")
#     generate_curriculum(user_prompt)
#     print("Curriculum generation completed")

# def test_lesson_generation(user_prompt: str):
#     """Test lesson generation with a user prompt"""
#     try:
#         setup_lesson_instruction()
#         print("Generating lesson...")
#         generate_lesson(user_prompt)
#         print("Lesson generation completed")
#     except FileNotFoundError as e:
#         print(f"Error: {e}")
#         print("Please generate a curriculum first using --mode curriculum")

# def main():
#     parser = argparse.ArgumentParser(description='Language Learning App CLI')
#     parser.add_argument('--mode', choices=['curriculum', 'lesson'], required=True,
#                       help='Mode of operation: curriculum or lesson generation')
#     parser.add_argument('--prompt', type=str, required=True,
#                       help='User prompt for generation')

#     args = parser.parse_args()

#     if args.mode == 'curriculum':
#         test_curriculum_generation(args.prompt)
#     elif args.mode == 'lesson':
#         test_lesson_generation(args.prompt)

# if __name__ == "__main__":
#     main()