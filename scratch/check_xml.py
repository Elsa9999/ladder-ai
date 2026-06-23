import xml.etree.ElementTree as ET
import os

xml_path = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\active_screen_2_export.xml"
print("File exists:", os.path.exists(xml_path))

tree = ET.parse(xml_path)
root = tree.getroot()
print("Root tag:", root.tag)

# Find all tags in the document to see what they are
tags = set()
for elem in root.iter():
    # remove namespace
    t = elem.tag.split("}")[-1]
    tags.add(t)
print("Tags in XML:", sorted(list(tags)))

# Let's count elements of type ScreenItem, TextField, IOField, etc.
for t in ["IOField", "TextField", "Button", "Circle"]:
    count = 0
    for elem in root.iter():
        if elem.tag.endswith(t):
            count += 1
    print(f"Count of {t}: {count}")
