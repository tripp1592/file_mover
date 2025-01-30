import os
import sys
import hashlib
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog


def compute_md5(filepath):
    """
    Compute the MD5 hash of a file. Returns the hex digest string.
    If the file can't be read, returns None.
    """
    try:
        md5_obj = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_obj.update(chunk)
        return md5_obj.hexdigest()
    except Exception:
        return None


def move_file_with_md5(src, dst):
    """
    Move a single file from src to dst, verifying MD5 before/after.
    Also handles filename collisions:
      - If file already exists at dst, ask user: Overwrite or Rename?

    Returns:
      None if success, or an error string if something went wrong.
    """
    # 1) Check source MD5
    src_hash = compute_md5(src)
    if src_hash is None:
        return f"Failed to compute MD5 for source: {src}"

    # 2) If destination exists, ask user Overwrite or Rename
    if os.path.exists(dst):
        action = messagebox.askyesno(
            "File Exists",
            f"The file:\n{dst}\nalready exists in the destination.\n\n"
            "Click YES to Overwrite, NO to Rename.",
        )
        if action is True:
            # Overwrite
            try:
                os.remove(dst)
            except Exception as e:
                return f"Failed to remove existing file: {dst}\n  {e}"
        else:
            # Rename
            filename = os.path.basename(src)
            new_name = simpledialog.askstring(
                "Rename File", "Enter a new filename (no path):", initialvalue=filename
            )
            if not new_name:
                # user hit cancel or provided empty -> skip
                return f"User skipped renaming for {src}"
            dst = os.path.join(os.path.dirname(dst), new_name)
            if os.path.exists(dst):
                # If the new name also exists, skip or prompt again
                return f"Renamed destination also exists! Skipping: {dst}"

    # 3) Perform the move
    try:
        shutil.move(src, dst)
    except Exception as e:
        return f"Error moving file {src} -> {dst}\n  {e}"

    # 4) Check MD5 of destination
    dst_hash = compute_md5(dst)
    if dst_hash is None:
        return f"Failed to compute MD5 for destination: {dst}"

    # 5) Compare
    if src_hash != dst_hash:
        return (
            f"MD5 mismatch after moving:\n"
            f"  Source MD5: {src_hash}\n"
            f"  Dest   MD5: {dst_hash}\n"
            f"Files may be corrupted or changed."
        )

    # If no issues, return None
    return None


def move_files():
    """
    Moves each file in the Listbox to the selected destination folder
    using MD5 checks and collision handling.
    """
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

        filename = os.path.basename(src)
        dst_path = os.path.join(destination, filename)

        error = move_file_with_md5(src, dst_path)
        if error:
            failed_moves.append(error)

    if failed_moves:
        msg = "Some files could not be moved or had errors:\n\n" + "\n\n".join(
            failed_moves
        )
        messagebox.showerror("Move Errors", msg)
    else:
        messagebox.showinfo(
            "Success",
            f"All files moved successfully and passed MD5 checks.\nDestination: {destination}",
        )

    # Clear the list after attempts
    file_listbox.delete(0, tk.END)


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
    selection = file_listbox.curselection()
    for index in reversed(selection):
        file_listbox.delete(index)


def browse_destination():
    """
    Lets the user pick a destination folder using a directory chooser.
    """
    folderpath = filedialog.askdirectory(title="Select Destination Folder")
    if folderpath:
        dest_var.set(folderpath)


# -------------------- MAIN GUI Setup --------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("My File Mover")
    root.resizable(False, False)

    file_frame = tk.LabelFrame(root, text="Source Files", padx=5, pady=5)
    file_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    file_listbox = tk.Listbox(file_frame, width=60, height=8, selectmode=tk.MULTIPLE)
    file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(file_frame, orient=tk.VERTICAL, command=file_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    file_listbox.config(yscrollcommand=scrollbar.set)

    browse_button = tk.Button(root, text="Add Files...", command=browse_files)
    browse_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    remove_button = tk.Button(
        root, text="Remove Selected", command=remove_selected_files
    )
    remove_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")

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

    move_button = tk.Button(root, text="Move Files", command=move_files, width=20)
    move_button.grid(row=4, column=0, pady=10)

    root.mainloop()
