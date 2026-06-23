import xml.etree.ElementTree as ET
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

path = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\PLC\FC_SCADA_Sim_B3to7.xml"

if not os.path.exists(path):
    print("File not found.")
    sys.exit(0)

tree = ET.parse(path)
root = tree.getroot()

# Let's count networks
networks = root.findall(".//SW.Blocks.CompileUnit")
print(f"Total compile units (networks) in FC: {len(networks)}")

# Print titles/comments of first 30 networks to understand the logic
for i, net in enumerate(networks[:35]):
    title_el = net.find(".//MultilingualText[@CompositionName='Title']//Text")
    title = title_el.text if title_el is not None else "No Title"
    print(f"Network {i+1}: {title}")
