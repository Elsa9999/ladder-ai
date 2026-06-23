import xml.etree.ElementTree as ET
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

path_bai1 = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai1\PLC\FC_SCADA_Simulation.xml"
path_sim = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\PLC\FC_SCADA_Sim_B3to7.xml"

if not os.path.exists(path_bai1) or not os.path.exists(path_sim):
    print("One of the files is missing.")
    sys.exit(0)

tree1 = ET.parse(path_bai1)
root1 = tree1.getroot()
nets1 = root1.findall(".//SW.Blocks.CompileUnit")

tree2 = ET.parse(path_sim)
root2 = tree2.getroot()
nets2 = root2.findall(".//SW.Blocks.CompileUnit")

print(f"scadabai1 networks count: {len(nets1)}")
print(f"scadabai_sim networks count: {len(nets2)}")

# Compare network by network
limit = min(len(nets1), len(nets2))
diff_found = 0
for idx in range(limit):
    net1 = nets1[idx]
    net2 = nets2[idx]
    
    t1_el = net1.find(".//MultilingualText[@CompositionName='Title']//Text")
    t1 = t1_el.text if t1_el is not None else ""
    t2_el = net2.find(".//MultilingualText[@CompositionName='Title']//Text")
    t2 = t2_el.text if t2_el is not None else ""
    
    # Check if logic is identical
    src1_el = net1.find(".//NetworkSource")
    src2_el = net2.find(".//NetworkSource")
    src1 = ET.tostring(src1_el, encoding='utf-8').decode('utf-8') if src1_el is not None else ""
    src2 = ET.tostring(src2_el, encoding='utf-8').decode('utf-8') if src2_el is not None else ""
    
    # Strip namespaces for comparison
    import re
    src1_clean = re.sub(r'xmlns(:\w+)?="[^"]+"', '', src1)
    src2_clean = re.sub(r'xmlns(:\w+)?="[^"]+"', '', src2)
    src1_clean = re.sub(r'\w+:', '', src1_clean)
    src2_clean = re.sub(r'\w+:', '', src2_clean)
    
    # Normalize spaces
    src1_clean = " ".join(src1_clean.split())
    src2_clean = " ".join(src2_clean.split())
    
    # Replace variable names so we compare structure
    # Let's see if they are identical structurally
    if src1_clean != src2_clean:
        if idx < 10: # Only print details for first few differences
            print(f"\n[DIFF] Network {idx+1}:")
            print(f"  scadabai1 title: {t1}")
            print(f"  scadabai_sim title: {t2}")
            print(f"  scadabai1 logic: {src1_clean[:200]}")
            print(f"  scadabai_sim logic: {src2_clean[:200]}")
            diff_found += 1
        else:
            diff_found += 1

print(f"\nTotal structural differences in first {limit} networks: {diff_found}")
if len(nets1) != len(nets2):
    print(f"Size difference: scadabai1 has {len(nets1)}, scadabai_sim has {len(nets2)}")
