import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os


def browse_files():
    """
    Allows the user to select multiple files, which are then added to the Listbox.
    """
    filepaths = filedialog.askopenfilenames(title="Select one or more files")
    if filepaths:
        for fp in filepaths:
            file_listbox.insert(tk.END, fp)


def remove_selected_files():
    """
    Removes the selected (highlighted) files from the Listbox.
    """
    # Get currently selected indices in ascending order
    selection = file_listbox.curselection()
    # We remove from the end to the beginning to avoid reindexing issues
    for index in reversed(selection):
        file_listbox.delete(index)


def browse_destination():
    """
    Lets the user pick a destination folder using a directory chooser.
    """
    folderpath = filedialog.askdirectory(title="Select Destination Folder")
    if folderpath:
        dest_var.set(folderpath)


def move_files():
    """
    Moves each file in the Listbox to the selected destination folder.
    If any move fails, that file is noted, and the script continues with the rest.
    """
    destination = dest_var.get().strip()
    if not destination:
        messagebox.showerror("Error", "Please select a destination folder.")
        return

    # Get all file paths from the Listbox
    all_files = file_listbox.get(0, tk.END)
    if not all_files:
        messagebox.showerror("Error", "No files selected to move.")
        return

    failed_moves = []

    for src in all_files:
        # Make sure the file still exists before moving
        if not os.path.isfile(src):
            failed_moves.append(f"(Missing file) {src}")
            continue
        try:
            filename = os.path.basename(src)
            destination_path = os.path.join(destination, filename)

            # Example check: If a file with the same name already exists in destination
            # (You can skip or rename or confirm with the user. Here we overwrite.)
            if os.path.exists(destination_path):
                # Overwrite or skip—this is your design choice
                # For now, let's just overwrite:
                os.remove(destination_path)

            shutil.move(src, destination_path)
        except Exception as e:
            # If this file fails, collect error info and move on
            failed_moves.append(f"{src}\n  Error: {e}")

    if failed_moves:
        # If some files failed, show them in a single message
        msg = "The following files could not be moved:\n\n" + "\n\n".join(failed_moves)
        messagebox.showerror("Some Moves Failed", msg)
    else:
        # If none failed, show success
        messagebox.showinfo(
            "Success", f"Successfully moved {len(all_files)} file(s) to:\n{destination}"
        )

    # Clear the Listbox after attempts
    file_listbox.delete(0, tk.END)


# --- GUI Setup ---
root = tk.Tk()
root.title("Multiple File Mover")
root.resizable(False, False)

# Frame to hold source file selection
file_frame = tk.LabelFrame(root, text="Source Files", padx=5, pady=5)
file_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Listbox to display selected files
file_listbox = tk.Listbox(file_frame, width=60, height=8, selectmode=tk.MULTIPLE)
file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar for the Listbox
scrollbar = tk.Scrollbar(file_frame, orient=tk.VERTICAL, command=file_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
file_listbox.config(yscrollcommand=scrollbar.set)

# Button to browse for files
browse_button = tk.Button(root, text="Add Files...", command=browse_files)
browse_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")

# Button to remove selected files from the list
remove_button = tk.Button(root, text="Remove Selected", command=remove_selected_files)
remove_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")

# Destination folder section
dest_frame = tk.Frame(root)
dest_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

dest_var = tk.StringVar()
dest_label = tk.Label(dest_frame, text="Destination Folder:")
dest_label.pack(side=tk.LEFT)

dest_entry = tk.Entry(dest_frame, textvariable=dest_var, width=40)
dest_entry.pack(side=tk.LEFT, padx=5)

browse_dest_button = tk.Button(dest_frame, text="Browse...", command=browse_destination)
browse_dest_button.pack(side=tk.LEFT)

# Button to move all files
move_button = tk.Button(root, text="Move Files", command=move_files, width=20)
move_button.grid(row=4, column=0, pady=10)

root.mainloop()
