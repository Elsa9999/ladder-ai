# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

input_xml = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Screen_2.xml"

if not os.path.exists(input_xml):
    print(f"[ERROR] Source XML not found: {input_xml}")
    exit(1)

tree = ET.parse(input_xml)
root = tree.getroot()

print("--- TEXT FIELDS ---")
for elem in root.iter():
    if elem.tag.endswith("TextField"):
        name = elem.find(".//ObjectName")
        name_val = name.text if name is not None else ""
        left = elem.find(".//Left")
        left_val = left.text if left is not None else ""
        top = elem.find(".//Top")
        top_val = top.text if top is not None else ""
        
        # Get text content
        text_el = elem.find(".//Text")
        text_val = ""
        if text_el is not None:
            text_val = "".join(text_el.itertext())
        
        print(f"Name: {name_val:30} | Pos: ({left_val}, {top_val}) | Text: {text_val.strip()}")

print("\n--- IO FIELDS ---")
for elem in root.iter():
    if elem.tag.endswith("IOField"):
        name = elem.find(".//ObjectName")
        name_val = name.text if name is not None else ""
        left = elem.find(".//Left")
        left_val = left.text if left is not None else ""
        top = elem.find(".//Top")
        top_val = top.text if top is not None else ""
        
        # Tag connection
        tag_conn = elem.find(".//Hmi.Dynamic.TagConnectionDynamic")
        tag_name = ""
        if tag_conn is not None:
            tag_name_el = tag_conn.find(".//Name")
            if tag_name_el is not None:
                tag_name = tag_name_el.text
        
        print(f"Name: {name_val:30} | Pos: ({left_val}, {top_val}) | Tag: {tag_name}")
