import xml.etree.ElementTree as ET
import os

path = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\PLC\FC_SCADA_Sim_B3to7.xml"

tree = ET.parse(path)
root = tree.getroot()

networks = root.findall(".//SW.Blocks.CompileUnit")
for idx in [1, 2, 3, 4]: # Networks 2, 3, 4, 5 (0-indexed 1, 2, 3, 4)
    print(f"\n--- Network {idx+1} XML ---")
    xml_str = ET.tostring(networks[idx], encoding='utf-8').decode('utf-8')
    # Print the network logic parts and wires
    parts = networks[idx].find(".//ns0:Parts", {"ns0": "http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4"})
    if parts is not None:
        print(ET.tostring(parts, encoding='utf-8').decode('utf-8')[:1000])
    else:
        # Try without namespace
        parts = networks[idx].find(".//Parts")
        if parts is not None:
            print(ET.tostring(parts, encoding='utf-8').decode('utf-8')[:1000])
