import tkinter as tk
import os
import json

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# Construct the relative path to config.json
CONFIG_FILE_PATH = os.path.join(SCRIPT_DIR, "config.json")

def save_last_used_folders(input_folder, output_folder, config_file_path=CONFIG_FILE_PATH):
    if not input_folder or not output_folder:
        # Don't save if input_folder or output_folder is empty
        return
    try:
        # Load existing JSON data
        with open(config_file_path, "r") as config_file:
            config_data = json.load(config_file)

        # Update the input_folder & output_folder keys
        config_data["input_folder"] = input_folder
        config_data["output_folder"] = output_folder

        with open(config_file_path, 'w') as config_file:
            json.dump(config_data, config_file, indent=4)
    except Exception as e:
        print("Error saving config:", e)

def load_last_used_folders(config_file_path=CONFIG_FILE_PATH):
    input_folder = ""
    output_folder = ""
    try:
        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)
            input_folder = config.get('input_folder', '')
            output_folder = config.get('output_folder', '')
    except Exception as e:
        print("Error loading config:", e)
    return input_folder, output_folder

def save_theme(theme_key, theme_name, config_file_path=CONFIG_FILE_PATH):
    try:
        # Load existing JSON data
        with open(config_file_path, "r") as config_file:
            config_data = json.load(config_file)

        # Update the theme key
        config_data[theme_key] = theme_name

        with open(config_file_path, "w") as config_file:
            json.dump(config_data, config_file, indent=4)
    except Exception as e:
        print("Error saving theme:", e)

def load_theme(theme_key, config_file_path=CONFIG_FILE_PATH):
    try:
        with open(config_file_path, "r") as config_file:
            config_data = json.load(config_file)
            saved_theme = config_data.get(theme_key, "default")
            return saved_theme
    except Exception as e:
        print("Error loading theme:", e)
        return "default"

def load_config(config_file_path=CONFIG_FILE_PATH):
    with open(config_file_path, "r") as config_file:
        return json.load(config_file)