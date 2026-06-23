# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

plc1_xml = r"D:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\output\PLC_Tags_PLC1.xml"
if not os.path.exists(plc1_xml):
    print("PLC_Tags_PLC1.xml not found")
    sys.exit(1)

tree = ET.parse(plc1_xml)
root = tree.getroot()

print("Recv/Send/HMI/PLC2 tags in PLC 1:")
found = 0
for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    if tag_local.endswith("PlcTag"):
        name_el = elem.find(".//{*}Name")
        if name_el is not None and name_el.text:
            name = name_el.text
            name_lower = name.lower()
            if "recv" in name_lower or "send" in name_lower or "plc2" in name_lower or "hmi_" in name_lower:
                dtype = elem.find(".//{*}DataTypeName").text
                addr = elem.find(".//{*}LogicalAddress").text
                comment_el = elem.find(".//{*}Comment//{*}Value")
                comment = comment_el.text if comment_el is not None else ""
                print(f"  Name: {name} | Type: {dtype} | Addr: {addr} | Comment: {comment}")
                found += 1

print(f"Total found: {found}")
