import tkinter as tk
import ttkbootstrap as ttkb
import translator as tr
import utils

class DataUpdate(tk.Toplevel):
    def __init__(self, parent, selected_text):
        super().__init__(parent)

        self.title(f"Update data for highlighted text")
        self.resizable(False, False)  # Disable resizing

        self.font_name = parent.font_name_combobox.get()
        self.font_size = utils.percent_to_float(parent.font_size_combobox.get())
        self.ratio = parent.ratio

        self.parent = parent
        self.text_trung = selected_text
        self.text_trung_backup = self.text_trung
        self.text_han, self.text_viet = tr.quick_translate(self.text_trung, False)
        self.data_list = tr.z_data_means.get_data_update_list(self.text_trung)
        self.data_items_ids = [] # List to store ID & ROOT_ID of the current items
        self.data_items = []  # List to store data items separate by "/"
        
        self.setup_gui()
        self.setup_fonts()
        self.setup_priority_check_button()

        self.load_data_items()  # Load data from CSV when the app starts

    def setup_gui(self):
        self.top_frame = ttkb.Frame(self)
        self.top_frame.pack(side="top", fill="both", expand=True)

        self.data_type_combobox = ttkb.Combobox(self.top_frame, values=list(tr.data_type_update.values()))
        if self.data_list:
            self.data_type_combobox.set(self.data_list[0]['TYPE_NAME'])
        else:
            self.data_type_combobox.set(tr.data_type_update[tr.DATA_TYPE_WORDS])
        self.data_type_combobox.bind("<<ComboboxSelected>>", self.load_data_items)

        # Radio button for Priority
        self.priority_var = tk.BooleanVar(value=False)
        self.priority_check_button = ttkb.Checkbutton(self.top_frame, text="Words priority", variable=self.priority_var)

        self.chinese_entry = ttkb.Entry(self.top_frame, width=70)
        self.hanviet_entry = ttkb.Entry(self.top_frame, width=70)
        self.vietnamese_entry = ttkb.Entry(self.top_frame, width=70)

        self.chinese_entry.insert(0, self.text_trung)
        self.hanviet_entry.insert(0, self.text_han)
        self.vietnamese_entry.insert(0, self.text_viet)
        self.chinese_entry.bind("<KeyRelease>", self.chinese_changed)

        self.data_type_combobox.grid(row=0, column=0, sticky="w", padx=10, pady=(10,5))
        self.priority_check_button.grid(row=0, column=0, sticky="e", padx=10)

        self.chinese_entry.grid(row=1, column=0, sticky="w", padx=(10,1), pady=5)
        self.hanviet_entry.grid(row=2, column=0, sticky="w", padx=(10,1), pady=5)
        self.vietnamese_entry.grid(row=3, column=0, sticky="w", padx=(10,1), pady=5)

        self.items_frame = ttkb.Frame(self)
        self.items_frame.pack(side="top", fill="both", expand=True)

        self.bottom_frame = ttkb.Frame(self)
        self.bottom_frame.pack(side="top", fill="both", expand=True)

        self.reset_button = ttkb.Button(self.top_frame, text="\u21BB", width=2, command=self.reset_chinese_text)
        self.reset_button.grid(row=1, column=1, sticky="e", padx=(1,10), pady=5)

        self.add_button = ttkb.Button(self.top_frame, bootstyle="success", text="+", width=2, command=self.add_item)
        self.add_button.grid(row=3, column=1, sticky="e", padx=(1,10), pady=5)

        self.update_button = ttkb.Button(self.bottom_frame, bootstyle="warning", text="Update", command=self.save_data_items)
        self.update_button.pack(side="left", padx=10, pady=(5,10))

        self.delete_button = ttkb.Button(self.bottom_frame, bootstyle="danger", text="Delete", command=self.delete_data_items)
        self.delete_button.pack(side="right", padx=10, pady=(5,10))

    def setup_fonts(self):
        combobox_font = (self.font_name, int(self.font_size * 9 * self.ratio))
        entry_font = (self.font_name, int(self.font_size * 9 * self.ratio))

        self.data_type_combobox.config(font=combobox_font)
        self.chinese_entry.config(font=entry_font)
        self.hanviet_entry.config(font=entry_font)
        self.vietnamese_entry.config(font=entry_font)

    def setup_priority_check_button(self):
        if self.text_trung in tr.z_data_words_priority:
            self.priority_var.set(True)  # Set the button to checked
        else:
            self.priority_var.set(False)  # Set it to unchecked

    def reset_chinese_text(self):
        self.chinese_entry.delete(0, tk.END)
        self.chinese_entry.insert(0, self.text_trung_backup)
        self.chinese_changed()

    def add_item(self):
        new_item = self.vietnamese_entry.get()
        if new_item:
            self.data_items.insert(0, new_item)
            self.refresh_items()

    def move_item_up(self, index):
        if index > 0:
            self.data_items.insert(0, self.data_items.pop(index))  # Move item to the top
            self.refresh_items()

    def move_item_down(self, index):
        if index < len(self.data_items) - 1:
            self.data_items.append(self.data_items.pop(index))  # Move item to the bottom
            self.refresh_items()

    def delete_item(self, index):
        del self.data_items[index]
        self.refresh_items()

    def update_item(self, index, entry):
        new_item = entry.get()
        self.data_items[index] = new_item  # Update the corresponding item in data_items

    def refresh_items(self):
        # Clear existing items
        for widget in self.items_frame.winfo_children():
            widget.destroy()

        # Recreate items from the updated list
        for i, item_name in enumerate(self.data_items):
            style = "success" if i == 0 else "light"
            entry = ttkb.Entry(self.items_frame, bootstyle=style, width=70)
            entry.config(font=(self.font_name, int(self.font_size * 9 * self.ratio)))
            entry.insert(0, item_name)
            entry.grid(row=i, column=0, sticky="ew", padx=(10,1), pady=5)
            entry.bind("<KeyRelease>", lambda event, index=i, entry=entry: self.update_item(index, entry))  # Bind an event to update data_items

            up_button = ttkb.Button(self.items_frame, text="↑", width=2, command=lambda index=i: self.move_item_up(index))
            up_button.grid(row=i, column=1, sticky="e", padx=1, pady=5)

            down_button = ttkb.Button(self.items_frame, text="↓", width=2, command=lambda index=i: self.move_item_down(index))
            down_button.grid(row=i, column=2, sticky="e", padx=1, pady=5)

            subtract_button = ttkb.Button(self.items_frame, bootstyle="danger", text="-", width=2, command=lambda index=i: self.delete_item(index))
            subtract_button.grid(row=i, column=3, sticky="e", padx=(1,10), pady=5)

        if self.data_items:
            self.update_button.config(state=tk.NORMAL)
        else:            
            self.update_button.config(state=tk.DISABLED)
        
        if self.data_items_ids:
            self.delete_button.config(state=tk.NORMAL)
        else:
            self.delete_button.config(state=tk.DISABLED)

    def save_data_items(self):
        current_data_type = self.data_type_combobox.get()
        str_items = '/'.join(self.data_items)

        if current_data_type == tr.data_type_update[tr.DATA_TYPE_NAMES]:
            tr.update_data_csv(tr.DATA_TYPE_NAMES, self.data_items_ids, self.text_trung, str_items)
        elif current_data_type == tr.data_type_update[tr.DATA_TYPE_NAMES2]:
            tr.update_data_csv(tr.DATA_TYPE_NAMES2, self.data_items_ids, self.text_trung, str_items)
        elif current_data_type == tr.data_type_update[tr.DATA_TYPE_WORDS]:
            tr.update_data_csv(tr.DATA_TYPE_WORDS, self.data_items_ids, self.text_trung, str_items)

        self.update_words_priority()

        self.parent.quick_translate()
        self.destroy()

    def delete_data_items(self):
        current_data_type = self.data_type_combobox.get()

        if current_data_type == tr.data_type_update[tr.DATA_TYPE_NAMES]:
            tr.delete_data_csv(tr.DATA_TYPE_NAMES, self.data_items_ids)
        elif current_data_type == tr.data_type_update[tr.DATA_TYPE_NAMES2]:
            tr.delete_data_csv(tr.DATA_TYPE_NAMES2, self.data_items_ids)
        elif current_data_type == tr.data_type_update[tr.DATA_TYPE_WORDS]:
            tr.delete_data_csv(tr.DATA_TYPE_WORDS, self.data_items_ids)
            tr.delete_words_priority_csv(self.text_trung)

        self.parent.quick_translate()
        self.destroy()

    def update_words_priority(self):
        if self.priority_var.get():
            tr.update_words_priority_csv(self.text_trung)
        else:
            tr.delete_words_priority_csv(self.text_trung)

    def load_data_items(self, event=None):
        current_data_type = self.data_type_combobox.get()
        try:
            self.data_items_ids = []
            for item in self.data_list:
                if item['TYPE_NAME'] == current_data_type:
                    self.data_items = item['VIET'].split("/")
                    self.data_items_ids.append([item['ID'], item['ROOT_ID']])
                    break;
            if not self.data_items_ids:
                self.load_empty_list()
            self.refresh_items()
        except Exception as e:
            print(f"An error occurred in load_data_items(): {e}")
            self.load_empty_list()  # Load default list if CSV file not found
            
        self.load_entry_text(current_data_type)

    def load_empty_list(self):
        self.data_items = []
        self.refresh_items()

    def load_entry_text(self, data_type):
        text_viet = self.text_viet

        if data_type == tr.data_type_update[tr.DATA_TYPE_NAMES] or data_type == tr.data_type_update[tr.DATA_TYPE_NAMES2]:
            if self.data_items:
                text_viet = self.data_items[0]
            else:
                text_viet = self.text_han.title()

        self.vietnamese_entry.delete(0, tk.END)
        self.vietnamese_entry.insert(0, text_viet)

    def chinese_changed(self, event=None):
        self.text_trung = self.chinese_entry.get()
        self.text_han, self.text_viet = tr.quick_translate(self.text_trung, False)

        # Update the hanviet_entry with the new text
        self.hanviet_entry.delete(0, tk.END)
        self.hanviet_entry.insert(0, self.text_han)

        # Update the vietnamese_entry with the new text
        self.vietnamese_entry.delete(0, tk.END)
        self.vietnamese_entry.insert(0, self.text_viet)

        self.data_list = tr.z_data_means.get_data_update_list(self.text_trung)
        self.load_data_items()