# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens\Hmi.Screen.Screen_2.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

print("--- VISIBILITY ANIMATIONS IN SCREEN_2 ---")
for elem in root.iter():
    if elem.tag.endswith("VisibilityAnimation"):
        # Find the parent element to see what object it is applied to
        parent = None
        # Let's search up or check name
        parent_name = ""
        # Let's find the ObjectName of the parent (which is usually two levels up)
        # We can find this by iterating or searching for parent.
        # But we can just find what element contains this VisibilityAnimation.
        
        # Let's find the tag of the Hmi tag used in the trigger
        tag_name_el = elem.find(".//Tag/Name")
        tag_name = tag_name_el.text if tag_name_el is not None else ""
        
        visible_el = elem.find(".//Visible")
        visible_val = visible_el.text if visible_el is not None else ""
        
        range_start_el = elem.find(".//RangeStart")
        range_start = range_start_el.text if range_start_el is not None else ""
        
        range_end_el = elem.find(".//RangeEnd")
        range_end = range_end_el.text if range_end_el is not None else ""
        
        print(f"Visibility Animation ID: {elem.get('ID')} | Tag: {tag_name:20} | Visible: {visible_val:5} | Range: {range_start} - {range_end}")

print("\n--- DETAILED OBJECT LIST ---")
for elem in root.iter():
    # Print elements that have a VisibilityAnimation in their ObjectList
    objs = elem.find("ObjectList")
    if objs is not None:
        vis = objs.find(".//Hmi.Dynamic.VisibilityAnimation")
        if vis is not None:
            name_el = elem.find("AttributeList/ObjectName")
            obj_name = name_el.text if name_el is not None else "Unknown"
            print(f"Object: {elem.tag:30} | Name: {obj_name:30} | ID: {elem.get('ID')}")
