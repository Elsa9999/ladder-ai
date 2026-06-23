import ctypes
import time

PostMessage = ctypes.windll.user32.PostMessageW
BM_CLICK = 0xF5
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202

dialog_hwnd = None
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
EnumChildWindows = ctypes.windll.user32.EnumChildWindows
EnumChildProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
GetClassName = ctypes.windll.user32.GetClassNameW

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

children = []
def foreach_child(hwnd, lParam):
    class_name = ctypes.create_unicode_buffer(256)
    GetClassName(hwnd, class_name, 256)
    if "BUTTON" in class_name.value.upper():
        children.append(hwnd)
    return True

EnumChildWindows(dialog_hwnd, EnumChildProc(foreach_child), 0)

print(f"Found {len(children)} buttons: {children}")

if len(children) >= 2:
    # Button 1 is usually Yes, Button 2 is usually Yes to all
    # We will post BM_CLICK to both to be sure!
    for btn in children[:2]:
        print(f"Posting click to button HWND {btn}")
        PostMessage(btn, BM_CLICK, 0, 0)
        time.sleep(0.1)
    print("Clicks posted successfully!")
else:
    print("Not enough buttons found.")
