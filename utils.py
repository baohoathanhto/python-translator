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

def save_config(key, name, config_file_path=CONFIG_FILE_PATH):
    try:
        # Load existing JSON data
        with open(config_file_path, "r") as config_file:
            config_data = json.load(config_file)

        # Update the key
        config_data[key] = name

        with open(config_file_path, "w") as config_file:
            json.dump(config_data, config_file, indent=4)
    except Exception as e:
        print("Error saving config:", e)

def load_config(key, config_file_path=CONFIG_FILE_PATH):
    try:
        with open(config_file_path, "r") as config_file:
            config_data = json.load(config_file)
            saved_config = config_data.get(key, "default")
            return saved_config
    except Exception as e:
        print("Error loading config:", e)
        return "default"

def generate_percent(_min, _max, step):
    values = []
    for i in range(_min, _max + 1, step):
        values.append(str(i) + '%')
    return values

def percent_to_float(percent_str):
    # Remove '%' character from the string and convert it to float
    percent_float = float(percent_str.rstrip('%')) / 100
    return percent_float

def dict_remove_duplicates(data, colname):
    seen = set()
    unique_data = []
    
    for row in data:
        value = row[colname]  # Use the colname variable to get the value
        if value not in seen:
            unique_data.append(row)
            seen.add(value)
    
    return unique_data

def dict_get_first_value(data, colname, delimiter='/'):
    for row in data:
        # Split the colname value at the first delimiter and take the first part
        row[colname] = row[colname].split(delimiter)[0]
    return data