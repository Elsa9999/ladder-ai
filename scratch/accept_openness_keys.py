import ctypes
import time

dialog_hwnd = None
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)

def find_dialog(hwnd, lParam):
    global dialog_hwnd
    length = GetWindowTextLength(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    GetWindowText(hwnd, buff, length + 1)
    if "Openness access" in buff.value:
        dialog_hwnd = hwnd
        return False
    return True

EnumWindows(EnumWindowsProc(find_dialog), 0)

if dialog_hwnd is None:
    print("Openness access dialog not found.")
    exit(0)

print(f"Found Openness access dialog: HWND {dialog_hwnd}")
ctypes.windll.user32.ShowWindow(dialog_hwnd, 9) # Restore if minimized
ctypes.windll.user32.SetForegroundWindow(dialog_hwnd)
time.sleep(0.5)

# Send Alt+A (Yes to All)
# Alt (0x12) down, A (0x41) down, A up, Alt up
ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)
time.sleep(0.05)
ctypes.windll.user32.keybd_event(0x41, 0, 0, 0)
time.sleep(0.05)
ctypes.windll.user32.keybd_event(0x41, 0, 2, 0)
time.sleep(0.05)
ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)
time.sleep(0.2)

# Just in case, send Alt+Y (Yes)
# Alt (0x12) down, Y (0x59) down, Y up, Alt up
ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)
time.sleep(0.05)
ctypes.windll.user32.keybd_event(0x59, 0, 0, 0)
time.sleep(0.05)
ctypes.windll.user32.keybd_event(0x59, 0, 2, 0)
time.sleep(0.05)
ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)

print("Keys sent!")
