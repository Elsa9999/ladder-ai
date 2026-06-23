# -*- coding: utf-8 -*-
import os

hmi_tags_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags.xml"

if not os.path.exists(hmi_tags_path):
    print(f"Error: {hmi_tags_path} not found!")
    exit(1)

print("Reading Screen1_HMI_Tags.xml...")
with open(hmi_tags_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace "None" value in LogicalAddress, StartValue, and SubstituteValue
print("Replacing 'None' with empty tags...")
content = content.replace("<LogicalAddress>None</LogicalAddress>", "<LogicalAddress />")
content = content.replace("<StartValue>None</StartValue>", "<StartValue />")
content = content.replace("<SubstituteValue>None</SubstituteValue>", "<SubstituteValue />")

print("Writing patched XML back...")
with open(hmi_tags_path, "w", encoding="utf-8") as f:
    f.write(content)

print("[PASS] Successfully removed 'None' values from Screen1_HMI_Tags.xml")
