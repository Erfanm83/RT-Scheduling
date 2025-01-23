import tkinter as tk
from tkinter import ttk

# Binary sources
binary_sources = [
    [3, 3],
    [2, 5],
    [4, 10],
    [2, 2]
]

# Tables
tables = {
    "First table": [
        ["T11", 4, 1, 1, 0, 1],
        ["T12", 4, 2, 3, 2, 1],
        ["T13", 2, 3, 3, 4, 1]
    ],
    "Second table": [
        ["T21", 4, 2, 3, 5]
    ],
    "Third table": [
        ["T31", 2, 21, 3, 4, 10]
    ],
    "Fourth table": [
        ["T41", 2, 2, 1, 5, "T42"],
        ["T42", 4, 2, 2, 7, "-"]
    ]
}

def submit_form():
    # Get binary sources
    for i in range(4):
        source = binary_source_entries[i].get()
        binary_sources[i] = list(map(int, source.split()))

    # Get tables
    for table_name in tables.keys():
        tables[table_name].clear()
        rows = table_entries[table_name].get("1.0", tk.END).strip().split("\n")
        for row in rows:
            tables[table_name].append(row.split())

    root.destroy()

root = tk.Tk()
root.title("User Input Form")

binary_source_entries = []
for i in range(4):
    tk.Label(root, text=f"Binary source {i+1} (format: x y):").grid(row=i, column=0)
    entry = tk.Entry(root)
    entry.grid(row=i, column=1)
    binary_source_entries.append(entry)

table_entries = {}
row_offset = 4
for table_name in tables.keys():
    tk.Label(root, text=f"{table_name} (format: Txx x x x x x, one per line):").grid(row=row_offset, column=0, columnspan=2)
    text = tk.Text(root, height=5, width=40)
    text.grid(row=row_offset+1, column=0, columnspan=2)
    table_entries[table_name] = text
    row_offset += 6

submit_button = tk.Button(root, text="Submit", command=submit_form)
submit_button.grid(row=row_offset, column=0, columnspan=2)

root.mainloop()
