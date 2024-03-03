import tkinter as tk
from tkinter import ttk

def display_table(data):     
    if not data:
        return
    
    # Create the Tkinter root window
    root = tk.Tk()
    root.title("Table Example")
    
    # Create a container to hold the canvas and scrollbar
    container = tk.Frame(root)
    container.pack(expand=True, fill=tk.BOTH)
    
    # Create a canvas to hold the table
    canvas = tk.Canvas(container)
    canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
    
    # Create a scrollbar for the canvas
    scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Configure the canvas to use the scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Create the table inside the canvas
    table = tk.Frame(canvas, bg="white")
    canvas.create_window((0, 0), window=table, anchor=tk.NW)
    
    # Function to update the scroll region
    def update_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    # Bind the canvas to the scroll region update function
    table.bind("<Configure>", update_scroll_region)
    
    # Create table headers
    headers = list(data[0].keys())
    for i, header in enumerate(headers):
        header_label = tk.Label(table, text=header, padx=10, pady=5, borderwidth=1, relief=tk.RAISED, bg="#f0f0f0", font=("Arial", 10, "bold"))
        header_label.grid(row=0, column=i, sticky="nsew")

    # Insert data into the table
    for i, row_data in enumerate(data):
        for j, key in enumerate(headers):
            value = row_data[key]
            cell = tk.Label(table, text=value, padx=10, pady=5, borderwidth=1, relief=tk.RIDGE, bg="white", font=("Arial", 10))
            cell.grid(row=i+1, column=j, sticky="nsew")

    # Configure column weights to allow resizing
    for i in range(len(headers)):
        table.grid_columnconfigure(i, weight=1)
    
    # Function to scroll the canvas when the mouse wheel is scrolled
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # Bind the mouse wheel event to the canvas
    canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    root.mainloop()
    
def display_table_no_header(data):     
    if not data:
        return
    
    # Create the Tkinter root window
    root = tk.Tk()
    root.title("Table Example")
    
    # Create a container to hold the canvas and scrollbar
    container = tk.Frame(root)
    container.pack(expand=True, fill=tk.BOTH)
    
    # Create a canvas to hold the table
    canvas = tk.Canvas(container)
    canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
    
    # Create a scrollbar for the canvas
    scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Configure the canvas to use the scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Create the table inside the canvas
    table = tk.Frame(canvas, bg="white")
    canvas.create_window((0, 0), window=table, anchor=tk.NW)
    
    # Function to update the scroll region
    def update_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    # Bind the canvas to the scroll region update function
    table.bind("<Configure>", update_scroll_region)
    
    # Insert data into the table
    for i, row_data in enumerate(data):
        for j, value in enumerate(row_data):
            cell = tk.Label(table, text=value, padx=10, pady=5, borderwidth=1, relief=tk.RIDGE, bg="white", font=("Arial", 10))
            cell.grid(row=i, column=j, sticky="nsew")

    # Configure column weights to allow resizing
    num_columns = len(data[0])  # Assuming all rows have the same number of columns
    for i in range(num_columns):
        table.grid_columnconfigure(i, weight=1)
    
    # Function to scroll the canvas when the mouse wheel is scrolled
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # Bind the mouse wheel event to the canvas
    canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    root.mainloop()
