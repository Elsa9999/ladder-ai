import xml.etree.ElementTree as ET
import os

path = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai1\PLC\PLC_Simulation_Tags.xml"

if os.path.exists(path):
    tree = ET.parse(path)
    root = tree.getroot()
    tags = root.findall(".//SW.Tags.PlcTag")
    print(f"Total tags in scadabai1 table: {len(tags)}")
    for i, tag in enumerate(tags):
        name_el = tag.find("AttributeList/Name")
        name = name_el.text if name_el is not None else ""
        logical_el = tag.find("AttributeList/LogicalAddress")
        address = logical_el.text if logical_el is not None else "N/A"
        type_el = tag.find("AttributeList/DataTypeName")
        datatype = type_el.text if type_el is not None else "N/A"
        print(f"Tag {i+1}: Name={name} | Address={address} | DataType={datatype}")
else:
    print("scadabai1 tag file not found.")
