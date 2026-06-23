# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

xml_path = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\scadabai3_export.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

def get_local_tag(elem):
    return elem.tag.split("}")[-1]

for elem in root.iter():
    tag = get_local_tag(elem)
    if tag.endswith("GraphicView"):
        name_el = elem.find(".//ObjectName") or elem.find("./AttributeList/ObjectName")
        name = name_el.text if name_el is not None else "Unknown"
        
        pic_el = elem.find(".//Picture") or elem.find("./AttributeList/Picture")
        pic = pic_el.text.strip() if pic_el is not None and pic_el.text else "NONE"
        
        left_el = elem.find(".//Left") or elem.find("./AttributeList/Left")
        top_el = elem.find(".//Top") or elem.find("./AttributeList/Top")
        left = left_el.text if left_el is not None else "0"
        top = top_el.text if top_el is not None else "0"
        
        print(f"Name: {name:25s} | Pos: ({left:>4s}, {top:>4s}) | Picture: {pic}")
