import tkinter as tk
from tkinter import ttk

class TranslatorUI:
    def __init__(self, translate_callback):
        self.root = tk.Tk()
        self.root.title("Zero-Translator")
        
        # Maximize the window
        self.root.wm_state('zoomed')

        # Function to toggle fullscreen mode (optional)
        def toggle_fullscreen(event=None):
            self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

        # Bind F11 key to toggle fullscreen mode (optional)
        self.root.bind("<F11>", toggle_fullscreen)

        # Set translate() callback
        self.translate_callback = translate_callback
        
        # Customize the appearance of the tabs
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Tahoma", 12, "bold"), padding=[10, 2])
        self.tabControl = ttk.Notebook(self.root, style='Custom.TNotebook')
        
        
        self.chinese_tab = ttk.Frame(self.tabControl)
        self.hanviet_tab = ttk.Frame(self.tabControl)
        self.vietnamese_tab = ttk.Frame(self.tabControl)

        self.tabControl.add(self.chinese_tab, text='Tiếng Trung')
        self.tabControl.add(self.hanviet_tab, text='Hán Việt')
        self.tabControl.add(self.vietnamese_tab, text='Tiếng Việt')
        
        # Create textboxes inside tabs
        self.chinese_textbox = tk.Text(self.chinese_tab, height=10, width=40, padx=10, pady=10, spacing1=5, spacing2=5)
        self.hanviet_textbox = tk.Text(self.hanviet_tab, height=10, width=40, padx=10, pady=10, spacing1=5, spacing2=5)
        self.vietnamese_textbox = tk.Text(self.vietnamese_tab, height=10, width=40, padx=10, pady=10, spacing1=5, spacing2=5)
             
        # Set font and size for textboxes
        self.chinese_textbox.config(font=('Tahoma', 12))
        self.hanviet_textbox.config(font=('Tahoma', 12))
        self.vietnamese_textbox.config(font=('Tahoma', 12))
        
        # Bind Ctrl+V to process clipboard text for each text box
        self.chinese_textbox.bind("<Control-v>", self.process_and_paste_clipboard)
        self.hanviet_textbox.bind("<Control-v>", self.process_and_paste_clipboard)
        self.vietnamese_textbox.bind("<Control-v>", self.process_and_paste_clipboard)
        
        # Create Translate button
        self.button_bg_color = "#007bff"
        self.button_fg_color = "white"
        self.button_font = ("Tahoma", 12, "bold")
        self.button_borderwidth = 0

        self.translate_button = tk.Button(self.root, text="Translate", command=self.translate, bg=self.button_bg_color, fg=self.button_fg_color, font=self.button_font, borderwidth=self.button_borderwidth)
        
        self.setup_layout()

    def setup_layout(self):
        self.tabControl.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.chinese_textbox.pack(fill="both", expand=True)
        self.hanviet_textbox.pack(fill="both", expand=True)
        self.vietnamese_textbox.pack(fill="both", expand=True)
        
        self.translate_button.pack(fill="x")
        
    def process_and_paste_clipboard(self, event=None):
        clipboard_text = self.root.clipboard_get()
        if '\n\n' not in clipboard_text:
            clipboard_text = clipboard_text.replace("\n", "\n\n")
        
            # Clear clipboard and copy processed text
            self.root.clipboard_clear()
            self.root.clipboard_append(clipboard_text)
        else:
            pass
        
    def translate(self):
        # Call the translate_callback function with textboxes
        self.translate_callback(self.chinese_textbox, self.hanviet_textbox, self.vietnamese_textbox)
        
        # Switch to the Vietnamese tab
        self.tabControl.select(self.vietnamese_tab)

    def run(self):
        self.root.mainloop()
