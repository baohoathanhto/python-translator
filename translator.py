# -*- coding: utf-8 -*-

import csv
import os
import re
import tkinter as tk
from tkinter import messagebox
from translator_ui import TranslatorUI
import translator_data_ui

# Constants
DATA_TYPE_NAMES = 1
DATA_TYPE_WORDS = 2
DATA_TYPE_DICTS = 3
DATA_TYPE_OTHERS = 4

DATA_MEANS_TYPE_VIETPHRASE_NAMES = 1
DATA_MEANS_TYPE_VIETPHRASE_WORDS = 2
DATA_MEANS_TYPE_LACVIET = 3
DATA_MEANS_TYPE_THIEUCHUU = 4

class ZData:
    def __init__(self):
        self.z_data = []

    def get_spacing(self, curr_string, next_string):
        try:
            spacing = ''

            # Check if curr_string is not empty
            if curr_string and curr_string[-1] in ['', ' ', '“', '‘', '{', '[', '(', '<', '\n', '\r', '\t']:
                spacing = ''
            else:
                spacing = ' '

            # Check if next_string is not empty and spacing is already set to a space
            if spacing == ' ' and next_string:
                if next_string[0] in [' ', ',', ';', ':', '.', '?', '!', '”', '’', '}', ']', ')', '>', '^', '\n', '\r', '\t']:
                    spacing = ''
                else:
                    spacing = ' '

            return spacing
        except Exception as e:
            print(f"An error occurred in get_spacing(): {e}")
            return ''

    # Array: [{TYPE, ID, T_INDEX, V_INDEX, TRUNG, HAN, VIET}]
    def get_han_viet(self):
        try:
            if not self.z_data:
                return '', ''

            txt_viet = ''
            txt_han = ''
            replace_index = 0

            for i in range(len(self.z_data)):
                curr_string = self.z_data[i]['VIET'].split('/')[0]
                next_string = self.z_data[i + 1]['VIET'].split('/')[0] if i + 1 < len(self.z_data) else ''

                spacing = self.get_spacing(curr_string, next_string)
                curr_string += spacing

                txt_viet += curr_string

                self.z_data[i]['V_INDEX'] = replace_index
                replace_index += len(curr_string)

            for i in range(len(self.z_data)):
                curr_string = self.z_data[i]['HAN']
                next_string = self.z_data[i + 1]['HAN'] if i + 1 < len(self.z_data) else ''

                spacing = self.get_spacing(curr_string, next_string)
                curr_string += spacing

                txt_han += curr_string

            return txt_han, txt_viet
        except Exception as e:
            print(f"An error occurred in get_han_viet(): {e}")
            return '', ''

    # Array: [{TYPE, ID, LEN, TRUNG, VIET}]
    def push_data_means(self, text, data_csv, data_type):
        try:
            for i in range(len(data_csv)):
                str_search = data_csv[i][0]
                index = 0
                while index < len(text) and index != -1:
                    index = text.find(str_search, index)
                    if index != -1:
                        self.z_data.append({'TYPE': data_type, 'ID': i, 'LEN': len(str_search), 'TRUNG': str_search, 'VIET': data_csv[i][1]})
                        index += 1
        except Exception as e:
            print(f"An error occurred in push_data_means(): {e}")

    # Array: [{TYPE, ID, T_INDEX, V_INDEX, TRUNG, HAN, VIET}]
    def push_data(self, text, data_csv, data_type):
        try:
            for i in range(len(data_csv)):
                str_search = data_csv[i][0]
                index = 0
                while index < len(text) and index != -1:
                    index = text.find(str_search, index)
                    if index != -1:
                        self.z_data.append({'TYPE': data_type, 'ID': i, 'T_INDEX': index, 'V_INDEX': -1, 'TRUNG': str_search, 'HAN': '', 'VIET': data_csv[i][1]})
                        index += 1
        except Exception as e:
            print(f"An error occurred in push_data(): {e}")

    # Array: [{TYPE, ID, T_INDEX, V_INDEX, TRUNG, HAN, VIET}]
    def push_other_chars(self, text_data, data_type):
        try:
            text = self.split_text(text_data)
            for i in range(len(text)):
                self.z_data.append({'TYPE': data_type, 'ID': -1, 'T_INDEX': text[i]['INDEX'], 'V_INDEX': -1, 'TRUNG': text[i]['TEXT'], 'HAN': text[i]['TEXT'], 'VIET': text[i]['TEXT']})
        except Exception as e:
            print(f"An error occurred in push_other_chars(): {e}")

    # Array: [{TYPE, ID, T_INDEX, V_INDEX, TRUNG, HAN, VIET}]
    def split_text(self, text_data):
        try:
            if text_data is None:
                return []

            results = []
            text = text_data
            index = 0

            for i in range(len(self.z_data)):
                pos = text.find(self.z_data[i]['TRUNG'])
                if pos != -1:
                    prev_text = text[:pos]
                    text = text[pos + len(self.z_data[i]['TRUNG']):]

                    if prev_text != '':
                        data_prev_text = self.split_text_in_line(prev_text)
                        if data_prev_text is not None:
                            for data in data_prev_text:
                                results.append({'TEXT': data, 'INDEX': index})

                    index += pos + len(self.z_data[i]['TRUNG'])

            if text != '':
                results.append({'TEXT': text, 'INDEX': index})

            return results
        except Exception as e:
            print(f"An error occurred in split_text(): {e}")
            return []

    def split_text_in_line(self, text):
        try:
            if not text:
                return ''

            regex_start = re.compile(r'[^\r\n\t ]')
            regex_end = re.compile(r'[\r\n\t]')

            data_text = []

            match_start = regex_start.search(text)
            match_end = None

            while match_start:
                temp = text[:match_start.start()]
                if temp:
                    data_text.append(temp)

                text = text[match_start.start():]
                match_end = regex_end.search(text)

                if match_end:
                    data_text.append(text[:match_end.start()])
                    text = text[match_end.start():]
                else:
                    break

                match_start = regex_start.search(text)

            if text:
                data_text.append(text)

            return data_text
        except Exception as e:
            print(f"An error occurred in split_text_in_line(): {e}")

    # All Arrays, clean data have the same value at (index)
    def clean_duplicate(self):
        try:
            if not self.z_data:
                pass

            self.key_sort({'T_INDEX': 'asc'})

            i = 0
            while i < len(self.z_data):
                next_index = self.z_data[i]['T_INDEX'] + len(self.z_data[i]['TRUNG'])
                flag = 0
                j = i + 1
                start = j
                count = 0
                while j < len(self.z_data) and self.z_data[j]['T_INDEX'] < next_index:
                    if self.z_data[j]['TYPE'] >= self.z_data[i]['TYPE'] and len(self.z_data[j]['TRUNG']) <= len(self.z_data[i]['TRUNG']):
                        count += 1
                        flag = 1
                        j += 1
                    else:
                        flag = 2
                        break
                if flag == 1:
                    del self.z_data[start:start+count]
                    i += 1
                elif flag == 2:
                    del self.z_data[i]
                else:
                    i += 1
        except Exception as e:
            print(f"An error occurred in clean_duplicate(): {e}")

    # All objects, clean data have the same value at (key)
    def clean_duplicate_object(self):
        try:
            if not self.z_data:
                pass

            self.key_sort({'TYPE': 'asc', 'ID': 'asc'})

            i = 0
            while i < len(self.z_data):
                j = i + 1
                count = 0
                while j < len(self.z_data):
                    if self.z_data[j]['ID'] == self.z_data[i]['ID'] and self.z_data[j]['TYPE'] == self.z_data[i]['TYPE']:
                        count += 1
                        j += 1
                    else:
                        break
                if count > 0:
                    del self.z_data[i:i+count]
                i += 1
        except Exception as e:
            print(f"An error occurred in clean_duplicate_object(): {e}")

    # Array: [{TYPE, ID, T_INDEX, V_INDEX, TRUNG, HAN, VIET}], sort array first, then clean duplicate
    def clean_duplicate(self):
        try:
            if not self.z_data:
                pass

            self.key_sort({'T_INDEX': 'asc'})

            i = 0
            while i < len(self.z_data):
                next_index = self.z_data[i]['T_INDEX'] + len(self.z_data[i]['TRUNG'])
                flag = 0
                j = i + 1
                start = j
                count = 0
                while j < len(self.z_data) and self.z_data[j]['T_INDEX'] < next_index:
                    if self.z_data[j]['TYPE'] >= self.z_data[i]['TYPE'] and len(self.z_data[j]['TRUNG']) <= len(self.z_data[i]['TRUNG']):
                        count += 1
                        flag = 1
                        j += 1
                    else:
                        flag = 2
                        break
                if flag == 1:
                    del self.z_data[start:start+count]
                    i += 1
                elif flag == 2:
                    del self.z_data[i]
                else:
                    i += 1
        except Exception as e:
            print(f"An error occurred in clean_duplicate(): {e}")

    # Array: [{TYPE, ID, T_INDEX, V_INDEX, TRUNG, HAN, VIET}]
    def update_dicts(self, data_dicts):
        try:
            if not self.z_data:
                pass

            for i in range(len(self.z_data)):
                if self.z_data[i]['ID'] != -1:
                    words = list(self.z_data[i]['TRUNG'])
                    for j, word in enumerate(words):
                        spacing = ' ' if j < len(words) - 1 else ''
                        for k in range(len(data_dicts) - 1):
                            if word == data_dicts[k][0]:
                                self.z_data[i]['HAN'] += data_dicts[k][1] + spacing
                                break
        except Exception as e:
            print(f"An error occurred in update_dicts(): {e}")

    # All object arrays
    def key_sort(self, keys):
        # Define a custom key function for sorting
        def custom_key(item):
            key_values = [item.get(key, '') for key in keys]  # Get values for specified keys
            return tuple(key_values)  # Return a tuple of key values for sorting

        # Sort the data in-place using the custom key function
        self.z_data.sort(key=custom_key)

# End of class ZData
                
def read_csv(file_path):
    try:
        data = []
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter="=")  # Specify the delimiter
            for row in reader:
                data.append(row)
        return data
    except Exception as e:
        print(f"An error occurred in read_csv(): {e}")
        return []

def get_data(file_name):
    try:
        data_dir = "data"
        file_path = os.path.join(data_dir, file_name)
        if os.path.exists(file_path):
            return read_csv(file_path)
        else:
            print(f"Error: File '{file_name}' not found.")
            return []
    except Exception as e:
        print(f"An error occurred in get_data(): {e}")
        return []
        
def to_sentence_case(text):
    return re.sub(r'(^|[\n.?!:][ “”‘’\"\'{}[\]()<>]*)(\w)', lambda match: match.group().upper(), text, flags=re.UNICODE)

# Translate function
def translate(chinese_textbox, hanviet_textbox, vietnamese_textbox):
    try:
        # Get Chinese text from the textbox
        txt_trung = chinese_textbox.get("1.0", tk.END).strip()

        # Check if Chinese text is not empty
        if txt_trung:
            # Initialize ZData
            z_data_search = ZData()

            # Search string in global data.csv & make new local data for this text
            z_data_search.push_data(txt_trung, z_data_names, DATA_TYPE_NAMES)
            z_data_search.push_data(txt_trung, z_data_names2, DATA_TYPE_NAMES)
            z_data_search.push_data(txt_trung, z_data_words, DATA_TYPE_WORDS)
            z_data_search.push_data(txt_trung, z_data_dicts, DATA_TYPE_DICTS)

            # Sort & then clean duplicate words
            z_data_search.clean_duplicate()

            # Update 'HAN' word into searched data
            z_data_search.update_dicts(z_data_dicts)

            # Add other chars not in any original data.csv & sort again
            z_data_search.push_other_chars(txt_trung, DATA_TYPE_OTHERS)
            z_data_search.key_sort({'T_INDEX': 'asc'})  # sort again

            # Get Han Viet translation
            txt_han, txt_viet = z_data_search.get_han_viet()

            # Set Hán Việt text in the Vietnamese textbox
            hanviet_textbox.delete("1.0", tk.END)
            hanviet_textbox.insert("1.0", to_sentence_case(txt_han))
            
            # Set Vietnamese text in the Vietnamese textbox
            vietnamese_textbox.delete("1.0", tk.END)
            vietnamese_textbox.insert("1.0", to_sentence_case(txt_viet))
            
            # Call translate_and_display with z_data_search array
            # translator_data_ui.display_table(z_data_search.z_data)
            
        else:
            messagebox.showinfo("Error", "Please enter Chinese text.")
    except Exception as e:
        print(f"An error occurred in translate(): {e}")
        
if __name__ == "__main__":
    try:
        z_data_dicts = get_data("zh_dicts.csv")
        z_data_words = get_data("zh_words.csv")
        z_data_names = get_data("zh_names.csv")
        z_data_names2 = get_data("zh_names2.csv")
        z_data_means_lacviet = get_data("zh_means_lacviet.csv")
        z_data_means_thieuchu = get_data("zh_means_thieuchuu.csv")
        
        app = TranslatorUI(translate)
        app.run()
    except Exception as e:
        print(f"An error occurred in main code block: {e}")
