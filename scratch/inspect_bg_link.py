# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens\Hmi.Screen.Screen_2.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

for elem in root.iter():
    if elem.tag.endswith("GraphicView"):
        name_el = elem.find("AttributeList/ObjectName")
        obj_name = name_el.text if name_el is not None else ""
        
        picture_name_el = elem.find(".//Picture/Name")
        pic_name = picture_name_el.text if picture_name_el is not None else "None"
        
        print(f"GraphicView Name: {obj_name} | Linked Picture: {pic_name}")
