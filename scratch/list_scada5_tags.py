# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys
import os

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens\Hmi.Screen.scadabai5.xml"

if not os.path.exists(xml_path):
    print(f"File not found: {xml_path}")
    sys.exit(1)

tree = ET.parse(xml_path)
root = tree.getroot()

tags = []
for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    if tag_local == "Tag":
        name_el = elem.find("Name")
        if name_el is not None:
            tags.append(name_el.text)

print(f"Total tags: {len(tags)}")
print("First 20 tags:")
for t in tags[:20]:
    print(f"  - {t}")
