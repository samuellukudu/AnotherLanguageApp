import json
import os

def read_json_file(file_path: str) -> dict:
    """Reads and parses a JSON file.

    Args:
        file_path (str): Path to the JSON file

    Returns:
        dict: Parsed JSON data or None if there was an error
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file at {file_path}")
        return None

def write_json_file(file_path: str, data: dict, indent: int = 4) -> bool:
    """Writes data to a JSON file.

    Args:
        file_path (str): Path to save the JSON file
        data (dict): Data to write
        indent (int): Indentation level for pretty printing

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error writing to file {file_path}: {str(e)}")
        return False

def ensure_directory(directory_path: str) -> bool:
    """Ensures a directory exists, creates it if it doesn't.

    Args:
        directory_path (str): Path to the directory

    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {directory_path}: {str(e)}")
        return False
