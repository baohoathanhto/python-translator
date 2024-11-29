import os
import json
import re
import threading
import pygame
import io
import gtts
import pydub

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# Construct the relative path to config.json
CONFIG_FILE_PATH = os.path.join(SCRIPT_DIR, "config.json")

# Global variables with "z_" prefix
z_is_speaking = False
z_audio_buffer = None
z_speech_thread = None

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

# Function to clean unwanted characters from the text
def clean_text(text):
    # Remove unwanted characters using regex
    text = re.sub(r'[<>-]+', '', text)  # Remove <, >, -, and multiple dashes
    text = re.sub(r'[^\w\s,.!?\'"()@#&$%^*+=\x00-\x7F]', '', text)  # Keep only letters, digits, and common punctuation
    return text

# Function to start speech
def start_speech(text, lang="en", pitch_semitones=0):
    global z_is_speaking, z_speech_thread
    z_is_speaking = True

    # Split the text into chunks by lines
    chunks = text.splitlines()

    # Create a separate thread for each chunk
    def speak_chunks():
        pygame.mixer.init()  # Initialize pygame mixer here, before starting speech
        for chunk in chunks:
            if not z_is_speaking:
                break
            gtts_speak_chunk(chunk, lang, pitch_semitones)

        stop_speech()  # Stop once all chunks are spoken

    # Run speech playback in a separate thread immediately
    z_speech_thread = threading.Thread(target=speak_chunks)
    z_speech_thread.daemon = True  # Allow thread to exit when main program exits
    z_speech_thread.start()

# Stop speech function
def stop_speech():
    global z_is_speaking
    z_is_speaking = False

    # Stop pygame mixer if initialized
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()

# Function to handle chunked speech
def gtts_speak_chunk(text, lang="en", pitch_semitones=0):
    global z_is_speaking, z_audio_buffer

    # Preprocess the text to remove unwanted characters
    cleaned_text = clean_text(text)

    # Check if cleaned text is empty, if so return early
    if not cleaned_text.strip():
        return

    try:
        # Create gTTS object
        tts = gtts.gTTS(text=cleaned_text, lang=lang)
        z_audio_buffer = io.BytesIO()
        tts.write_to_fp(z_audio_buffer)
        z_audio_buffer.seek(0)

        # Convert the audio buffer to a pydub AudioSegment
        audio_segment = pydub.AudioSegment.from_mp3(z_audio_buffer)

        # Apply pitch change
        if pitch_semitones != 0:
            audio_segment = pitch_shift(audio_segment, pitch_semitones)

        # Save the modified audio back to a buffer
        z_audio_buffer = io.BytesIO()
        audio_segment.export(z_audio_buffer, format="mp3")
        z_audio_buffer.seek(0)

        # Load and play audio from buffer
        pygame.mixer.music.load(z_audio_buffer, "mp3")
        pygame.mixer.music.play()

        # Wait for the current speech to finish before playing the next one
        while pygame.mixer.music.get_busy():
            if not z_is_speaking:
                break

    except Exception as e:
        print(f"Error: {e}")
        stop_speech()

# Function to change the pitch of an audio segment
def pitch_shift(audio_segment, pitch_semitones):
    # Calculate the new frame rate based on the pitch shift
    # 12 semitones is one octave, so 1 semitone is 2^(1/12)
    factor = 2 ** (pitch_semitones / 12)
    
    # Change the frame rate (sample rate) to shift the pitch
    new_frame_rate = int(audio_segment.frame_rate * factor)
    
    # Apply the pitch shift by setting the new frame rate
    shifted_audio = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_frame_rate})
    
    # Return the pitch-shifted audio
    return shifted_audio