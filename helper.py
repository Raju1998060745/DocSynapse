import os
import json
def load_config():
    file_name = "config.json"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, file_name)
    try:
        with open(config_path, "r") as file:
           return  json.load(file)
    except FileNotFoundError:
        print(f"Error: The file {config_path} was not found.")
        return{}
    except json.JSONDecodeError:
        print(f"Error: The file {config_path} is not a valid JSON file.")
        return{}
