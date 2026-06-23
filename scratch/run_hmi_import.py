# -*- coding: utf-8 -*-
import subprocess
import time
import ctypes
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

exe_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\import_stage2_hmi.exe"

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
    # TIA Portal access dialog contains "Openness access" or "Siemens"
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
        # Button 1 is usually Yes, Button 2 is usually Yes to all
        for btn in children[:2]:
            print(f"Clicking button HWND {btn}")
            PostMessage(btn, BM_CLICK, 0, 0)
            time.sleep(0.1)
        return True
    return False

# Launch import_stage2_hmi.exe in background
print("=== Starting HMI Import Process ===")
proc = subprocess.Popen([exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")

# Poll for Openness access dialog
print("Polling for TIA Openness access dialog...")
start_time = time.time()
clicked = False
while proc.poll() is None:
    if not clicked:
        dialog_hwnd = None
        EnumWindows(EnumWindowsProc(find_dialog), 0)
        if dialog_hwnd is not None:
            print(f"Found TIA Openness dialog HWND: {dialog_hwnd}")
            time.sleep(0.5) # Wait for dialog to initialize
            if click_dialog_buttons(dialog_hwnd):
                clicked = True
                print("Dialog access accepted successfully!")
    time.sleep(0.5)
    # Timeout if it runs for too long without finishing
    if time.time() - start_time > 180:
        print("Timeout reached (180s). Terminating process.")
        proc.terminate()
        break

# Capture output
stdout, stderr = proc.communicate()
print("\n=== HMI Import Process Output ===")
print(stdout)
if stderr:
    print("=== HMI Import Process Errors ===")
    print(stderr)

sys.exit(proc.returncode if proc.returncode is not None else 1)
