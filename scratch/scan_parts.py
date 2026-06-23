import os
import xml.etree.ElementTree as ET

templates_dir = r"d:\AI_Agent_PLC_LADDER_ONLY\templates\TIA_Dataset_XML"
target_instructions = [
    "TP", "TOF", "TONR", "CTD", "CTUD", "R_TRIG", "F_TRIG", "P_TRIG", "N_TRIG",
    "SR", "RS", "IN_RANGE", "OUT_RANGE", "MIN", "MAX", "LIMIT", "SEL", "MUX",
    "AND", "OR", "XOR", "INVERT", "MOVE_BLK", "FILL_BLK", "SHR", "SHL", "ROR", "ROL"
]

found_parts = {}

# We will search both for exact name match (case-insensitive) and sub-matches
for filename in os.listdir(templates_dir):
    if not filename.endswith(".xml"):
        continue
    filepath = os.path.join(templates_dir, filename)
    try:
        # Parse XML (we use a simple string search or ET)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Quick check if any target instruction might be inside as a Part Name
        for inst in target_instructions:
            # Look for Part Name="inst" or Part Name="inst_something" or similar
            search_str_1 = f'Part Name="{inst}"'
            search_str_2 = f'Part Name="{inst.capitalize()}"'
            search_str_3 = f'Part Name="{inst.lower()}"'
            
            found = False
            for s in [search_str_1, search_str_2, search_str_3]:
                if s in content:
                    found = True
                    break
            
            if found:
                if inst not in found_parts:
                    found_parts[inst] = []
                found_parts[inst].append(filename)
    except Exception as e:
        print(f"Error reading {filename}: {e}")

print("--- SCAN RESULTS ---")
for inst, files in found_parts.items():
    print(f"Instruction '{inst}' found in {len(files)} files: {files[:3]}")
