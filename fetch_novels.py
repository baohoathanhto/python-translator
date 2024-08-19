import tkinter as tk
import ttkbootstrap as ttkb
import requests
from bs4 import BeautifulSoup
import translator

class Fetchtitles(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Fetch titles")
        self.wm_state('zoomed') 

        self.setup_gui()
        self.setup_bindings()

        # Define custom headers with a user agent
        self.HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36'
        }

        self.z_titles = []
        self.z_chapters = []

        # Fetch title info and populate the title Treeview
        self.fetch_titles()

    def setup_gui(self):
        # Frame container
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Create URL textbox
        self.url_label = ttkb.Label(self.container, text="URL:")
        self.url_entry = ttkb.Entry(self.container, width=55)

        # Create search textbox
        self.search_label = ttkb.Label(self.container, text="Search:")
        self.search_entry = ttkb.Entry(self.container, width=55)

        # Create title Treeview
        self.titles_tree = ttkb.Treeview(self.container, height=35)
        self.titles_tree.heading("#0", text="title Titles")
        self.titles_tree.column("#0", width=200)

        # Create chapters Treeview
        self.chapters_tree = ttkb.Treeview(self.container, height=35)
        self.chapters_tree.heading("#0", text="Chapters")
        self.chapters_tree.column("#0", width=200)

        # Create canvas for displaying pictures
        self.vietnamese_textbox = ttkb.ScrolledText(self.container, width=136, spacing1=5, spacing2=5, wrap="word")

        # Setup layout
        self.url_label.grid(row=0, column=0, padx=(10,5), pady=(10,5), sticky="e")
        self.url_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=(10,5), sticky="w")
        self.search_label.grid(row=1, column=0, padx=(10,5), pady=5, sticky="e")
        self.search_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        self.titles_tree.grid(row=2, column=0, columnspan=2, padx=(10,5), pady=(5,10), sticky="ns")
        self.chapters_tree.grid(row=2, column=2, padx=5, pady=(5,10), sticky="ns")
        self.vietnamese_textbox.grid(row=0, column=3, rowspan=3, padx=(5,10), pady=10, sticky="nswe")

    def setup_bindings(self):
        self.titles_tree.bind("<<TreeviewSelect>>", self.fetch_chapters)
        self.chapters_tree.bind("<<TreeviewSelect>>", self.fetch_content)

        self.titles_tree.bind("<Button-3>", lambda event: self.copy_item_text(event, self.titles_tree))
        self.chapters_tree.bind("<Button-3>", lambda event: self.copy_item_text(event, self.chapters_tree))

    def copy_item_text(self, event, tree):
        # Get the item ID under the cursor
        item_id = tree.identify_row(event.y)

        # Get the text of the item
        item_text = tree.item(item_id, "text")

        # Copy the text to the clipboard
        self.clipboard_clear()
        self.clipboard_append(item_text)
        print("Copied item text:", item_text)

    def fetch_titles(self):
        # URL of the title page on blogtruyen.vn
        url = 'https://www.piaotia.com/booksort/0/1.html'

        # Send an HTTP GET request to the title page with custom headers
        response = requests.get(url, headers=self.HEADERS)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the title page
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all <td> elements with class="odd"
            title_list = soup.find_all('td', class_='odd')

            # Iterate over the <td> elements
            for title in title_list:
                # Find <a> tags within the <td> element
                a_tags = title.find_all('a')
                
                # If <a> tags are found
                if a_tags:
                    # Iterate over the <a> tags
                    for a_tag in a_tags:
                        # Extract href attribute and text content of the <a> tag
                        href = a_tag['href']
                        text = a_tag.text.strip().replace('<br/>', '\n')

                        self.z_titles.append({'href': href, 'text': text})
                        self.titles_tree.insert('', 'end', text=text)
        else:
            print('Failed to retrieve titles. Status code:', response.status_code)

    def fetch_chapters(self, event):
        self.chapters_tree.delete(*self.chapters_tree.get_children())
        self.z_chapters = []

        # Get the selected item in the titles_tree Treeview
        selected_item = self.titles_tree.selection()[0]
        
        # Get the text of the selected item
        selected_text = self.titles_tree.item(selected_item, 'text')
        
        # Find the corresponding <a> tag in the HTML content
        for index, title in enumerate(self.z_titles):
            if selected_text == title['text']:
                url = title['href'].replace('bookinfo', 'html').replace('.html', '/')
                response = requests.get(url, headers=self.HEADERS)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    chapter_list = soup.find_all('li')

                    for chapter in chapter_list:
                        a_tags = chapter.find_all('a')
                        
                        if a_tags:
                            for a_tag in a_tags:
                                href = url + a_tag['href']
                                text = a_tag.text.strip()

                                self.z_chapters.append({'title_index': index, 'href': href, 'text': text})
                                self.chapters_tree.insert('', 'end', text=text)
                else:
                    print('Failed to retrieve chapters. Status code:', response.status_code)

                break # Found title

    def fetch_content(self, event):
        self.vietnamese_textbox.delete("1.0", tk.END)

        # Get the selected item in the chapters_tree Treeview
        selected_item = self.chapters_tree.selection()[0]
        
        # Get the text of the selected item
        selected_text = self.chapters_tree.item(selected_item, 'text')
        
        # Find the corresponding <a> tag in the HTML content
        for chapter in self.z_chapters:
            if selected_text == chapter['text']:
                url = chapter['href']
                response = requests.get(url, headers=self.HEADERS)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    #content = soup.find('html')

                    # Find the <h1> tag
                    h1_tag = soup.find('h1')

                    # Initialize the text content
                    text_content = ''

                    # Start from <h1> tag and iterate over its siblings and descendants
                    if h1_tag:
                        for tag in h1_tag.find_next_siblings():
                            print(tag.name)
                            if tag.name == 'center':
                                print("tag: ", tag.content)
                                break  # Stop iteration when reaching the target tag
                            text_content += tag.get_text(separator='\n')

                    txt_han, txt_viet = translator.translate(text_content)
                    self.vietnamese_textbox.insert("1.0", txt_viet)
                else:
                    print('Failed to retrieve content. Status code:', response.status_code)

                break # Found chapter

    def process_text(self, input_text):
        lines = input_text.splitlines()
        cleaned_lines = [line for line in lines if line.strip()]
        processed_text = '\n\n'.join(cleaned_lines)
        return processed_text

if __name__ == "__main__":
    app = Fetchtitles()
    app.mainloop()
