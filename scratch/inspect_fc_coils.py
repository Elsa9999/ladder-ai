import xml.etree.ElementTree as ET
import sys

filepath = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\tia_import\PLC_2_Mixing_Import\FC_PLC2_Mixing.xml"
tree = ET.parse(filepath)
root = tree.getroot()

# Find the compile unit (network) containing UId='2480'
for cu in root.findall(".//{*}SW.Blocks.CompileUnit"):
    found = False
    for elem in cu.iter():
        if elem.attrib.get("UId") == "2480" or elem.attrib.get("ID") == "2480":
            found = True
            break
    if found:
        title = cu.find(".//{*}Title")
        title_text = ""
        if title is not None:
            text_node = title.find(".//{*}Text")
            if text_node is not None:
                title_text = text_node.text
        print(f"Found UId 2480 in CompileUnit: Title='{title_text}', ID={cu.attrib.get('ID')}")
        # Print the XML of the CompileUnit
        ET.dump(cu)
        break
else:
    print("Could not find UId 2480 in FC_PLC2_Mixing.xml")
