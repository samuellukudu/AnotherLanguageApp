import json
import os


class Config:
    def __init__(self, file_path="config.json"):
        self.file_path = file_path
        self.data = {}
        self.load()

    def load(self):
        """Loads the configuration data from the JSON file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            print(f"Config file not found at {self.file_path}. Creating a new one.")
            self.data = {}  # Start with an empty config
            self.save()
        except json.JSONDecodeError:
            print(
                f"Error: Invalid JSON format in config file at {self.file_path}. Creating a new one"
            )
            self.data = {}
            self.save()

    def save(self):
        """Saves the configuration data to the JSON file."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def get(self, key, default=None):
        """Gets a configuration value by key.

        Args:
            key (str): The key to look up.
            default: The default value to return if the key is not found.

        Returns:
            The configuration value or the default.
        """
        return self.data.get(key, default)

    def set(self, key, value):
        """Sets a configuration value.

        Args:
            key (str): The key to set.
            value: The value to set.
        """
        self.data[key] = value
        self.save()

    def update(self, new_data):
        """Updates the config data with a new dict

        Args:
            new_data: The data to update
        """
        self.data.update(new_data)
        self.save()

    def delete(self, key):
        """Deletes a key from the config

        Args:
            key (str): the key to delete
        """
        if key in self.data:
            del self.data[key]
        self.save()
