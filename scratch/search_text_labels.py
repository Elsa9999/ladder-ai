# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys
import os

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Man Tong Quan.xml"

if not os.path.exists(xml_path):
    print(f"File not found: {xml_path}")
    sys.exit(1)

tree = ET.parse(xml_path)
root = tree.getroot()

found = 0
for elem in root.iter():
    # Search in all text attributes or text elements
    if elem.text and ("32" in elem.text or "33" in elem.text or "Bon" in elem.text or "Bồn" in elem.text or "FT" in elem.text or "LT" in elem.text):
        path = []
        curr = elem
        # trace path
        # print
        print(f"Found match: '{elem.text}' in tag {elem.tag}")
        found += 1

print(f"Total matching elements: {found}")
