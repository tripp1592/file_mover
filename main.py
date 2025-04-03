import hashlib
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import json
from pathlib import Path
import sys

# Constants
RECENT_DESTINATIONS_FILE = "recent_destinations.json"
MAX_RECENT_DESTINATIONS = 5

def load_recent_destinations():
    """Load recently used destination folders from JSON file."""
    try:
        if os.path.exists(RECENT_DESTINATIONS_FILE):
            with open(RECENT_DESTINATIONS_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_recent_destinations(destinations):
    """Save recently used destination folders to JSON file."""
    try:
        with open(RECENT_DESTINATIONS_FILE, 'w') as f:
            json.dump(destinations, f)
    except Exception:
        pass

def get_free_space(path):
    """Get free space in bytes for the given path."""
    try:
        return shutil.disk_usage(path).free
    except Exception:
        return 0

def format_size(size_bytes):
    """Format size in bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

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

    # Check total size of files to move
    total_size = sum(os.path.getsize(f) for f in all_files if os.path.isfile(f))
    free_space = get_free_space(destination)
    
    if total_size > free_space:
        msg = (f"Not enough free space in destination folder.\n"
               f"Required: {format_size(total_size)}\n"
               f"Available: {format_size(free_space)}")
        messagebox.showerror("Error", msg)
        return

    # Create progress window
    progress_window = tk.Toplevel(root)
    progress_window.title("Moving Files")
    progress_window.transient(root)
    progress_window.grab_set()
    
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(
        progress_window, 
        variable=progress_var,
        maximum=len(all_files)
    )
    progress_bar.pack(padx=10, pady=10, fill=tk.X)
    
    status_label = tk.Label(progress_window, text="")
    status_label.pack(pady=5)

    failed_moves = []
    for i, src in enumerate(all_files):
        if not os.path.isfile(src):
            failed_moves.append(f"(Missing file) {src}")
            continue

        filename = os.path.basename(src)
        dst_path = os.path.join(destination, filename)
        
        status_label.config(text=f"Moving: {filename}")
        progress_var.set(i)
        progress_window.update()

        error = move_file_with_md5(src, dst_path)
        if error:
            failed_moves.append(error)

    progress_window.destroy()

    if failed_moves:
        msg = "Some files could not be moved or had errors:\n\n" + "\n\n".join(failed_moves)
        messagebox.showerror("Move Errors", msg)
    else:
        # Update recent destinations
        recent = load_recent_destinations()
        if destination in recent:
            recent.remove(destination)
        recent.insert(0, destination)
        recent = recent[:MAX_RECENT_DESTINATIONS]
        save_recent_destinations(recent)
        
        messagebox.showinfo(
            "Success",
            f"All files moved successfully and passed MD5 checks.\nDestination: {destination}"
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
    folder_path = filedialog.askdirectory(title="Select Destination Folder")
    if folder_path:
        dest_var.set(folder_path)


# -------------------- MAIN GUI Setup --------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("My File Mover")
    root.resizable(False, False)

    # Handle command line arguments (files from context menu)
    if len(sys.argv) > 1:
        # Bring window to front
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(root.attributes, '-topmost', False)
        
        # Add files from command line
        for filepath in sys.argv[1:]:
            # Handle quoted paths
            filepath = filepath.strip('"')
            if os.path.isfile(filepath):
                file_listbox.insert(tk.END, filepath)
            elif os.path.isdir(filepath):
                # If it's a directory, add all files in it
                for root_dir, _, files in os.walk(filepath):
                    for file in files:
                        full_path = os.path.join(root_dir, file)
                        file_listbox.insert(tk.END, full_path)

    file_frame = tk.LabelFrame(root, text="Source Files", padx=5, pady=5)
    file_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    file_listbox = tk.Listbox(file_frame, width=60, height=8, selectmode=tk.MULTIPLE)
    file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(file_frame, orient=tk.VERTICAL, command=file_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    file_listbox.config(yscrollcommand=scrollbar.set)

    browse_button = tk.Button(root, text="Add Files... (Ctrl+O)", command=browse_files)
    browse_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    remove_button = tk.Button(
        root, text="Remove Selected (Del)", command=remove_selected_files
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

    # Add recent destinations menu
    recent_menu = tk.Menubutton(dest_frame, text="Recent")
    recent_menu.pack(side=tk.LEFT, padx=5)
    recent_menu.menu = tk.Menu(recent_menu, tearoff=0)
    recent_menu["menu"] = recent_menu.menu

    def update_recent_menu():
        recent_menu.menu.delete(0, tk.END)
        for dest in load_recent_destinations():
            recent_menu.menu.add_command(
                label=dest,
                command=lambda d=dest: dest_var.set(d)
            )

    update_recent_menu()

    move_button = tk.Button(root, text="Move Files (Ctrl+M)", command=move_files, width=20)
    move_button.grid(row=4, column=0, pady=10)

    root.mainloop()