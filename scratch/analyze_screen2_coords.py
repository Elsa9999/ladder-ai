# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Screen_2.xml"

if not os.path.exists(xml_path):
    print(f"[ERROR] XML file not found at {xml_path}")
    exit(1)

ET.register_namespace('', '')
tree = ET.parse(xml_path)
root = tree.getroot()

layer = root.find(".//Hmi.Screen.ScreenLayer")
if layer is None:
    print("[ERROR] Layer not found!")
    exit(1)

object_list = layer.find("ObjectList")
if object_list is None:
    print("[ERROR] ObjectList of Layer not found!")
    exit(1)

min_y = 9999
max_y = 0
min_x = 9999
max_x = 0

elements_count = 0

for item in object_list:
    attr_list = item.find("AttributeList")
    if attr_list is not None:
        left_el = attr_list.find("Left")
        top_el = attr_list.find("Top")
        width_el = attr_list.find("Width")
        height_el = attr_list.find("Height")
        name_el = attr_list.find("ObjectName")
        
        if left_el is not None and top_el is not None:
            left = int(left_el.text)
            top = int(top_el.text)
            width = int(width_el.text) if width_el is not None else 0
            height = int(height_el.text) if height_el is not None else 0
            name = name_el.text if name_el is not None else item.tag
            
            # Skip the main background GraphicView which spans 1920x1080
            if name == "Graphic view_1" and left == 0 and top == 0:
                continue
                
            elements_count += 1
            if top < min_y:
                min_y = top
            if (top + height) > max_y:
                max_y = top + height
            if left < min_x:
                min_x = left
            if (left + width) > max_x:
                max_x = left + width
                
            print(f"Element: {name} | Left={left}, Top={top}, Width={width}, Height={height}")

print("\n=== SUMMARY OF COORDINATES ===")
print(f"Total active elements analyzed: {elements_count}")
print(f"Horizontal bounds: X = {min_x} to {max_x}")
print(f"Vertical bounds:   Y = {min_y} to {max_y}")
