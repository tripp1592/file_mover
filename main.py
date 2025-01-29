import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil


def browse_files():
    """Allows the user to select multiple files to add to the Listbox."""
    filepaths = filedialog.askopenfilenames(title="Select one or more files")
    if filepaths:
        for fp in filepaths:
            file_listbox.insert(tk.END, fp)


def remove_selected_files():
    """Removes the selected (highlighted) files from the Listbox."""
    selection = file_listbox.curselection()
    for index in reversed(selection):
        file_listbox.delete(index)


def browse_destination():
    """Lets the user pick a destination folder using a directory chooser."""
    folderpath = filedialog.askdirectory(title="Select Destination Folder")
    if folderpath:
        dest_var.set(folderpath)


def move_files():
    """Moves each file in the Listbox to the selected destination folder."""
    destination = dest_var.get().strip()
    if not destination:
        messagebox.showerror("Error", "Please select a destination folder.")
        return

    all_files = file_listbox.get(0, tk.END)
    if not all_files:
        messagebox.showerror("Error", "No files selected to move.")
        return

    failed_moves = []
    for src in all_files:
        if not os.path.isfile(src):
            failed_moves.append(f"(Missing file) {src}")
            continue
        try:
            filename = os.path.basename(src)
            destination_path = os.path.join(destination, filename)
            if os.path.exists(destination_path):
                # Overwrite or handle collision
                os.remove(destination_path)
            shutil.move(src, destination_path)
        except Exception as e:
            failed_moves.append(f"{src}\n  Error: {e}")

    if failed_moves:
        msg = "Some files could not be moved:\n\n" + "\n\n".join(failed_moves)
        messagebox.showerror("Some Moves Failed", msg)
    else:
        messagebox.showinfo(
            "Success", f"Successfully moved {len(all_files)} file(s) to:\n{destination}"
        )
    # Clear after moving
    file_listbox.delete(0, tk.END)


def main():
    """Main entry point: parse any command-line arg, build the GUI, etc."""
    # 1) If Explorer passed us a file/folder path, figure out the default directory
    if len(sys.argv) > 1:
        clicked_path = sys.argv[1]
    else:
        clicked_path = ""

    if os.path.isfile(clicked_path):
        default_dir = os.path.dirname(clicked_path)
    elif os.path.isdir(clicked_path):
        default_dir = clicked_path
    else:
        default_dir = os.getcwd()  # fallback

    # 2) Build the main Tkinter window
    global root  # if needed for references
    root = tk.Tk()
    root.title("Multiple File Mover")
    root.resizable(False, False)

    # 3) Create the UI
    global file_listbox, dest_var

    # Frame to hold source file selection
    file_frame = tk.LabelFrame(root, text="Source Files", padx=5, pady=5)
    file_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    file_listbox = tk.Listbox(file_frame, width=60, height=8, selectmode=tk.MULTIPLE)
    file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(file_frame, orient=tk.VERTICAL, command=file_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    file_listbox.config(yscrollcommand=scrollbar.set)

    # Optionally, auto-insert the clicked file into the Listbox
    if os.path.isfile(clicked_path):
        file_listbox.insert(tk.END, clicked_path)

    # Button to browse for files
    browse_button = tk.Button(root, text="Add Files...", command=browse_files)
    browse_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    # Button to remove selected
    remove_button = tk.Button(
        root, text="Remove Selected", command=remove_selected_files
    )
    remove_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")

    # Destination folder
    dest_frame = tk.Frame(root)
    dest_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

    dest_var = tk.StringVar()
    dest_label = tk.Label(dest_frame, text="Destination Folder:")
    dest_label.pack(side=tk.LEFT)

    dest_entry = tk.Entry(dest_frame, textvariable=dest_var, width=40)
    dest_entry.pack(side=tk.LEFT, padx=5)

    browse_dest_button = tk.Button(
        dest_frame, text="Browse...", command=browse_destination
    )
    browse_dest_button.pack(side=tk.LEFT)

    # Move button
    move_button = tk.Button(root, text="Move Files", command=move_files, width=20)
    move_button.grid(row=4, column=0, pady=10)

    # 4) If you want the "Add Files..." dialog to open automatically in default_dir:
    #    (Optional convenience feature, can remove if not needed)
    root.after(200, lambda: filedialog.askopenfilenames(initialdir=default_dir))

    # 5) Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main()
