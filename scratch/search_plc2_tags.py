# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

plc2_xml = r"D:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\output\PLC_Tags_PLC2.xml"
if not os.path.exists(plc2_xml):
    print("PLC_Tags_PLC2.xml not found")
    sys.exit(1)

tree = ET.parse(plc2_xml)
root = tree.getroot()

print("Tags in PLC 2:")
found = 0
for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    if tag_local.endswith("PlcTag"):
        name_el = elem.find(".//{*}Name")
        if name_el is not None and name_el.text:
            name = name_el.text
            name_lower = name.lower()
            if "hmi_" in name_lower or "anim" in name_lower or "bon3" in name_lower or "bon4" in name_lower or "321" in name_lower or "323" in name_lower or "324" in name_lower or "326" in name_lower:
                dtype = elem.find(".//{*}DataTypeName").text
                addr = elem.find(".//{*}LogicalAddress").text
                comment_el = elem.find(".//{*}Comment//{*}Value")
                comment = comment_el.text if comment_el is not None else ""
                print(f"  Name: {name} | Type: {dtype} | Addr: {addr} | Comment: {comment}")
                found += 1

print(f"Total found in PLC 2: {found}")
