import os
import sys
import winreg
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def add_context_menu():
    # Get the path to the executable
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        exe_path = sys.executable
    else:
        # Running as script
        exe_path = sys.executable

    # Create the registry entries
    try:
        # For files
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\MoveWithFileMover") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "Move with File Mover")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, r"%SystemRoot%\System32\shell32.dll,145")

        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\MoveWithFileMover\command") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, f'"{exe_path}" "%V"')

        # For directories
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\MoveWithFileMover") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "Move with File Mover")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, r"%SystemRoot%\System32\shell32.dll,145")

        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\MoveWithFileMover\command") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, f'"{exe_path}" "%V"')

        print("Context menu integration added successfully!")
    except Exception as e:
        print(f"Error adding context menu: {e}")

def remove_context_menu():
    try:
        # Remove file entries
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\MoveWithFileMover\command")
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\MoveWithFileMover")

        # Remove directory entries
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\MoveWithFileMover\command")
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\MoveWithFileMover")

        print("Context menu integration removed successfully!")
    except Exception as e:
        print(f"Error removing context menu: {e}")

if __name__ == "__main__":
    if not is_admin():
        print("This script requires administrator privileges.")
        print("Please run it as administrator.")
        sys.exit(1)

    action = input("Enter 'add' to add context menu or 'remove' to remove it: ").lower()
    if action == 'add':
        add_context_menu()
    elif action == 'remove':
        remove_context_menu()
    else:
        print("Invalid action. Please enter 'add' or 'remove'.") 