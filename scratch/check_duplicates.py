import os
import json

main_patterns_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\patterns"
raw_patterns_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\raw_patterns"

# 1. Collect all instruction names in the main library
main_instructions = {}

for root_dir, dirs, files in os.walk(main_patterns_dir):
    if "manifest.json" in files:
        manifest_path = os.path.join(root_dir, "manifest.json")
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            inst_name = data.get("block_instruction_name")
            if inst_name:
                # Store the instruction name and its relative path
                rel_path = os.path.relpath(root_dir, main_patterns_dir)
                main_instructions[inst_name.upper()] = {
                    "path": rel_path,
                    "name": inst_name
                }
        except Exception as e:
            pass

# 2. Check each extracted raw pattern
print("--- CHECKING FOR DUPLICATES ---")
duplicates = []
uniques = []

for folder in os.listdir(raw_patterns_dir):
    folder_path = os.path.join(raw_patterns_dir, folder)
    if not os.path.isdir(folder_path):
        continue
    
    manifest_path = os.path.join(folder_path, "manifest.raw.json")
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            raw_inst_name = data.get("block_instruction_name", "").upper()
            
            if raw_inst_name in main_instructions:
                duplicates.append({
                    "raw_name": data.get("block_instruction_name"),
                    "main_name": main_instructions[raw_inst_name]["name"],
                    "main_path": main_instructions[raw_inst_name]["path"]
                })
            else:
                uniques.append(data.get("block_instruction_name"))
        except Exception as e:
            pass

print("\n[DUPLICATES FOUND] These instructions are already in the main library:")
for d in duplicates:
    print(f"  - '{d['raw_name']}' matches existing pattern '{d['main_name']}' in patterns/{d['main_path']}")

print("\n[UNIQUE / NEW INSTRUCTIONS] These are brand new and not in the main library:")
for u in uniques:
    print(f"  - '{u}'")
