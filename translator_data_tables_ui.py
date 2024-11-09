import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
import translator
import utils
import re
import os, csv

class DataTables(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Data Tables")
        self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))

        self.font_name = parent.font_name_combobox.get()
        self.font_size = utils.percent_to_float(parent.font_size_combobox.get())
        self.ratio = parent.ratio

        self.setup_gui()
        self.setup_fonts()

        self.data_search = translator.z_data_search.get_data()
        self.data_means = translator.z_data_means.get_data()
        self.last_search_index = None

        self.create_table(self.data_tree, self.data_search)

        self.data_export = utils.dict_get_first_value(utils.dict_remove_duplicates(self.data_search, 'TRUNG'), 'VIET')

    def setup_gui(self):
        # Frame for row 1
        frame_row1 = tk.Frame(self)
        frame_row1.pack(fill=tk.X, padx=(10, 10), pady=(10, 5))

        # Create a combobox to choose all local data type
        data_types = ["Data search", "Data meaning", "Data name", "Data name 2", "Data words", "Data dictionaries"]
        data_label = ttkb.Label(frame_row1, text="Choose data type:")
        data_label.pack(side=tk.LEFT, padx=5)
        self.data_combobox = ttkb.Combobox(frame_row1, values=data_types)
        self.data_combobox.current(0)
        self.data_combobox.bind("<<ComboboxSelected>>", self.change_data_type)
        self.data_combobox.pack(side=tk.LEFT, padx=5)

        self.search_button = ttk.Button(frame_row1, text="Search", command=self.search_data)
        self.search_button.pack(side=tk.RIGHT, padx=5)

        self.search_entry = ttk.Entry(frame_row1, width=70)
        self.search_entry.pack(side=tk.RIGHT)

        # Export button (from data to csv)
        self.export_button = ttk.Button(frame_row1, text="Export", command=self.export_data)
        self.show_export_button(True)

        # Frame for row 2
        frame_row2 = tk.Frame(self)
        frame_row2.pack(expand=True, fill=tk.BOTH, padx=(10, 10), pady=(5, 10))

        # Create a treeview to hold the table
        self.data_tree = ttkb.Treeview(frame_row2, show="headings")
        self.data_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # Add vertical scrollbar for the treeview
        v_scrollbar = ttkb.Scrollbar(self.data_tree, orient=tk.VERTICAL, command=self.data_tree.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.data_tree.configure(yscrollcommand=v_scrollbar.set)

        # Add horizontal scrollbar for the treeview
        h_scrollbar = ttkb.Scrollbar(self.data_tree, orient=tk.HORIZONTAL, command=self.data_tree.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.data_tree.configure(xscrollcommand=h_scrollbar.set)

    def setup_fonts(self):
        combobox_font = (self.font_name, int(self.font_size * 9 * self.ratio))
        entry_font = (self.font_name, int(self.font_size * 9 * self.ratio))
        
        self.data_combobox.config(font=combobox_font)
        self.search_entry.config(font=entry_font)

    def get_font_info(self, style_name):
        font_option = ttkb.Style().lookup(style_name, "font")
        if font_option:
            # Use regular expression to extract font family name and font size
            match = re.match(r'^\{?(.*?)\}?\s+(\d+)$', font_option)
            if match:
                font_family = match.group(1)
                font_size = match.group(2)
                return font_family, font_size
        return None, None

    def create_table(self, data_tree, data):
        # Clear existing columns and items in the Treeview
        data_tree['columns'] = data[0].keys() if data else []
        data_tree.delete(*data_tree.get_children())

        # Get the keys from the first dictionary
        headers = list(data[0].keys())

        # Insert headers into the treeview
        for i, header in enumerate(headers):
            data_tree.heading(i, text=header, anchor=tk.W)  # Use index i as column identifier

        # Insert data into the treeview
        for row_data in data:
            values = [value for value in row_data.values()]  # Extract values from each row_data dictionary
            data_tree.insert("", tk.END, values=values)

        # Get the maximum width of text in each column
        font_family, font_size = self.get_font_info("Treeview")
        tree_font = tk.font.Font(family=font_family, size=font_size)
        # print(f"font_family: {font_family}, font_size: {font_size}")

        max_widths = {}
        for header in headers:
            # Initialize the maximum width and index with the length of the header string and -1 respectively
            max_width = len(str(header))
            max_index = -1
            
            # Iterate through each row in the data to find the maximum width for the current header
            for index, row_data in enumerate(data):
                # Get the length of the string representation of the value corresponding to the header
                width = len(str(row_data[header]))
                # Update max_width and max_index if the current width is greater
                if width > max_width:
                    max_width = width
                    max_index = index
            
            # Store the maximum width and its corresponding row index for the current header
            if max_index == -1:
                max_widths[header] = tree_font.measure(str(header))
            else:
                max_widths[header] = tree_font.measure(str(data[max_index][header]))

        # Set the column width in the treeview
        for index, (header, max_width) in enumerate(max_widths.items()):
            #print(f"Column '{header}': Index = '{index}': Max Width = {max_width}")
            data_tree.column(index, anchor=tk.W, width=max_width + 20) # Padding +20

    def change_data_type(self, event):
        # By default, hide the Export button
        self.show_export_button(False)

        data_table = [{"ID": -1, "ROOT_ID": -1, "TRUNG": "None", "VIET": "None"}]
        data_type = self.data_combobox.get()

        if data_type == "Data search":
            data_table = self.data_search
            self.show_export_button(True)
        elif data_type == "Data meaning":
            data_table = self.data_means
        elif data_type == "Data name" and translator.z_data_names_local:
            data_table = [{"ID": index, "ROOT_ID": line[2], "TRUNG": line[0], "VIET": line[1]} for index, line in enumerate(translator.z_data_names_local)]
            self.show_export_button(True)
        elif data_type == "Data name 2" and translator.z_data_names2_local:
            data_table = [{"ID": index, "ROOT_ID": line[2], "TRUNG": line[0], "VIET": line[1]} for index, line in enumerate(translator.z_data_names2_local)]
            self.show_export_button(True)
        elif data_type == "Data words" and translator.z_data_words_local:
            data_table = [{"ID": index, "ROOT_ID": line[2], "TRUNG": line[0], "VIET": line[1]} for index, line in enumerate(translator.z_data_words_local)]
            self.show_export_button(True)
        elif data_type == "Data dictionaries" and translator.z_data_dicts_local:
            data_table = [{"ID": index, "ROOT_ID": line[2], "TRUNG": line[0], "VIET": line[1]} for index, line in enumerate(translator.z_data_dicts_local)]
        else:
            pass

        self.create_table(self.data_tree, data_table)

        self.data_export = utils.dict_get_first_value(utils.dict_remove_duplicates(data_table, 'TRUNG'), 'VIET')

    def search_data(self):
        query = self.search_entry.get().lower()
        if query:
            if self.last_search_index is None:
                self.last_search_index = 0
            else:
                self.last_search_index += 1

            items = self.data_tree.get_children()
            num_items = len(items)
            
            for _ in range(num_items):  # Loop through all items
                item = items[self.last_search_index % num_items]  # Wrap around to start if end is reached
                values = self.data_tree.item(item, 'values')
                if any(query in str(value).lower() for value in values):
                    self.data_tree.selection_set(item)
                    self.data_tree.focus(item)
                    self.data_tree.see(item)  # Ensure selected item is visible
                    self.last_search_index = items.index(item)
                    return
                self.last_search_index += 1
            
            self.data_tree.selection_remove(self.data_tree.selection())
            self.last_search_index = None

    def show_export_button(self, show):
        if show:
            self.export_button.pack(side=tk.RIGHT, padx=5)  # Show the Export button
        else:
            self.export_button.pack_forget()  # Hide the Export button

    def export_data(self):
        # Get the data type to determine the file name
        data_type = self.data_combobox.get()
        
        # Set the file name based on the data_type
        if data_type == "Data search":
            file_name = "search.csv"
        elif data_type == "Data name":
            file_name = "name.csv"
        elif data_type == "Data name 2":
            file_name = "name2.csv"
        elif data_type == "Data words":
            file_name = "words.csv"
        else:
            file_name = "export.csv"  # Default file name if no match

        # Define the export folder path
        export_folder = os.path.join(utils.SCRIPT_DIR, "export")
        
        # Create the export folder if it doesn't exist
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)
        
        # Set the full path for the file
        file_path = os.path.join(export_folder, file_name)
        
        # Open the CSV file in write mode
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write the TRUNG and VIET values for each row
            for row in self.data_export:
                writer.writerow([f"{row['TRUNG']}={row['VIET']}"])
        
        print(f"Data exported successfully to {file_path}.")