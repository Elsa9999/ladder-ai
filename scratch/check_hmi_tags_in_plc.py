# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os

plc1_tags_path = r"D:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\output\PLC_Tags_PLC1.xml"
plc2_tags_path = r"D:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\output\PLC_Tags_PLC2.xml"
hmi_tags_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags.xml"

def parse_plc_tags(path):
    tags = {}
    if not os.path.exists(path):
        return tags
    tree = ET.parse(path)
    root = tree.getroot()
    for tag_el in root.iter():
        if tag_el.tag.endswith("SW.Tags.PlcTag"):
            name = tag_el.find(".//{*}Name").text
            dtype = tag_el.find(".//{*}DataTypeName").text
            tags[name] = dtype
    return tags

plc1_tags = parse_plc_tags(plc1_tags_path)
plc2_tags = parse_plc_tags(plc2_tags_path)

# Parse HMI tags
hmi_tags = {}
tree = ET.parse(hmi_tags_path)
root = tree.getroot()
for tag_el in root.iter():
    if tag_el.tag.endswith("Hmi.Tag.Tag"):
        name = tag_el.find("AttributeList/Name").text
        conn = tag_el.find("LinkList/Connection/Name").text
        hmi_tags[name] = conn

print(f"Total HMI tags: {len(hmi_tags)}")

missing = 0
for name, conn in sorted(hmi_tags.items()):
    if conn == "HMI_Connection_1":
        if name not in plc1_tags:
            print(f"  [MISSING] {name} (PLC1) not found in PLC1 tag table!")
            missing += 1
    elif conn == "HMI_Connection_2":
        if name not in plc2_tags:
            print(f"  [MISSING] {name} (PLC2) not found in PLC2 tag table!")
            missing += 1

print(f"Total missing: {missing}")
