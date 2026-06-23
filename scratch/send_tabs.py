# -*- coding: utf-8 -*-
import ctypes
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Find Openness access
dialog_hwnd = None
def find_dialog(hwnd, lParam):
    global dialog_hwnd
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
    if "Openness access" in buff.value:
        dialog_hwnd = hwnd
        return False
    return True

ctypes.windll.user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(find_dialog), 0)

if dialog_hwnd is None:
    print("Dialog not found")
    sys.exit(0)

print(f"Found dialog HWND {dialog_hwnd}")
ctypes.windll.user32.ShowWindow(dialog_hwnd, 9)
time.sleep(0.1)
ctypes.windll.user32.SetForegroundWindow(dialog_hwnd)
time.sleep(0.5)

# Virtual Keys
VK_TAB = 0x09
VK_SPACE = 0x20
VK_RETURN = 0x0D
VK_LEFT = 0x25
KEYEVENTF_KEYUP = 0x0002

def press_key(key):
    ctypes.windll.user32.keybd_event(key, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(key, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)

# Try Tab then Space
print("Sending Tab, then Space...")
press_key(VK_TAB)
time.sleep(0.2)
press_key(VK_SPACE)

# Try Left, Left then Space (in case focus was on No, which is typically on the right)
print("Sending Left, Left, then Space...")
press_key(VK_LEFT)
time.sleep(0.1)
press_key(VK_LEFT)
time.sleep(0.2)
press_key(VK_SPACE)

# Try Enter
print("Sending Enter...")
press_key(VK_RETURN)

print("Finished sending keys.")
