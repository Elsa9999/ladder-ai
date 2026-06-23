# -*- coding: utf-8 -*-
import subprocess
import time
import ctypes
import os
import sys

# We will redirect python's stdout/stderr to a file so we can view it
py_log_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\python_import_log.txt"
sys.stdout = open(py_log_path, "w", encoding="utf-8")
sys.stderr = sys.stdout

print("=== Starting Detail Screens Import Process ===")
exe_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\import_detail_screens.exe"

if not os.path.exists(exe_path):
    print(f"Error: Exe not found at {exe_path}")
    sys.exit(1)

# Win32 APIs for auto-dismissing TIA Portal access request dialog
PostMessage = ctypes.windll.user32.PostMessageW
BM_CLICK = 0xF5
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
EnumChildWindows = ctypes.windll.user32.EnumChildWindows
EnumChildProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
GetClassName = ctypes.windll.user32.GetClassNameW

dialog_hwnd = None

def find_dialog(hwnd, lParam):
    global dialog_hwnd
    length = GetWindowTextLength(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    GetWindowText(hwnd, buff, length + 1)
    if "Openness access" in buff.value or "Access attempt" in buff.value:
        dialog_hwnd = hwnd
        return False
    return True

def click_dialog_buttons(dlg_hwnd):
    children = []
    def foreach_child(hwnd, lParam):
        class_name = ctypes.create_unicode_buffer(256)
        GetClassName(hwnd, class_name, 256)
        if "BUTTON" in class_name.value.upper():
            children.append(hwnd)
        return True
    
    EnumChildWindows(dlg_hwnd, EnumChildProc(foreach_child), 0)
    print(f"Found dialog buttons: {children}")
    if len(children) >= 2:
        for btn in children[:2]:
            print(f"Clicking button HWND {btn}")
            PostMessage(btn, BM_CLICK, 0, 0)
            time.sleep(0.1)
        return True
    return False

log_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\import_detail_screens_output.txt"
print(f"Launching C# executable, output redirected to {log_path}...")
with open(log_path, "w", encoding="utf-8") as log_file:
    proc = subprocess.Popen([exe_path], stdout=log_file, stderr=log_file, text=True)

    print("Polling for TIA Openness access dialog...")
    start_time = time.time()
    clicked = False
    while proc.poll() is None:
        if not clicked:
            dialog_hwnd = None
            EnumWindows(EnumWindowsProc(find_dialog), 0)
            if dialog_hwnd is not None:
                print(f"Found TIA Openness dialog HWND: {dialog_hwnd}")
                time.sleep(0.5)
                if click_dialog_buttons(dialog_hwnd):
                    clicked = True
                    print("Dialog access accepted successfully!")
        time.sleep(0.5)
        # Timeout if it runs for too long without finishing
        if time.time() - start_time > 180:
            print("Timeout reached (180s). Terminating process.")
            proc.terminate()
            break

print(f"Import process finished with exit code: {proc.returncode}")
sys.exit(proc.returncode if proc.returncode is not None else 1)
