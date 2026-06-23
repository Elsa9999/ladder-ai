import os
import re

projects_dir = r"d:\AI_Agent_PLC_LADDER_ONLY\projects"
target_instructions = [
    "TP", "TOF", "TONR", "CTD", "CTUD", "R_TRIG", "F_TRIG", "P_TRIG", "N_TRIG",
    "SR", "RS", "IN_RANGE", "OUT_RANGE", "MIN", "MAX", "LIMIT", "SEL", "MUX",
    "AND", "OR", "XOR", "INVERT", "MOVE_BLK", "FILL_BLK", "SHR", "SHL", "ROR", "ROL"
]

found_parts = {}

# Regular expression to extract Part Name="..."
part_regex = re.compile(r'<Part\s+Name="([^"]+)"')

for root_dir, dirs, files in os.walk(projects_dir):
    for filename in files:
        if not filename.endswith(".xml"):
            continue
        filepath = os.path.join(root_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            matches = part_regex.findall(content)
            for m in matches:
                # Case insensitive check
                for inst in target_instructions:
                    if m.lower() == inst.lower():
                        if inst not in found_parts:
                            found_parts[inst] = []
                        found_parts[inst].append((filepath, filename))
        except Exception as e:
            pass

print("--- PROJECTS SCAN RESULTS ---")
for inst, files in found_parts.items():
    print(f"Instruction '{inst}' found in {len(files)} files. Example:")
    for path, name in files[:2]:
        print(f"  - {name} in {os.path.relpath(path, projects_dir)}")
