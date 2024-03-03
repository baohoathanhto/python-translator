# -*- coding: utf-8 -*-

import csv
import os
import re
import tkinter as tk
from tkinter import messagebox

class ZData:
    def __init__(self):
        self.z_data = []

    # Get data search
    def get_data(self):
        return self.z_data

    # Array: [{TYPE, TYPE_NAME, ID, T_INDEX, H_INDEX, V_INDEX, TRUNG, HAN, VIET}]
    def get_han_viet(self):
        if not self.z_data:
            return '', ''

        txt_viet = ''
        txt_han = ''
        line = 1
        replace_index_viet = 0
        replace_index_han = 0

        for i in range(len(self.z_data)):
            if (line < self.z_data[i]['LINE']):
                line = self.z_data[i]['LINE']
                replace_index_viet = 0
                replace_index_han = 0

            # Update viet index & get viet text
            curr_string_viet = self.z_data[i]['VIET'].split('/')[0]
            next_string_viet = self.z_data[i + 1]['VIET'].split('/')[0] if i + 1 < len(self.z_data) else ''

            spacing_viet = get_spacing(curr_string_viet, next_string_viet)
            curr_string_viet += spacing_viet

            txt_viet += curr_string_viet

            self.z_data[i]['V_INDEX'] = replace_index_viet
            replace_index_viet += len(curr_string_viet)

            # Update han index & get han text
            curr_string_han = self.z_data[i]['HAN']
            next_string_han = self.z_data[i + 1]['HAN'] if i + 1 < len(self.z_data) else ''

            spacing_han = get_spacing(curr_string_han, next_string_han)
            curr_string_han += spacing_han

            txt_han += curr_string_han
            self.z_data[i]['H_INDEX'] = replace_index_han
            replace_index_han += len(curr_string_han)

        return txt_han, txt_viet

    def get_data_update_list(self, txt_trung):
        data_list = []
        for data in self.z_data:
            if data['TRUNG'] == txt_trung:
                data_list.append(data)
        return data_list

    # Array: [{TYPE, TYPE_NAME, ID, T_INDEX, H_INDEX, V_INDEX, TRUNG, HAN, VIET}]
    def push_data(self, text_data, data_csv, data_type):
        lines = splitlines_keep_linebreak(text_data)
        for i in range(len(data_csv)):
            str_search = data_csv[i][0]
            line_num = 1
            for line in lines:
                index = 0
                while index < len(line) and index != -1:
                    index = line.find(str_search, index)
                    if index != -1:
                        self.z_data.append({'TYPE': data_type, 'TYPE_NAME': data_type_mapping[data_type], 'ID': i, 'ROOT_ID': data_csv[i][2], 'LINE': line_num, 'T_INDEX': index, 'H_INDEX': -1, 'V_INDEX': -1, 'TRUNG': str_search, 'HAN': '', 'VIET': data_csv[i][1]})
                        index += 1
                line_num += 1
    
    # Array: [{TYPE, TYPE_NAME, ID, T_INDEX, H_INDEX, V_INDEX, TRUNG, HAN, VIET}]
    def push_other_chars(self, text_data, data_type):
        lines = splitlines_keep_linebreak(text_data)
        for line_num, line in enumerate(lines, start=1):
            index = 0
            existed_data = self.get_data_by_line(line_num)
            if existed_data:
                for t_index, trung in existed_data:
                    if index < t_index:
                        result = line[index:t_index]
                        self.z_data.append({'TYPE': data_type, 'TYPE_NAME': data_type_mapping[data_type], 'ID': -1, 'ROOT_ID': -1, 'LINE': line_num, 'T_INDEX': index, 'H_INDEX': -1, 'V_INDEX': -1, 'TRUNG': result, 'HAN': result, 'VIET': result})
                    index = t_index + len(trung) # data[1] = TRUNG
                if index < len(line):
                    result = line[index:len(line)]
                    self.z_data.append({'TYPE': data_type, 'TYPE_NAME': data_type_mapping[data_type], 'ID': -1, 'ROOT_ID': -1, 'LINE': line_num, 'T_INDEX': index, 'H_INDEX': -1, 'V_INDEX': -1, 'TRUNG': result, 'HAN': result, 'VIET': result})
            else:
                result = line
                self.z_data.append({'TYPE': data_type, 'TYPE_NAME': data_type_mapping[data_type], 'ID': -1, 'ROOT_ID': -1, 'LINE': line_num, 'T_INDEX': index, 'H_INDEX': -1, 'V_INDEX': -1, 'TRUNG': result, 'HAN': result, 'VIET': result})
                   
        self.z_data = sorted(self.z_data, key=lambda x: (x['LINE'], x['T_INDEX']))

    def get_data_by_line(self, line):
        data = []
        for item in self.z_data:
            if item['LINE'] == line:
                data.append((item['T_INDEX'], item['TRUNG']))
        return data

    # Array: [{TYPE, TYPE_NAME, ID, T_INDEX, H_INDEX, V_INDEX, TRUNG, HAN, VIET}], sort array first, then clean duplicate
    def clean_duplicate(self):
        if not self.z_data:
            pass

        self.z_data = sorted(self.z_data, key=lambda x: (x['LINE'], x['T_INDEX']))

        i = 0
        while i < len(self.z_data):
            flag = 0
            j = i + 1
            start = j
            count = 0
            next_index = self.z_data[i]['T_INDEX'] + len(self.z_data[i]['TRUNG'])
            while j < len(self.z_data) and self.z_data[i]['LINE'] == self.z_data[j]['LINE'] and self.z_data[j]['T_INDEX'] < next_index:
                if len(self.z_data[j]['TRUNG']) < len(self.z_data[i]['TRUNG']):
                    count += 1
                    flag = 1
                    j += 1
                elif len(self.z_data[j]['TRUNG']) > len(self.z_data[i]['TRUNG']):
                    flag = 2
                    break
                else:
                    if self.z_data[j]['TYPE'] >= self.z_data[i]['TYPE']:
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
                del self.z_data[i:i+1]
            else:
                i += 1

    # Array: [{TYPE, TYPE_NAME, ID, T_INDEX, H_INDEX, V_INDEX, TRUNG, HAN, VIET}]
    def update_dicts(self, data_dicts):
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

    # Textbox type should be chinese, hanviet, vietnamese
    def get_selected_text_index(self, textbox_type, index_start, index_end):
        # Retrieve the character index of the selected text
        line_start = int(index_start.split('.')[0])
        column_start = int(index_start.split('.')[1])
        line_end = int(index_end.split('.')[0])
        column_end = int(index_end.split('.')[1]) - 1 # columne_end is the index of the last selected character + 1, so this could be -1 to match the concept

        #print (f"index_start: {index_start}, index_end: {index_end}")

        # Store index & text header of each textbox
        lang_type = {
            'chinese': ['T_INDEX', 'TRUNG'],
            'hanviet': ['H_INDEX', 'HAN'],
            'vietnamese': ['V_INDEX', 'VIET']
        }

        # Store start column & end column of each textbox
        columns = {
            'chinese': [0, 0],
            'hanviet': [0, 0],
            'vietnamese': [0, 0]
        }

        # Store column start index & end index of each textbox
        indexes = {
            'chinese': [0, 0],
            'hanviet': [0, 0],
            'vietnamese': [0, 0]
        }

        found_item_start = False
        found_item_end = False
        item_start = {}
        item_end = {}
        prev_item = {}
        
        for item in self.z_data:
            if item['LINE'] <= line_end:
                index = item[lang_type[textbox_type][0]]
                length = len(item[lang_type[textbox_type][1]].split('/')[0])

                if item['LINE'] == line_start and not found_item_start:
                    if (column_start >= index and column_start < index + length) or (column_start < index and column_end >= index):
                        found_item_start = True
                        item_start = item

                if item['LINE'] == line_end and not found_item_end:
                    if column_end >= index:
                        if column_end < index + length:
                            found_item_end = True
                            item_end = item
                        else:
                            prev_item = item
                    else:
                        found_item_end = True
                        item_end = prev_item
            else:
                break

        if item_start and item_end:
            # Start columne is the index of the first selected character
            columns['chinese'][0] = item_start[lang_type['chinese'][0]]                            
            columns['hanviet'][0] = item_start[lang_type['hanviet'][0]]                            
            columns['vietnamese'][0] = item_start[lang_type['vietnamese'][0]]

            # End columne is the index of the last selected character + 1, so in this case, we don't need - 1
            columns['chinese'][1] = item_end[lang_type['chinese'][0]] + len(item_end[lang_type['chinese'][1]])
            columns['hanviet'][1] = item_end[lang_type['hanviet'][0]] + len(item_end[lang_type['hanviet'][1]])
            columns['vietnamese'][1] = item_end[lang_type['vietnamese'][0]] + len(item_end[lang_type['vietnamese'][1]].split('/')[0])

            indexes['chinese'][0] = f"{line_start}.{columns['chinese'][0]}"
            indexes['chinese'][1] = f"{line_end}.{columns['chinese'][1]}"
            indexes['hanviet'][0] = f"{line_start}.{columns['hanviet'][0]}"
            indexes['hanviet'][1] = f"{line_end}.{columns['hanviet'][1]}"
            indexes['vietnamese'][0] = f"{line_start}.{columns['vietnamese'][0]}"
            indexes['vietnamese'][1] = f"{line_end}.{columns['vietnamese'][1]}"
        else:
            return {}

        return indexes

# End of class ZData

class ZDataMeans:
    def __init__(self):
        self.z_data = []

    # Get data means
    def get_data(self):
        return self.z_data

    # Array: [{TYPE, TYPE_NAME, ID, LEN, TRUNG, VIET}]
    def push_data(self, text, data_csv, data_type):
        for i in range(len(data_csv)):
            if len(data_csv[i]) < 2:
                print(f"Error: Insufficient data for index {i} in data_csv")
                continue
            str_search = data_csv[i][0]
            index = 0
            while index < len(text) and index != -1:
                index = text.find(str_search, index)
                if index != -1:
                    self.z_data.append({'TYPE': data_type, 'TYPE_NAME': data_type_mapping[data_type], 'ID': i, 'ROOT_ID': data_csv[i][2], 'LEN': len(str_search), 'TRUNG': str_search, 'VIET': data_csv[i][1]})
                    index += 1

    # All objects, clean data have the same value at (key)
    def clean_duplicate(self):
        if not self.z_data:
            pass

        self.z_data = sorted(self.z_data, key=lambda x: (x['TYPE'], x['ID']))

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

        self.z_data = sorted(self.z_data, key=lambda x: (x['TYPE'], -x['LEN'], x['TRUNG']))

    def get_meaning(self, chinese_text):
        if chinese_text == '':
            return

        result = chinese_text
        info = '';
        count = 0

        for data_mean in self.z_data:
            pos = chinese_text.find(data_mean['TRUNG'])
            if pos != -1:
                type_name = ''
                separator = '-----------------' if count > 0 else ''
                if data_mean['TYPE'] == DATA_MEANS_TYPE_VIETPHRASE_NAMES:
                    type_name = 'VietPhrase - Name'
                elif data_mean['TYPE'] == DATA_MEANS_TYPE_VIETPHRASE_WORDS:
                    type_name = 'VietPhrase'
                elif data_mean['TYPE'] == DATA_MEANS_TYPE_LACVIET:
                    type_name = 'Lạc Việt'
                elif data_mean['TYPE'] == DATA_MEANS_TYPE_THIEUCHUU:
                    type_name = 'Thiều Chửu'
                else:
                    type_name = 'Unknown'
                info += f'\n{separator}\n{data_mean["TRUNG"]}《{type_name} ~ {int(data_mean["ROOT_ID"]) + 1}》\n{revert_escape_characters(data_mean["VIET"])}'
                count += 1
        if info != '':
            result += info
        else:
            result = 'Không tìm thấy thông tin!'

        return result


# End of class ZDataMeans
                
def read_csv(file_path):
    data = []
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="=", quoting=csv.QUOTE_NONE)  # Specify the delimiter
        for i, row in enumerate(reader):
            row.insert(2, str(i))  # Inserting index as the third element (index 2)
            data.append(row)
    return data

def write_csv(file_path, data_csv):
    with open(file_path, mode="w", encoding="utf-8", newline='') as file:
        writer = csv.writer(file, delimiter="=")
        for row in data_csv:
            writer.writerow(row[:2])  # Write only the first two columns of each row

def get_data(file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    file_path = os.path.join(data_dir, file_name)
    
    if os.path.isfile(file_path):
        return read_csv(file_path)
    else:
        print(f"Error: File '{file_path}' not found.")
        return []

def save_data(file_name, data_csv):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    file_path = os.path.join(data_dir, file_name)
    
    if os.path.isfile(file_path):
        return write_csv(file_path, data_csv)
    else:
        print(f"Error: File '{file_path}' not found.")
        return []

def get_data_local(text, data_csv, data_type):
    text = remove_escape_characters(text)
    data_local = []
    for row in data_csv:
        str_search = row[0]
        if str_search in text:
            data_local.append(row)
    return data_local

def get_spacing(curr_string, next_string):
    spacing = ''

    # Check if curr_string is not empty
    if curr_string:
        if curr_string[-1] in [' ', '“', '‘', '{', '[', '(', '<', '\n', '\r', '\t']:
            spacing = ''
        else:
            spacing = ' '

    # Check if next_string is not empty and spacing is already set to a space
    if next_string:
        if spacing == ' ':
            if next_string[0] in [' ', ',', ';', ':', '.', '?', '!', '”', '’', '}', ']', ')', '>', '^', '\n', '\r', '\t']:
                spacing = ''
            else:
                spacing = ' '

    return spacing

# All Arrays, clean data have the same value at (index)
def clean_duplicate_array(data, index):
    if not data:
        return []

    unique_data = []
    seen_values = set()

    for row in data:
        value = row[index]
        if value not in seen_values:
            unique_data.append(row)
            seen_values.add(value)

    return unique_data
        
def to_sentence_case(text):
    return re.sub(r'(^|[\n.?!:][ “”‘’\"\'{}[\]()<>]*)(\w)', lambda match: match.group().upper(), text, flags=re.UNICODE)

def replace_special_characters(input_string):
    # Mapping of special characters to their regular counterparts
    special_characters_mapping = {
        '？': '?',
        '！': '!',
        '＠': '@',
        '＃': '#',
        '％': '%',
        '＾': '^',
        '＆': '&',
        '＊': '*',
        '（': '(',
        '）': ')',
        '［': '[',
        '］': ']',
        '｛': '{',
        '｝': '}',
        '；': ';',
        '：': ':',
        #'’': '\'',
        #'”': '\"',
        #'‘': '\'',
        #'“': '\"',
        '，': ',',
        '．': '.',
        '。': '.',
        '·': '.',
        '《': '<',
        '》': '>',
        '／': '/',
        '？': '?',
        '＼': '\\',
        '｜': '|',
        '～': '~',
        '！': '!',
    }

    # Replace special characters with regular counterparts
    return input_string.translate(str.maketrans(special_characters_mapping))

# Revert from string
def revert_escape_characters(text):
    # Define the regex pattern to match \\n, \\t, and \\r
    pattern = r'\\(n|t|r)'
    
    # Define a dictionary to map escape sequences to their corresponding characters
    replacements = {'n': '\n', 't': '   ', 'r': '\r'}
    
    # Use re.sub() to replace escape sequences with their corresponding characters
    replaced_text = re.sub(pattern, lambda match: replacements.get(match.group(1)), text)
    
    return replaced_text

# Convert to string
def convert_escape_characters(text):
    # Define the regex pattern to match newline, tab, and carriage return characters
    pattern = r'(\n|\t|\r)'
    
    # Define a dictionary to map characters to their corresponding escape sequences
    replacements = {'\n': '\\n', '\t': '\\t', '\r': '\\r'}
    
    # Use re.sub() to replace newline, tab, and carriage return characters with their escape sequences
    reverted_text = re.sub(pattern, lambda match: replacements.get(match.group(1)), text)
    
    return reverted_text

# Remove from text
def remove_escape_characters(text):
    # Define the regex pattern to match newline, tab, and carriage return characters
    pattern = r'(\n|\t|\r)'
    
    # Define a dictionary to map characters to their corresponding escape sequences
    replacements = {'\n': '', '\t': '', '\r': ''}
    
    # Use re.sub() to replace newline, tab, and carriage return characters with their escape sequences
    reverted_text = re.sub(pattern, lambda match: replacements.get(match.group(1)), text)
    
    return reverted_text

def splitlines_keep_linebreak(text):
    lines = []
    current_line = ''
    for char in text:
        if char == '\n':
            lines.append(current_line + '\n')  # Include '\n' at the end of each line
            current_line = ''
        else:
            current_line += char
    if current_line:
        lines.append(current_line + '\n')  # Include '\n' for the last line
    return lines

# Constants
DATA_TYPE_NAMES = 1
DATA_TYPE_NAMES2 = 2
DATA_TYPE_WORDS = 3
DATA_TYPE_DICTS = 4
DATA_TYPE_OTHERS = 5

# Mapping dictionary
data_type_mapping = {
    DATA_TYPE_NAMES: "Names",
    DATA_TYPE_NAMES2: "Names2",
    DATA_TYPE_WORDS: "Words",
    DATA_TYPE_DICTS: "Dicts",
    DATA_TYPE_OTHERS: "Others"
}

data_type_update = {
    DATA_TYPE_NAMES: "Names",
    DATA_TYPE_NAMES2: "Names2",
    DATA_TYPE_WORDS: "Words"
}

DATA_MEANS_TYPE_VIETPHRASE_NAMES = 1
DATA_MEANS_TYPE_VIETPHRASE_WORDS = 2
DATA_MEANS_TYPE_LACVIET = 3
DATA_MEANS_TYPE_THIEUCHUU = 4

z_data_names = get_data("zh_names.csv")
z_data_names2 = get_data("zh_names2.csv")
z_data_words = get_data("zh_words.csv")
z_data_dicts = get_data("zh_dicts.csv")
z_data_means_lacviet = get_data("zh_means_lacviet.csv")
z_data_means_thieuchu = get_data("zh_means_thieuchuu.csv")

z_data_names_local = []
z_data_names2_local = []
z_data_words_local = []
z_data_dicts_local = []

z_data_search = ZData()
z_data_search_update = ZData()
z_data_means = ZDataMeans()

def update_data_csv(data_type, data_ids, txt_trung, txt_viet):
    global z_data_names_local
    global z_data_names2_local
    global z_data_words_local
    global z_data_names
    global z_data_names2
    global z_data_words

    local_id = -1
    global_id = -1

    if data_ids:
        local_id = int(data_ids[0][0])
        global_id = int(data_ids[0][1])
        #print(f"data_type = {data_type}, local_id = {local_id}, global_id = {global_id}")

    if data_type == DATA_TYPE_NAMES:
        if data_ids:
            z_data_names_local[local_id][1] = txt_viet
            z_data_names[global_id][1] = txt_viet
        else:
            z_data_names_local.append([txt_trung, txt_viet, len(z_data_names)])
            z_data_names.append([txt_trung, txt_viet, len(z_data_names)])
        save_data("zh_names.csv", z_data_names)

    elif data_type == DATA_TYPE_NAMES2:
        if data_ids:
            z_data_names2_local[local_id][1] = txt_viet
            z_data_names2[global_id][1] = txt_viet
        else:
            z_data_names2_local.append([txt_trung, txt_viet, len(z_data_names2)])
            z_data_names2.append([txt_trung, txt_viet, len(z_data_names2)])
        save_data("zh_names2.csv", z_data_names2)

    elif data_type == DATA_TYPE_WORDS:
        if data_ids:
            z_data_words_local[local_id][1] = txt_viet
            z_data_words[global_id][1] = txt_viet
        else:
            z_data_words_local.append([txt_trung, txt_viet, len(z_data_words)])
            z_data_words.append([txt_trung, txt_viet, len(z_data_words)])
        save_data("zh_words.csv", z_data_words)

def delete_data_csv(data_type, data_ids):
    global z_data_names_local
    global z_data_names2_local
    global z_data_words_local
    global z_data_names
    global z_data_names2
    global z_data_words

    local_id = -1
    global_id = -1

    if data_ids:
        local_id = int(data_ids[0][0])
        global_id = int(data_ids[0][1])
        print(f"data_type = {data_type}, local_id = {local_id}, global_id = {global_id}")

    if data_type == DATA_TYPE_NAMES:
        if data_ids:
            z_data_names_local.pop(local_id)
            z_data_names.pop(global_id)
            save_data("zh_names.csv", z_data_names)

    elif data_type == DATA_TYPE_NAMES2:
        if data_ids:
            z_data_names2_local.pop(local_id)
            z_data_names2.pop(global_id)
            save_data("zh_names2.csv", z_data_names2)

    elif data_type == DATA_TYPE_WORDS:
        if data_ids:
            z_data_words_local.pop(local_id)
            z_data_words.pop(global_id)
            save_data("zh_words.csv", z_data_words)

def get_data_search(txt_trung):
    # Initialize ZData
    data_search = ZData()

    # Search string using local data to increase perfomance
    data_search.push_data(txt_trung, z_data_names_local, DATA_TYPE_NAMES)
    data_search.push_data(txt_trung, z_data_names2_local, DATA_TYPE_NAMES2)
    data_search.push_data(txt_trung, z_data_words_local, DATA_TYPE_WORDS)
    data_search.push_data(txt_trung, z_data_dicts_local, DATA_TYPE_DICTS)

    # Sort & then clean duplicate words
    data_search.clean_duplicate()

    # Update 'HAN' word into searched data
    data_search.update_dicts(z_data_dicts)

    # Add other chars not in any original data.csv & sort again
    data_search.push_other_chars(txt_trung, DATA_TYPE_OTHERS)

    return data_search

def get_data_means(txt_trung):
    # Make new local meaning dictionary (Vietphrase, Lac Viet, Thieu Chuu) for this text
    data_means = ZDataMeans()

    data_means.push_data(txt_trung, z_data_names_local, DATA_MEANS_TYPE_VIETPHRASE_NAMES);
    data_means.push_data(txt_trung, z_data_names2_local, DATA_MEANS_TYPE_VIETPHRASE_NAMES);
    data_means.push_data(txt_trung, z_data_words_local, DATA_MEANS_TYPE_VIETPHRASE_WORDS);
    data_means.push_data(txt_trung, z_data_means_lacviet, DATA_MEANS_TYPE_LACVIET);
    data_means.push_data(txt_trung, z_data_means_thieuchu, DATA_MEANS_TYPE_THIEUCHUU);

    data_means.clean_duplicate()

    return data_means

# Translate function
def translate(txt_trung):
    global z_data_names_local
    global z_data_names2_local
    global z_data_words_local
    global z_data_dicts_local
    global z_data_search
    global z_data_means

    txt_han = ""
    txt_viet = ""

    try:
        # Check if Chinese text is not empty
        if txt_trung:
            # Get local data from data.csv to use for this context
            z_data_names_local = get_data_local(txt_trung, z_data_names, DATA_TYPE_NAMES)
            z_data_names2_local = get_data_local(txt_trung, z_data_names2, DATA_TYPE_NAMES2)
            z_data_words_local = get_data_local(txt_trung, z_data_words, DATA_TYPE_WORDS)
            z_data_dicts_local = get_data_local(txt_trung, z_data_dicts, DATA_TYPE_DICTS)

            z_data_search = get_data_search(txt_trung)
            z_data_means = get_data_means(txt_trung)            
            
            # Get Han Viet translation
            txt_han, txt_viet = z_data_search.get_han_viet()
        else:
            messagebox.showinfo("Error", "Please enter Chinese text.")
    except Exception as e:
        print(f"An error occurred in translate(): {e}")
        
    return to_sentence_case(txt_han), to_sentence_case(txt_viet)

# Quick translate function, only using local data from the previous translate
def quick_translate(txt_trung, is_translate=True):
    global z_data_search
    global z_data_search_update
    global z_data_means

    txt_han = ""
    txt_viet = ""

    try:
        # Check if Chinese text is not empty
        if txt_trung:
            # Initialize ZData
            data_search = get_data_search(txt_trung)
            
            # Get Han Viet translation
            txt_han, txt_viet = data_search.get_han_viet()
        else:
            messagebox.showinfo("Error", "Please enter Chinese text.")
    except Exception as e:
        print(f"An error occurred in translate(): {e}")
        
    if is_translate:
        z_data_search = data_search
        z_data_means = get_data_means(txt_trung)
        txt_han = to_sentence_case(txt_han)
        txt_viet = to_sentence_case(txt_viet)
    else:
        z_data_search_update = data_search
        txt_han = txt_han.strip()
        txt_viet = txt_viet.strip()

    return txt_han, txt_viet
