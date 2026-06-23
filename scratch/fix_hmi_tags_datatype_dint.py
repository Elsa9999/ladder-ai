# -*- coding: utf-8 -*-
import os

hmi_tags_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags.xml"

if not os.path.exists(hmi_tags_path):
    print(f"Error: {hmi_tags_path} not found!")
    exit(1)

print("Reading Screen1_HMI_Tags.xml...")
with open(hmi_tags_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace <Name>Time</Name> with <Name>DInt</Name>
print("Replacing '<Name>Time</Name>' with '<Name>DInt</Name>'...")
content = content.replace("<Name>Time</Name>", "<Name>DInt</Name>")

print("Writing patched XML back...")
with open(hmi_tags_path, "w", encoding="utf-8") as f:
    f.write(content)

print("[PASS] Successfully updated datatype 'Time' to 'DInt' in Screen1_HMI_Tags.xml")
