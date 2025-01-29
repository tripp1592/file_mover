# MyFileMover

**MyFileMover** is a simple Python‐based GUI tool that helps you move multiple files to a destination folder. You can launch it by double‐clicking the EXE, or integrate it into the Windows Explorer context menu so it appears when you right‐click a file or folder.

## Features

1. **Add Files**  
   - Browse and select multiple files to move, listed in a `Listbox`.
2. **Remove Selected Files**  
   - Easily remove files from the selection list if you change your mind.
3. **Destination Folder**  
   - Choose a target directory for moving your files.
4. **Move**  
   - Moves all files in one shot, with basic error handling and a final success/failure message.
5. **Context Menu Integration** *(optional)*  
   - Right‐click on any file or folder → **MyFileMover**  
   - The app will open with that file or folder ready to go.

## Requirements

- **Python 3.7+** (if you run the script directly without building an EXE).
- **Tkinter** (usually included with standard Python on Windows).
- **PyInstaller** (if you want a single‐file EXE).

## Getting Started

### 1. Clone or Download

```bash
git clone https://github.com/yourusername/MyFileMover.git
cd MyFileMover
```

### 2. (Optional) Create a Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

If you’re just running the Python script:

```bash
pip install -r requirements.txt
```

*(If `requirements.txt` doesn’t exist, install `pyinstaller` separately if you want to build an EXE.)*

### 4. Run the Script Directly (Developer Mode)

```bash
python main.py
```

This should launch the Tkinter GUI. Use **Add Files** to select items, choose **Destination**, and click **Move Files**.

## Building an EXE

1. **Install PyInstaller** (if not already):
   ```bash
   pip install pyinstaller
   ```

2. **Compile**:
   ```bash
   pyinstaller --onefile --name MyFileMover main.py
   ```

3. **Find the EXE** in the `dist/` folder:
   - `dist/MyFileMover.exe`

4. You can run `MyFileMover.exe` directly from `dist/` or copy it anywhere you like.

## Context Menu Integration

If you’d like **MyFileMover** to appear when you right‐click a file or folder in Windows Explorer:

1. **Build** the EXE (see above) so the script runs without needing Python installed.
2. **Edit or create** a `.reg` file (e.g. `AddMyFileMover.reg`) with content like this:

   ```reg
   Windows Registry Editor Version 5.00

   [HKEY_CLASSES_ROOT\*\shell\MyFileMover]
   @="MyFileMover"

   [HKEY_CLASSES_ROOT\*\shell\MyFileMover\command]
   @="\"H:\\path\\to\\MyFileMover.exe\" \"%1\""

   [HKEY_CLASSES_ROOT\\Directory\\shell\\MyFileMover]
   @="MyFileMover"

   [HKEY_CLASSES_ROOT\\Directory\\shell\\MyFileMover\\command]
   @="\"H:\\path\\to\\MyFileMover.exe\" \"%1\""
   ```
   - Replace `H:\\path\\to\\MyFileMover.exe` with the **actual** location of your EXE.  
   - Note the **double backslashes** in `.reg` files.

3. **Double‐click** the `.reg` file to merge it into the registry.  
4. **Right‐click** any file or folder → **MyFileMover**.  
5. The GUI will launch, and if you clicked on a file, it auto‐detects that file’s directory for convenience.

> **Note**: On Windows 11, the context menu item may appear under “Show more options” by default.

## How It Works

1. **Command‐Line Argument**  
   - When launched via Explorer’s context menu, `%1` is passed to the EXE, which is read via `sys.argv[1]`.
   - If it’s a file, we derive the parent directory; if it’s a folder, we use that folder path.

2. **Tkinter GUI**  
   - The main window has a `Listbox` for selected files, plus options to browse for more files, remove any, select a destination folder, and move files.

3. **Moving Files**  
   - We use `shutil.move(src, dest)` under the hood.  
   - If collisions occur, we currently overwrite, but you can customize that behavior.

4. **Error Handling**  
   - Missing files or permissions issues are logged, and we keep going with the rest of the list.

## Troubleshooting

- **Multiple Instances**: On older Windows versions (or certain Explorer configurations), multi‐selecting files can trigger multiple EXE instances if you use the standard registry approach. For a single instance with multiple files, consider using “Send To” integration or a custom shell extension.
- **Path Escapes**: In `.reg` files, remember to escape backslashes (`\\`) and wrap paths with quotes if they contain spaces.
- **No Icon**: If you want a custom icon for the EXE, add `--icon=icon.ico` to your PyInstaller command.

## License

*(Choose and insert your preferred license, e.g. MIT, Apache, etc.)*

---

That’s it! You now have a straightforward **Multiple File Mover** with a GUI, plus an optional Explorer **context menu** integration for quick access. Feel free to open issues or submit PRs if you encounter any problems.