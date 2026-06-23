# -*- coding: utf-8 -*-
import os

hmi_tags_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags.xml"

if not os.path.exists(hmi_tags_path):
    print(f"Error: {hmi_tags_path} not found!")
    exit(1)

print("Reading Screen1_HMI_Tags.xml...")
with open(hmi_tags_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace "SignedDWord" with "None"
print("Replacing 'SignedDWord' with 'None'...")
content = content.replace("<Coding>SignedDWord</Coding>", "<Coding>None</Coding>")

print("Writing patched XML back...")
with open(hmi_tags_path, "w", encoding="utf-8") as f:
    f.write(content)

print("[PASS] Successfully updated coding values to 'None' in Screen1_HMI_Tags.xml")
