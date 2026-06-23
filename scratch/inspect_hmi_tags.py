# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai1\HMI\AI_HMI_Tags.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

print("--- HMI TAGS ---")
for tag in root.findall(".//{http://www.siemens.com/automation/Openness/Attributes}Tag") or root.findall(".//Hmi.Tag.Tag"):
    name_el = tag.find(".//Name") or tag.find("./AttributeList/Name")
    name = name_el.text if name_el is not None else "Unknown"
    
    comment_el = tag.find(".//Comment//Text") or tag.find(".//MultilingualTextItem/AttributeList/Text")
    comment = comment_el.text if comment_el is not None else ""
    
    type_el = tag.find(".//DataType/Name") or tag.find(".//LinkList/DataType/Name")
    type_val = type_el.text if type_el is not None else ""
    
    print(f"Tag: {name:30} | Type: {type_val:10} | Comment: {comment}")
