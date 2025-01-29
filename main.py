import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os


def browse_files():
    """
    Opens a file dialog that allows the user to select multiple files.
    The chosen files are added to the Listbox for display.
    """
    filepaths = filedialog.askopenfilenames(title="Select one or more files")
    # `filepaths` is a tuple of selected file paths
    if filepaths:
        for fp in filepaths:
            file_listbox.insert(tk.END, fp)


def browse_destination():
    """
    Opens a folder dialog for the user to pick a destination folder.
    """
    folderpath = filedialog.askdirectory(title="Select Destination Folder")
    if folderpath:
        dest_var.set(folderpath)


def move_files():
    """
    Moves each file in the Listbox to the selected destination folder.
    """
    dst = dest_var.get()
    if not dst:
        messagebox.showerror("Error", "Please select a destination folder.")
        return

    # Get all file paths from the Listbox
    all_files = file_listbox.get(0, tk.END)
    if not all_files:
        messagebox.showerror("Error", "No files selected to move.")
        return

    # Move each file
    for src in all_files:
        try:
            filename = os.path.basename(src)
            destination_path = os.path.join(dst, filename)
            shutil.move(src, destination_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not move {src}:\n{e}")
            return

    messagebox.showinfo("Success", f"Moved {len(all_files)} file(s) to:\n{dst}")

    # Clear the Listbox after moving
    file_listbox.delete(0, tk.END)


# Create the main window
root = tk.Tk()
root.title("Multiple File Mover")
root.resizable(False, False)

# Destination folder path variable
dest_var = tk.StringVar()

# Frame for file selection
file_frame = tk.LabelFrame(root, text="Source Files", padx=5, pady=5)
file_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Listbox to show selected files
file_listbox = tk.Listbox(file_frame, width=60, height=8, selectmode=tk.MULTIPLE)
file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar for the Listbox
scrollbar = tk.Scrollbar(file_frame, orient=tk.VERTICAL, command=file_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
file_listbox.config(yscrollcommand=scrollbar.set)

# Button to browse and select multiple files
browse_button = tk.Button(root, text="Browse Files...", command=browse_files)
browse_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")

# Frame for destination selection
dest_frame = tk.Frame(root)
dest_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

dest_label = tk.Label(dest_frame, text="Destination Folder:")
dest_label.pack(side=tk.LEFT)

dest_entry = tk.Entry(dest_frame, textvariable=dest_var, width=40)
dest_entry.pack(side=tk.LEFT, padx=5)

browse_dest_button = tk.Button(dest_frame, text="Browse...", command=browse_destination)
browse_dest_button.pack(side=tk.LEFT)

# Move button
move_button = tk.Button(root, text="Move Files", command=move_files, width=20)
move_button.grid(row=3, column=0, pady=10)

root.mainloop()
