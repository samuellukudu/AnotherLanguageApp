import json
import os
from backend.CurriculumManager import generate_curriculum

with open("/home/samu2505/AnotherLanguageApp/ai-language-tutor/v0/backend/config.json", "r") as f:
    config = json.load(f)

DATA_PATH = "/home/samu2505/AnotherLanguageApp/ai-language-tutor/v0/output/curriculum.json"

def load_curriculum(file_path):
    """Loads the curriculum data from the specified JSON file.

    Args:
        file_path (str): The path to the curriculum JSON file.

    Returns:
        dict or None: The curriculum data as a Python dictionary,
                      or None if there was an error.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print(f"Error: Curriculum file not found at {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in curriculum file at {file_path}")
        return None

curriculum_data = load_curriculum(DATA_PATH)

weekly_data = curriculum_data["weeks"]

LessonInstuction = weekly_data[0]



# if __name__ == "__main__":
#     prompt = """
#     I would like to improve my chinese so as i can talk to investors. 

#     I can communicate with people about daily stuff and i would consider myself as an intermediate chinese learner
#     """
#     generate_curriculum.get_completion(prompt)
#     # config.user_input = prompt
#     config.update({"user_input": prompt})