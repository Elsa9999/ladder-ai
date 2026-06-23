# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens\Hmi.Screen.Screen_2.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

cultures = {}
for elem in root.iter():
    if elem.tag.endswith("Culture"):
        culture = elem.text
        cultures[culture] = cultures.get(culture, 0) + 1

print("--- ACTIVE CULTURES IN SCREEN_2 XML ---")
for c, count in cultures.items():
    print(f"Culture: {c} | Count: {count}")
