import ctypes
import time

EnumChildWindows = ctypes.windll.user32.EnumChildWindows
EnumChildProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
GetClassName = ctypes.windll.user32.GetClassNameW
SendMessage = ctypes.windll.user32.SendMessageW
BM_CLICK = 0xF5

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)

dialog_hwnd = None

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

children = []
def foreach_child(hwnd, lParam):
    length = GetWindowTextLength(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    GetWindowText(hwnd, buff, length + 1)
    class_name = ctypes.create_unicode_buffer(256)
    GetClassName(hwnd, class_name, 256)
    children.append((hwnd, buff.value, class_name.value))
    return True

EnumChildWindows(dialog_hwnd, EnumChildProc(foreach_child), 0)

buttons = [hwnd for hwnd, text, cls in children if "BUTTON" in cls.upper()]
print(f"Found buttons: {buttons}")
if len(buttons) >= 2:
    ctypes.windll.user32.SetForegroundWindow(dialog_hwnd)
    time.sleep(0.2)
    for btn in buttons:
        # Click all button HWNDs to ensure 'Yes' or 'Yes to all' is triggered
        print(f"Clicking button HWND {btn}")
        SendMessage(btn, BM_CLICK, 0, 0)
        time.sleep(0.1)
    print("Clicked successfully!")
else:
    print("Not enough buttons found.")
