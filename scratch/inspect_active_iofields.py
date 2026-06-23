# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\active_screen_2_export.xml"
if not os.path.exists(xml_path):
    print(f"File not found: {xml_path}")
    sys.exit(1)

tree = ET.parse(xml_path)
root = tree.getroot()

io_fields = []
for elem in root.iter():
    if elem.tag.endswith("IOField"):
        io_fields.append(elem)

print(f"Found {len(io_fields)} IOFields in active screen export:\n")

for io in io_fields:
    attrs = io.find("AttributeList")
    obj_name = attrs.find("ObjectName").text if attrs.find("ObjectName") is not None else "Unknown"
    left = attrs.find("Left").text if attrs.find("Left") is not None else "N/A"
    top = attrs.find("Top").text if attrs.find("Top") is not None else "N/A"
    width = attrs.find("Width").text if attrs.find("Width") is not None else "N/A"
    height = attrs.find("Height").text if attrs.find("Height") is not None else "N/A"
    fp = attrs.find("FormatPattern").text if attrs.find("FormatPattern") is not None else "None"
    mode = attrs.find("Mode").text if attrs.find("Mode") is not None else "None"
    
    # Bound tag
    tag_name = "None"
    objs = io.find("ObjectList")
    if objs is not None:
        for prop in objs.findall(".//Hmi.Screen.Property") + objs.findall(".//Property"):
            pname = prop.find("AttributeList/Name")
            if pname is not None and pname.text == "ProcessValue":
                # Find tag connection
                tag_conn = prop.find(".//Hmi.Dynamic.TagConnectionDynamic") or prop.find(".//TagConnectionDynamic")
                if tag_conn is not None:
                    tag_el = tag_conn.find(".//Tag")
                    if tag_el is not None:
                        name_el = tag_el.find("Name")
                        if name_el is not None:
                            tag_name = name_el.text

    print(f"Name: {obj_name}")
    print(f"  Pos: Left={left}, Top={top}, Width={width}, Height={height}")
    print(f"  FormatPattern: {fp}")
    print(f"  Mode: {mode}")
    print(f"  Bound Tag: {tag_name}")
    print("-" * 40)
