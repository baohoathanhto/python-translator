import tkinter as tk
from tkinter import ttk, font
import ttkbootstrap as ttkb
import translator
import utils
import translator_data_tables_ui
import translator_data_update_ui
import pyperclip
import re

class TranslatorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Python Translator")
        self.wm_state('zoomed')
        self.bind("<F11>", self.toggle_fullscreen)

        self.setup_style()
        self.setup_fonts()
        self.setup_gui()
        self.setup_bindings()
        
        self.z_selected_text = {
            'chinese': "",
            'hanviet': "",
            'vietnamese': ""
        }

        self.z_indexes = None

    def setup_style(self):
        self.style = ttkb.Style()
        self.saved_theme = utils.load_config("ttkb_theme")
        self.available_themes = self.style.theme_names()

        if self.saved_theme not in self.available_themes:
            self.saved_theme = self.available_themes[0]

        self.style.theme_use(self.saved_theme)

    def setup_fonts(self):
        # Set font and size for all widgets
        self.ratio = self.winfo_screenheight() / 720

        self.saved_font_name = utils.load_config("app_font_name")
        self.available_font_names = font.families()

        if self.saved_font_name not in self.available_font_names:
            self.saved_font_name = self.option_get("font", "TkDefaultFont")

        self.saved_font_size = utils.load_config("app_font_size")
        self.available_font_sizes = utils.generate_percent(50, 200, 10)

        if self.saved_font_size not in self.available_font_sizes:
            self.saved_font_size = "100%"

    def setup_gui(self):
        # Frame container
        self.frame_container = tk.Frame(self)
        self.frame_container.pack(fill=tk.BOTH, expand=True)

        # Frame for row 2
        self.frame_row2 = tk.Frame(self.frame_container)
        self.frame_row2.pack(side=tk.BOTTOM, fill=tk.BOTH)

        # Frame for row 1
        self.frame_row1 = tk.Frame(self.frame_container)
        self.frame_row1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Frame for column 1 inside frame row 1
        self.frame_col1_1 = tk.Frame(self.frame_row1)
        self.frame_col1_1.pack(side=tk.LEFT, fill=tk.BOTH)

        # Frame for column 2 inside frame row 1
        self.frame_col1_2 = tk.Frame(self.frame_row1)
        self.frame_col1_2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create textboxes inside frame column 1
        self.highlighted_textbox = ttkb.Text(self.frame_col1_1, width=40, height=2, spacing1=5, spacing2=5, wrap="word")
        self.meaning_textbox = ttkb.Text(self.frame_col1_1, width=40, spacing1=5, spacing2=5, wrap="word")

        # Create tabs inside frame column 2
        self.tab_control = ttkb.Notebook(self.frame_col1_2, bootstyle="secondary")

        self.chinese_tab = ttkb.Frame(self.tab_control)
        self.hanviet_tab = ttkb.Frame(self.tab_control)
        self.vietnamese_tab = ttkb.Frame(self.tab_control)

        self.tab_control.add(self.chinese_tab, text='Tiếng Trung')
        self.tab_control.add(self.hanviet_tab, text='Hán Việt')
        self.tab_control.add(self.vietnamese_tab, text='Tiếng Việt')

        # Create textboxes inside tabs
        self.chinese_textbox = ttkb.Text(self.chinese_tab, spacing1=5, spacing2=5, wrap="word", state="disabled")
        self.hanviet_textbox = ttkb.Text(self.hanviet_tab, spacing1=5, spacing2=5, wrap="word", state="disabled")
        self.vietnamese_textbox = ttkb.Text(self.vietnamese_tab, spacing1=5, spacing2=5, wrap="word", state="disabled")

        # Create button inside frame row 2
        self.translate_button = ttkb.Button(self.frame_row2, text="Translate from clipboard", command=self.translate)
        self.quick_translate_button = ttkb.Button(self.frame_row2, bootstyle="success", text="Quick translate", command=self.quick_translate)
        self.data_ui_button = ttkb.Button(self.frame_row2, bootstyle="dark", text="Show data", command=self.show_data_tables_ui)

        self.quick_translate_button.config(state=tk.DISABLED)
        self.data_ui_button.config(state=tk.DISABLED)

        # Create a combobox to choose theme inside frame row 2
        self.theme_label = ttkb.Label(self.frame_row2, text="Theme:")
        self.theme_combobox = ttkb.Combobox(self.frame_row2, values=sorted(self.available_themes))
        self.theme_combobox.current(self.theme_combobox["values"].index(self.saved_theme)) if self.saved_theme in self.theme_combobox["values"] else None

        # Create a combobox to choose font inside frame row 2
        self.font_label = ttkb.Label(self.frame_row2, text="Font:")
        self.font_name_combobox = ttkb.Combobox(self.frame_row2, values=sorted(self.available_font_names))
        self.font_name_combobox.current(self.font_name_combobox["values"].index(self.saved_font_name)) if self.saved_font_name in self.font_name_combobox["values"] else None
        self.font_size_combobox = ttkb.Combobox(self.frame_row2, values=self.available_font_sizes)
        self.font_size_combobox.current(self.font_size_combobox["values"].index(self.saved_font_size)) if self.saved_font_size in self.font_size_combobox["values"] else None

        # Setup layout
        self.highlighted_textbox.pack(fill=tk.BOTH, padx=(10, 5), pady=(10, 5))
        self.meaning_textbox.pack(fill=tk.BOTH, expand=True, padx=(10, 5), pady=(5, 5))
        
        self.tab_control.pack(fill=tk.BOTH, expand=True, padx=(5, 10), pady=(10, 5))
        self.chinese_textbox.pack(fill=tk.BOTH, expand=True)
        self.hanviet_textbox.pack(fill=tk.BOTH, expand=True)
        self.vietnamese_textbox.pack(fill=tk.BOTH, expand=True)
        
        self.translate_button.pack(side=tk.LEFT, padx=(10, 5), pady=(5, 10))
        self.quick_translate_button.pack(side=tk.LEFT, padx=5, pady=(5, 10))
        self.data_ui_button.pack(side=tk.LEFT, padx=5, pady=(5, 10))
        
        self.theme_combobox.pack(side=tk.RIGHT, padx=(5, 10), pady=(5, 10))
        self.theme_label.pack(side=tk.RIGHT, padx=(5, 5), pady=(5, 10))

        self.font_size_combobox.pack(side=tk.RIGHT, padx=(5, 5), pady=(5, 10))
        self.font_name_combobox.pack(side=tk.RIGHT, padx=(5, 5), pady=(5, 10))
        self.font_label.pack(side=tk.RIGHT, padx=(5, 5), pady=(5, 10))

        self.font_use(self.saved_font_name, self.saved_font_size)

    def setup_bindings(self):
        # Bindings for keyboard shortcuts, tab switching, etc.
        self.tab_control.bind("<<NotebookTabChanged>>", self.switch_tab)
        self.chinese_textbox.bind("<<Selection>>", lambda event: self.update_highlighted_text(event, self.chinese_textbox, "chinese"))    
        self.hanviet_textbox.bind("<<Selection>>", lambda event: self.update_highlighted_text(event, self.hanviet_textbox, "hanviet"))    
        self.vietnamese_textbox.bind("<<Selection>>", lambda event: self.update_highlighted_text(event, self.vietnamese_textbox, "vietnamese"))    
        self.theme_combobox.bind("<<ComboboxSelected>>", self.change_theme)
        self.font_name_combobox.bind("<<ComboboxSelected>>", self.change_font_name)
        self.font_size_combobox.bind("<<ComboboxSelected>>", self.change_font_size)

        # Bind right-click event to each textbox to display context menu
        self.chinese_textbox.bind("<Button-3>", lambda event: self.show_context_menu(event, self.chinese_textbox))
        self.hanviet_textbox.bind("<Button-3>", lambda event: self.show_context_menu(event, self.hanviet_textbox))
        self.vietnamese_textbox.bind("<Button-3>", lambda event: self.show_context_menu(event, self.vietnamese_textbox))

    def toggle_fullscreen(self, event=None):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    def change_theme(self, event):
        selected_theme = self.theme_combobox.get()
        self.style.theme_use(selected_theme)
        utils.save_config("ttkb_theme", selected_theme)

    def change_font_name(self, event):
        selected_font_name = self.font_name_combobox.get()
        selected_font_size = self.font_size_combobox.get()
        self.font_use(selected_font_name, selected_font_size)
        utils.save_config("app_font_name", selected_font_name)

    def change_font_size(self, event):
        selected_font_name = self.font_name_combobox.get()
        selected_font_size = self.font_size_combobox.get()
        self.font_use(selected_font_name, selected_font_size)
        utils.save_config("app_font_size", selected_font_size)

    def font_use(self, font_name, font_size_string):
        font_size = utils.percent_to_float(font_size_string)
        self.style.configure('.', font=(font_name, int(font_size * 9 * self.ratio)))

        # Create a Font object with the desired font settings
        custom_font = font.Font(family=font_name, size=int(font_size * 9 * self.ratio))

        # Get the font metrics using the Font object
        font_height = custom_font.metrics("linespace")
        
        self.style.configure("Treeview", rowheight=font_height)

        main_textbox_font = (font_name, int(font_size * 12 * self.ratio))
        sub_textbox_font = (font_name, int(font_size * 9 * self.ratio))
        combobox_font = (font_name, int(font_size * 9 * self.ratio))

        self.highlighted_textbox.config(font=sub_textbox_font)
        self.meaning_textbox.config(font=sub_textbox_font)

        self.chinese_textbox.config(font=main_textbox_font)
        self.hanviet_textbox.config(font=main_textbox_font)
        self.vietnamese_textbox.config(font=main_textbox_font)

        self.theme_combobox.config(font=combobox_font)
        self.font_size_combobox.config(font=combobox_font)
        self.font_name_combobox.config(font=combobox_font)

    def show_context_menu(self, event, textbox):
        # Create a context menu
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="Update data", command=lambda: self.show_data_update_ui())

        # Display the context menu at the click location
        context_menu.post(event.x_root, event.y_root)

    def show_data_update_ui(self):
        data_update_window = translator_data_update_ui.DataUpdate(self, translator.convert_escape_characters(self.z_selected_text['chinese']))
        data_update_window.mainloop()

    def show_data_tables_ui(self):
        data_tables_window = translator_data_tables_ui.DataTables(self)
        data_tables_window.mainloop()

    def set_selection(self, textbox, start_index, end_index, color="#3498db"):
        # Remove any existing tags named "selected"
        textbox.tag_delete("selected")
        
        # Apply the "selected" tag to the selected text
        textbox.tag_add("selected", start_index, end_index)
        
        # Configure the appearance of the "selected" tag (e.g., set the foreground color)
        textbox.tag_configure("selected", foreground=color)

    def update_highlighted_text(self, event, textbox, textbox_type):
        # Check if there is any selected text
        if textbox.tag_ranges("sel"):
            # Retrive the index of the selected text in format line.column
            index_start = textbox.index("sel.first")
            index_end = textbox.index("sel.last")

            self.z_indexes = translator.z_data_search.get_selected_text_index(textbox_type, index_start, index_end)

            if self.z_indexes:
                self.z_selected_text['chinese'] = self.chinese_textbox.get(self.z_indexes['chinese'][0], self.z_indexes['chinese'][1])
                self.z_selected_text['hanviet'] = self.hanviet_textbox.get(self.z_indexes['hanviet'][0], self.z_indexes['hanviet'][1])
                self.z_selected_text['vietnamese'] = self.vietnamese_textbox.get(self.z_indexes['vietnamese'][0], self.z_indexes['vietnamese'][1])

                selected_text = textbox.get(self.z_indexes[textbox_type][0], self.z_indexes[textbox_type][1])
                meaning_text = translator.z_data_means.get_meaning(self.z_selected_text['chinese'])

                # Set selected text for all language textbox
                self.set_selection(self.chinese_textbox, self.z_indexes['chinese'][0], self.z_indexes['chinese'][1])
                self.set_selection(self.hanviet_textbox, self.z_indexes['hanviet'][0], self.z_indexes['hanviet'][1])
                self.set_selection(self.vietnamese_textbox, self.z_indexes['vietnamese'][0], self.z_indexes['vietnamese'][1])

                # Scroll the textbox to make the selected text visible
                self.chinese_textbox.see(self.z_indexes['chinese'][0])
                self.hanviet_textbox.see(self.z_indexes['hanviet'][0])
                self.vietnamese_textbox.see(self.z_indexes['vietnamese'][0])

                # Update the highlighted_textbox with the selected text
                self.highlighted_textbox.delete("1.0", tk.END)
                self.highlighted_textbox.insert("1.0", selected_text)

                # Update the meaning_textbox with the selected text
                self.meaning_textbox.delete("1.0", tk.END)
                self.meaning_textbox.insert("1.0", meaning_text)

    def scroll_to_last_position(self):
        if self.z_indexes:
            # Set selected text for all language textbox
            self.set_selection(self.chinese_textbox, self.z_indexes['chinese'][0], self.z_indexes['chinese'][1])
            self.set_selection(self.hanviet_textbox, self.z_indexes['hanviet'][0], self.z_indexes['hanviet'][1])
            self.set_selection(self.vietnamese_textbox, self.z_indexes['vietnamese'][0], self.z_indexes['vietnamese'][1])

            # Scroll the textbox to make the selected text visible
            self.chinese_textbox.see(self.z_indexes['chinese'][0])
            self.hanviet_textbox.see(self.z_indexes['hanviet'][0])
            self.vietnamese_textbox.see(self.z_indexes['vietnamese'][0])

    def switch_tab(self, event):
        current_tab_index = self.tab_control.index("current")  # Get index of the currently selected tab
        language_keys = ['chinese', 'hanviet', 'vietnamese']
        selected_text = self.z_selected_text[language_keys[current_tab_index]]

        # Update the highlighted_textbox with the selected text
        self.highlighted_textbox.delete("1.0", tk.END)
        self.highlighted_textbox.insert("1.0", selected_text)

    def process_text(self, input_text):
        lines = input_text.splitlines()
        cleaned_lines = [line for line in lines if line.strip()]
        processed_text = '\n\n'.join(cleaned_lines)
        return processed_text

    def process_clipboard(self):
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text:
                clipboard_text = self.process_text(clipboard_text)
                pyperclip.copy(clipboard_text)
            else:
                print("Clipboard is empty.")
        except pyperclip.PyperclipException as e:
            print("Error processing clipboard:", e)

    def translate(self):
        # Set all textbox to normal before Translate
        self.chinese_textbox.config(state="normal")
        self.hanviet_textbox.config(state="normal")
        self.vietnamese_textbox.config(state="normal")

        # Get Chinese text from the clipboard
        self.process_clipboard()
        txt_trung = pyperclip.paste()

        # Call the translate_callback function with textboxes
        txt_han, txt_viet = translator.translate(txt_trung)

        # Set Chinese text in the Chinese textbox
        self.chinese_textbox.delete("1.0", tk.END)
        self.chinese_textbox.insert("1.0", txt_trung)

        # Set Hán Việt text in the Hán Việt textbox
        self.hanviet_textbox.delete("1.0", tk.END)
        self.hanviet_textbox.insert("1.0", txt_han)
        
        # Set Vietnamese text in the Vietnamese textbox
        self.vietnamese_textbox.delete("1.0", tk.END)
        self.vietnamese_textbox.insert("1.0", txt_viet)

        # Set all textbox to readonly after Translate
        self.hanviet_textbox.config(state="disabled")
        self.vietnamese_textbox.config(state="disabled")

        # Switch to the Vietnamese tab
        if txt_viet:
            self.tab_control.select(self.vietnamese_tab)
            self.quick_translate_button.config(state=tk.NORMAL)  # Enable the button
            self.data_ui_button.config(state=tk.NORMAL)  # Enable the button

    def quick_translate(self):
        # Set all textbox to normal before Translate
        self.hanviet_textbox.config(state="normal")
        self.vietnamese_textbox.config(state="normal")

        # Get Chinese text from the chinese textbox
        txt_trung = self.chinese_textbox.get("1.0", tk.END)

        # Call the translate_callback function with textboxes
        txt_han, txt_viet = translator.quick_translate(txt_trung)

        # Set Hán Việt text in the Hán Việt textbox
        self.hanviet_textbox.delete("1.0", tk.END)
        self.hanviet_textbox.insert("1.0", txt_han)
        
        # Set Vietnamese text in the Vietnamese textbox
        self.vietnamese_textbox.delete("1.0", tk.END)
        self.vietnamese_textbox.insert("1.0", txt_viet)

        # Set all textbox to readonly after Translate
        self.hanviet_textbox.config(state="disabled")
        self.vietnamese_textbox.config(state="disabled")

        # Switch to the Vietnamese tab
        if txt_viet:
            self.tab_control.select(self.vietnamese_tab)

        self.scroll_to_last_position()

if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()
