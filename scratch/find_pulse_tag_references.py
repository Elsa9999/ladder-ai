import os
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

plc_dir = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\PLC"

tag_name = "Timer_Sim_Pulse_Output"
print(f"Searching for references to '{tag_name}' in PLC XML files...")

for root_dir, dirs, files in os.walk(plc_dir):
    for file in files:
        if file.endswith(".xml"):
            path = os.path.join(root_dir, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if tag_name in content:
                    # Parse XML to find which networks reference it
                    tree = ET.parse(path)
                    root_el = tree.getroot()
                    nets = root_el.findall(".//SW.Blocks.CompileUnit")
                    referenced_nets = []
                    for idx, net in enumerate(nets):
                        net_str = ET.tostring(net, encoding='utf-8').decode('utf-8')
                        if tag_name in net_str:
                            title_el = net.find(".//MultilingualText[@CompositionName='Title']//Text")
                            title = title_el.text if title_el is not None else "No Title"
                            referenced_nets.append(f"Network {idx+1}: {title}")
                    
                    print(f"\nFile: {file} (Found {len(referenced_nets)} references):")
                    for ref in referenced_nets:
                        print(f"  {ref}")
            except Exception as e:
                print(f"Error reading {file}: {e}")
