import win32com.client
import os

path = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Siemens Automation\TIA Portal V18.lnk"

if os.path.exists(path):
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(path)
        print("Shortcut Target Path:", shortcut.TargetPath)
        print("Shortcut Arguments:", shortcut.Arguments)
    except Exception as e:
        print("Error resolving shortcut:", e)
else:
    print("Shortcut not found.")
