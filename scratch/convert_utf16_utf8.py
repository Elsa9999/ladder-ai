# -*- coding: utf-8 -*-
import sys

utf16_file = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_tags_in_project.txt"
utf8_file = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_tags_utf8.txt"

try:
    with open(utf16_file, "r", encoding="utf-16-le") as f:
        content = f.read()
    
    with open(utf8_file, "w", encoding="utf-8") as f:
        f.write(content)
    print("Conversion successful.")
except Exception as e:
    print(f"Error during conversion: {e}")
