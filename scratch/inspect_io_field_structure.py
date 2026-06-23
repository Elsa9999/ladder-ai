# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Screen_2.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

io_field = None
for elem in root.iter():
    if elem.tag.endswith("IOField"):
        io_field = elem
        break

if io_field is not None:
    object_list = io_field.find("ObjectList")
    if object_list is not None:
        for obj in object_list:
            print(f"Child Tag: {obj.tag} | ID: {obj.get('ID')} | Composition: {obj.get('CompositionName')}")
            # If it's a Property, print its name and children
            if obj.tag.endswith("Property"):
                name_el = obj.find("AttributeList/Name")
                name_val = name_el.text if name_el is not None else ""
                print(f"  Property Name: {name_val}")
                for sub in obj.iter():
                    if sub.tag.endswith("TagConnectionDynamic"):
                        tag_name_el = sub.find(".//Name")
                        tag_name = tag_name_el.text if tag_name_el is not None else ""
                        print(f"    TagConnectionDynamic Name: {tag_name}")
else:
    print("No IOField found!")
