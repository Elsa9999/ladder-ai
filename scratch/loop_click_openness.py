# -*- coding: utf-8 -*-
import ctypes
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

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
        # Click Yes (usually index 0) and Yes to all (usually index 1)
        for btn in children[:2]:
            print(f"Clicking button HWND {btn}")
            PostMessage(btn, BM_CLICK, 0, 0)
            time.sleep(0.1)
        return True
    return False

print("=== Starting Loop Click Openness ===")
try:
    while True:
        dialog_hwnd = None
        EnumWindows(EnumWindowsProc(find_dialog), 0)
        if dialog_hwnd is not None:
            print(f"Found TIA Openness dialog HWND: {dialog_hwnd}")
            time.sleep(0.5)  # Wait for dialog to initialize
            if click_dialog_buttons(dialog_hwnd):
                print("Dialog access accepted successfully!")
                time.sleep(2.0)  # Sleep longer after successful click to avoid multiple clicks
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Loop terminated by user.")
except Exception as ex:
    print(f"Error: {ex}")
