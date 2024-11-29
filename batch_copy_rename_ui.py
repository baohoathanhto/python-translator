import os
import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import filedialog
import utils
import shutil

def select_input_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        input_folder_entry.delete(0, tk.END)
        input_folder_entry.insert(0, folder_path)

def select_output_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        output_folder_entry.delete(0, tk.END)
        output_folder_entry.insert(0, folder_path)

def batch_copy_rename():
    input_folder = input_folder_entry.get()
    output_folder = output_folder_entry.get()

    if not os.path.exists(input_folder) or not os.path.exists(output_folder):
        tk.messagebox.showerror("Error", "Please select both input and output folders.")
        return

    utils.save_last_used_folders(input_folder, output_folder, )

    # Load configuration from JSON file
    config = utils.load_config()
    
    # Iterate over each key-value pair in the configuration
    for old_name, new_name in config["data_names"].items():
        old_name_path = os.path.join(input_folder, old_name)
        new_name_path = os.path.join(output_folder, new_name)
        # Check if the old file exists
        if os.path.exists(old_name_path):
            # Copy the file to the new destination
            shutil.copy2(old_name_path, new_name_path)
            print(f"Copied & renamed '{old_name}' to '{new_name}'")
        else:
            print(f"File '{old_name}' not found, skipping.")

# GUI setup
root = tk.Tk()
root.title("Batch copy & rename files")

input_dir, output_dir = utils.load_last_used_folders()

# Input folder selection
input_folder_label = ttkb.Label(root, text="Input Folder:")
input_folder_entry = ttkb.Entry(root, width=50)
input_folder_button = ttkb.Button(root, text="Browse", command=select_input_folder)
input_folder_entry.insert(0, input_dir)

# Output folder selection
output_folder_label = ttkb.Label(root, text="Output Folder:")
output_folder_entry = ttkb.Entry(root, width=50)
output_folder_button = ttkb.Button(root, text="Browse", command=select_output_folder)
output_folder_entry.insert(0, output_dir)

# Rename button
rename_button = ttkb.Button(root, text="Batch Copy & Rename", command=batch_copy_rename)

# Setup layot
input_folder_label.grid(row=0, column=0, padx=(10, 5), pady=(10, 5), sticky="e")
input_folder_entry.grid(row=0, column=1, padx=(5, 5), pady=(10, 5), sticky="we")
input_folder_button.grid(row=0, column=2, padx=(5, 10), pady=(10, 5), sticky="w")
output_folder_label.grid(row=1, column=0, padx=(10, 5), pady=(5, 5), sticky="e")
output_folder_entry.grid(row=1, column=1, padx=(5, 5), pady=(5, 5), sticky="we")
output_folder_button.grid(row=1, column=2, padx=(5, 10), pady=(5, 5), sticky="w")
rename_button.grid(row=2, column=0, columnspan=3, pady=(5, 10))

root.mainloop()
