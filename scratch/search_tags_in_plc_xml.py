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

print("Searching for Bồn 3/4 tags in PLC 1 XML:")
keywords = ["Bon3", "Bon4", "3210", "3211", "3213", "3214", "3215", "3216", "3218", "3219", "PLC2"]

found = 0
for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    if tag_local.endswith("PlcTag"):
        name_el = elem.find(".//{*}Name")
        if name_el is not None and name_el.text:
            name = name_el.text
            match = [k for k in keywords if k.lower() in name.lower()]
            if match:
                dtype = elem.find(".//{*}DataTypeName").text
                addr = elem.find(".//{*}LogicalAddress").text
                print(f"  Matched Name: {name} | Type: {dtype} | Addr: {addr} (Matched: {match})")
                found += 1

print(f"Total matched tags in PLC 1: {found}")
