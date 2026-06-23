import os
import json

main_patterns_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\patterns"
raw_patterns_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\raw_patterns"

print("=================================================")
print(" SCANNING MAIN PATTERN LIBRARY FOR DUPLICATES")
print("=================================================")

# 1. Gather all info from main patterns folder
main_folders = set()
main_manifest_names = {}
main_xml_files = set()

for root, dirs, files in os.walk(main_patterns_dir):
    # Store folder names
    for d in dirs:
        main_folders.add(d.upper())
    
    # Store XML file names (without extension)
    for f in files:
        if f.endswith(".xml"):
            name_no_ext = os.path.splitext(f)[0].upper()
            main_xml_files.add(name_no_ext)
            
    # Parse manifest if present
    if "manifest.json" in files:
        manifest_path = os.path.join(root, "manifest.json")
        try:
            with open(manifest_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            inst_name = data.get("block_instruction_name")
            if inst_name:
                rel_path = os.path.relpath(root, main_patterns_dir)
                main_manifest_names[inst_name.upper()] = rel_path
        except Exception as e:
            pass

print(f"Main Library Folders Found: {len(main_folders)}")
print(f"Main Library Manifest Names Found: {len(main_manifest_names)}")
print(f"Main Library XML Names Found: {len(main_xml_files)}")

# 2. Check each raw pattern
print("\n--- DETAILED DUPLICATE AUDIT ---")
duplicates = []
uniques = []

for folder in os.listdir(raw_patterns_dir):
    folder_path = os.path.join(raw_patterns_dir, folder)
    if not os.path.isdir(folder_path):
        continue
        
    manifest_path = os.path.join(folder_path, "manifest.raw.json")
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            raw_name = data.get("block_instruction_name", "")
            raw_name_upper = raw_name.upper()
            folder_upper = folder.upper()
            
            # Check by manifest name, folder name, or XML name
            matched_by = []
            matched_path = ""
            
            if raw_name_upper in main_manifest_names:
                matched_by.append("manifest_name")
                matched_path = main_manifest_names[raw_name_upper]
            if folder_upper in main_folders:
                matched_by.append("folder_name")
                # Find the path of this folder in main library
                for root, dirs, files in os.walk(main_patterns_dir):
                    if folder in dirs:
                        matched_path = os.path.relpath(os.path.join(root, folder), main_patterns_dir)
                        break
            if raw_name_upper in main_xml_files:
                matched_by.append("xml_file_name")
                
            if matched_by:
                duplicates.append({
                    "raw_name": raw_name,
                    "folder": folder,
                    "matched_by": matched_by,
                    "matched_path": matched_path
                })
            else:
                uniques.append(raw_name)
        except Exception as e:
            print(f"Error reading raw manifest for {folder}: {e}")

print("\n[DUPLICATES DETECTED]")
for d in sorted(duplicates, key=lambda x: x["raw_name"]):
    print(f"  - '{d['raw_name']}' (folder: '{d['folder']}') matched by {d['matched_by']} in patterns/{d['matched_path']}")

print("\n[TRULY UNIQUE NEW PATTERNS]")
for u in sorted(uniques):
    print(f"  - '{u}'")
