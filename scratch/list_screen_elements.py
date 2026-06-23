# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens\Hmi.Screen.Screen_2.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

print("--- SCREEN ELEMENTS ---")
counts = {}
for elem in root.iter():
    tag = elem.tag.split('}')[-1] # Remove namespace if any
    counts[tag] = counts.get(tag, 0) + 1
    
    # If it is a screen item, print its name
    if "ScreenItems" in elem.get("CompositionName", ""):
        name_el = elem.find("AttributeList/ObjectName")
        name = name_el.text if name_el is not None else "Unknown"
        left_el = elem.find("AttributeList/Left")
        left = left_el.text if left_el is not None else "0"
        top_el = elem.find("AttributeList/Top")
        top = top_el.text if top_el is not None else "0"
        print(f"Object: {tag:25} | Name: {name:30} | Pos: ({left}, {top})")

print("\n--- TAG COUNTS ---")
for tag, count in counts.items():
    print(f"  {tag}: {count}")
