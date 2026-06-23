# -*- coding: utf-8 -*-
import ctypes
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible

dialog_hwnd = None

def find_dialog(hwnd, lParam):
    global dialog_hwnd
    if IsWindowVisible(hwnd):
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        if "Openness access" in buff.value:
            dialog_hwnd = hwnd
            print(f"Found dialog: HWND {hwnd}, Title: '{buff.value}'")
            return False
    return True

EnumWindows(EnumWindowsProc(find_dialog), 0)

if dialog_hwnd is None:
    print("Openness dialog not found.")
    sys.exit(0)

# Bring to foreground
ctypes.windll.user32.ShowWindow(dialog_hwnd, 9) # SW_RESTORE
time.sleep(0.1)
ctypes.windll.user32.SetForegroundWindow(dialog_hwnd)
time.sleep(0.5)

# Try Alt+A (Yes to All) and Alt+Y (Yes)
VK_MENU = 0x12 # Alt
VK_A = 0x41
VK_Y = 0x59
KEYEVENTF_KEYUP = 0x0002

def send_key_combo(modifier, key):
    ctypes.windll.user32.keybd_event(modifier, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(key, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(key, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(modifier, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)

print("Sending Alt+A...")
send_key_combo(VK_MENU, VK_A)

time.sleep(0.5)
# If Alt+A didn't work, maybe Alt+Y
print("Sending Alt+Y...")
send_key_combo(VK_MENU, VK_Y)

print("Key sending sequence completed.")
