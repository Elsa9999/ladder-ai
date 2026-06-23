# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

filename = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Screen_2.xml"
print(f"--- Checking limits in {filename} ---")
tree = ET.parse(filename)
root = tree.getroot()

found_limits = []
for elem in root.iter():
    if elem.tag == "Hmi.Dynamic.Range":
        attrs = elem.find("AttributeList")
        if attrs is not None:
            low = attrs.find("LowerLimit").text if attrs.find("LowerLimit") is not None else "N/A"
            high = attrs.find("UpperLimit").text if attrs.find("UpperLimit") is not None else "N/A"
            found_limits.append((low, high))

print("Found Range limits: ", found_limits)
