import xml.etree.ElementTree as ET
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

path = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\PLC\PLC_Tags_B3to7.xml"

if not os.path.exists(path):
    print("Tag file not found.")
    sys.exit(0)

tree = ET.parse(path)
root = tree.getroot()

# Find tags containing "Sim"
tags = root.findall(".//PlcTag")
print(f"Total tags in table: {len(tags)}")

sim_tags = []
for tag in tags:
    name_el = tag.find("Name")
    name = name_el.text if name_el is not None else ""
    if "sim" in name.lower():
        logical_el = tag.find("LogicalAddress")
        address = logical_el.text if logical_el is not None else "N/A"
        type_el = tag.find("DataTypeName")
        datatype = type_el.text if type_el is not None else "N/A"
        sim_tags.append((name, address, datatype))

print("\n=== Simulation Tags found ===")
for name, address, datatype in sim_tags:
    print(f"Name: {name} | Address: {address} | DataType: {datatype}")
