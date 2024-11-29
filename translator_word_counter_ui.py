import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import tkinter as tk
import utils

class WordCounter(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Word Counter")
        self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))

        self.font_name = parent.font_name_combobox.get()
        self.font_size = utils.percent_to_float(parent.font_size_combobox.get())
        self.ratio = parent.ratio

        # Get content from parent.vietnamese_textbox
        self.vietnamese_text = parent.vietnamese_textbox.get("1.0", tk.END)

        self.setup_gui()
        self.setup_fonts()
        self.init_textbox()

    def setup_gui(self):
        # Textbox for entering the paragraph (full screen)
        self.text_box = ttkb.Text(self, undo=True)  # Enable undo/redo functionality
        self.text_box.pack(expand=True, fill=BOTH, padx=10, pady=10)

        # Label to display the word count
        self.word_count_label = ttkb.Label(self, text="Word count: 0")
        self.word_count_label.pack(side=tk.LEFT, padx=10, pady=(10, 20))

        # Add button speak
        self.speak_button = ttkb.Button(self, bootstyle="light", text="Speak", command=self.toggle_speech)
        self.speak_button.pack(side=tk.RIGHT, padx=10, pady=(10, 20))

        # Bind text box content changes to the function
        self.text_box.bind("<KeyRelease>", self.count_words)

        # Bind Ctrl+A to select all text
        self.text_box.bind('<Control-a>', self.select_all)

        # Bind Ctrl+Z to undo
        self.text_box.bind('<Control-z>', self.undo_action)

        # Bind Ctrl+Y to redo
        self.text_box.bind('<Control-y>', self.redo_action)

    def setup_fonts(self):
        text_box_font = (self.font_name, int(self.font_size * 12 * self.ratio))
        word_count_label_font = (self.font_name, int(self.font_size * 10 * self.ratio))

        self.text_box.config(font=text_box_font)        
        self.word_count_label.config(font=word_count_label_font)

    def init_textbox(self):
        # Set the content from the parent text box
        self.text_box.insert(tk.END, self.vietnamese_text)

        # Count words after init text box
        self.count_words()

    def count_words(self, event=None):
        paragraph = self.text_box.get("1.0", tk.END)  # Get content from the textbox
        words = paragraph.split()
        word_count = len(words) if words else 0  # Check if words is empty
        self.word_count_label.config(text=f"Word count: {word_count}")

    def toggle_speech(self):
        if self.speak_button['text'] == "Speak":
            text = self.text_box.get("1.0", tk.END)
            utils.start_speech(text, lang="vi", pitch_semitones=3)  # Call start_speech with text and language
            self.speak_button.config(text="Cancel")   # Change button label to 'Cancel'
        else:
            utils.stop_speech()  # Call stop_speech to stop playback
            self.speak_button.config(text="Speak")  # Change button label back to 'Speak'

    def select_all(self, event=None):
        self.text_box.tag_add(tk.SEL, "1.0", tk.END)  # Select all text
        self.text_box.mark_set(tk.INSERT, "1.0")  # Move cursor to the beginning
        self.text_box.see(tk.INSERT)  # Ensure the cursor is visible
        return 'break'  # Prevent the default behavior of Ctrl+A
    
    def undo_action(self, event=None):
        try:
            self.text_box.edit_undo() # Try to perform undo
        except tk.TclError:
            pass  # Nothing to undo, so we just pass without any action
        return 'break'  # Prevent the default behavior of Ctrl+Z
        
    def redo_action(self, event=None):    
        try:
            self.text_box.edit_redo() # Try to perform redo
        except tk.TclError:
            pass  # Nothing to redo, so we just pass without any action
        return 'break'  # Prevent the default behavior of Ctrl+Y