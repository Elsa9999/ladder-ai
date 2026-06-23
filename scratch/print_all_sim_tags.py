import xml.etree.ElementTree as ET
import os

path = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\PLC\PLC_Tags_B3to7.xml"

if os.path.exists(path):
    tree = ET.parse(path)
    root = tree.getroot()
    tags = root.findall(".//SW.Tags.PlcTag")
    print(f"Total tags in scadabai_sim table: {len(tags)}")
    found = 0
    for tag in tags:
        name_el = tag.find("AttributeList/Name")
        name = name_el.text if name_el is not None else ""
        if "sim" in name.lower() or "pulse" in name.lower() or "counter" in name.lower() or "dir" in name.lower():
            logical_el = tag.find("AttributeList/LogicalAddress")
            address = logical_el.text if logical_el is not None else "N/A"
            type_el = tag.find("AttributeList/DataTypeName")
            datatype = type_el.text if type_el is not None else "N/A"
            print(f"Name: {name} | Address: {address} | DataType: {datatype}")
            found += 1
    print(f"Found {found} simulation tags.")
else:
    print("scadabai_sim tag file not found.")
