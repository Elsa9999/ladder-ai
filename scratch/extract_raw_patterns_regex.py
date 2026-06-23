import os
import re
import json

export_root_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\raw_exports\PLSP_export"
output_patterns_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\raw_patterns"
os.makedirs(output_patterns_dir, exist_ok=True)

target_instructions = {
    # Timers & Counters
    "TP": "TP", "TOF": "TOF", "TONR": "TONR", "CTD": "CTD", "CTUD": "CTUD", "TON": "TON", "CTU": "CTU",
    # Triggers
    "R_TRIG": "R_TRIG", "F_TRIG": "F_TRIG", "P_TRIG": "P_TRIG", "N_TRIG": "N_TRIG",
    "PContact": "P_TRIG", "NContact": "N_TRIG",
    "PBox": "P_TRIG", "NBox": "N_TRIG",
    # Flip-Flops
    "SR": "SR", "RS": "RS", "Sr": "SR", "Rs": "RS",
    # Ranges & Limits
    "IN_RANGE": "IN_RANGE", "OUT_RANGE": "OUT_RANGE",
    "In_Range": "IN_RANGE", "Out_Range": "OUT_RANGE",
    "Min": "MIN", "Max": "MAX", "Limit": "LIMIT",
    "MIN": "MIN", "MAX": "MAX", "LIMIT": "LIMIT",
    # Selection
    "Sel": "SEL", "Mux": "MUX",
    "SEL": "SEL", "MUX": "MUX",
    # Bitwise logic
    "Xor": "XOR", "XOR": "XOR", "Not": "INVERT", "INVERT": "INVERT",
    "A": "AND", "O": "OR",
    # Blocks & Shifts
    "MOVE_BLK": "MOVE_BLK", "FILL_BLK": "FILL_BLK",
    "Shr": "SHR", "Shl": "SHL", "Ror": "ROR", "Rol": "ROL",
    "SHR": "SHR", "SHL": "SHL", "ROR": "ROR", "ROL": "ROL",
    # Analog Scaling
    "Normalize": "NORM_X", "Scale_X": "SCALE_X"
}

found_instructions = {}

# Regex compiled patterns
compile_unit_re = re.compile(r'(<SW\.Blocks\.CompileUnit[^>]*>.*?</SW\.Blocks\.CompileUnit>)', re.DOTALL)
part_re = re.compile(r'<Part\s+Name="([^"]+)"(?:\s+Version="([^"]+)")?[^>]*>', re.IGNORECASE)
instance_re = re.compile(r'<Instance\s+Scope="([^"]+)"[^>]*>.*?<Component\s+Name="([^"]+)"\s*/>', re.DOTALL)
title_re = re.compile(r'<MultilingualText[^>]*CompositionName="Title">.*?<Text>([^<]*)</Text>', re.DOTALL)
access_re = re.compile(r'<Access\s+Scope="GlobalVariable"[^>]*>.*?<Component\s+Name="([^"]+)"\s*/>', re.DOTALL)

# Walk recursively through all files in PLSP_export
for root_dir, dirs, files in os.walk(export_root_dir):
    # We only care about files in "Blocks" directories
    if "Blocks" not in root_dir:
        continue
        
    for filename in files:
        if not filename.endswith(".xml"):
            continue
        filepath = os.path.join(root_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            compile_units = compile_unit_re.findall(content)
            
            for cu_idx, cu in enumerate(compile_units):
                # Check for any parts inside this network
                parts = part_re.findall(cu)
                for part_name, version in parts:
                    if part_name in target_instructions:
                        mapped_name = target_instructions[part_name]
                        
                        # Search for instance DB if any in the specific Part tag block
                        part_start = cu.find(f'Name="{part_name}"')
                        instance_db = ""
                        if part_start != -1:
                            part_end = cu.find('</Part>', part_start)
                            if part_end != -1:
                                part_block = cu[part_start:part_end]
                                inst_match = instance_re.search(part_block)
                                if inst_match:
                                    instance_db = inst_match.group(2)
                                    
                        # Get title
                        title_match = title_re.search(cu)
                        title = title_match.group(1).strip() if title_match else ""
                        
                        # Parse referenced global variable tags
                        referenced_tags = list(set(access_re.findall(cu)))
                        
                        if mapped_name not in found_instructions:
                            found_instructions[mapped_name] = []
                            
                        # Avoid duplicates from the exact same file/network
                        is_dup = False
                        for existing in found_instructions[mapped_name]:
                            if existing["filename"] == filename and existing["network_idx"] == cu_idx + 1:
                                if "PLC_2" in root_dir and "PLC_2" in existing.get("filepath", ""):
                                    is_dup = True
                                    break
                                elif "PLC_2" not in root_dir and "PLC_2" not in existing.get("filepath", ""):
                                    is_dup = True
                                    break
                        if is_dup:
                            continue
                            
                        found_instructions[mapped_name].append({
                            "filename": filename,
                            "filepath": filepath,
                            "network_idx": cu_idx + 1,
                            "network_title": title,
                            "version": version or "1.0",
                            "instance_db": instance_db,
                            "xml_content": cu,
                            "referenced_tags": referenced_tags
                        })
        except Exception as e:
            print(f"Error parsing {filename}: {e}")

# Save found patterns
print("\n--- EXTRACTING PATTERNS ---")
for inst, occurrences in found_instructions.items():
    primary = occurrences[0]
    
    inst_dir = os.path.join(output_patterns_dir, inst.lower())
    os.makedirs(inst_dir, exist_ok=True)
    
    # 1. Save pattern.raw.xml
    xml_path = os.path.join(inst_dir, "pattern.raw.xml")
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(primary["xml_content"].strip())
        
    # 2. Save manifest.raw.json
    plc_family = "S7-300" if "PLC_2" in primary.get("filepath", "") else "S7-1200"
    if inst in ["TOF", "INVERT", "CTU", "TON"]:
        plc_family = "S7-1200"
        
    manifest = {
        "tia_version": "V18",
        "plc_family": plc_family,
        "language": "LAD",
        "block_instruction_name": inst,
        "tested_status": "compiled",
        "required_tags": [{"name": t, "type": "AUTO"} for t in primary["referenced_tags"]],
        "required_dbs": [],
        "required_instance_db": primary["instance_db"],
        "required_data_types": [],
        "source_file": primary["filename"],
        "network_index": primary["network_idx"],
        "network_title": primary["network_title"],
        "version": primary["version"]
    }
    
    manifest_path = os.path.join(inst_dir, "manifest.raw.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print(f"[OK] Extracted: {inst} (from {primary['filename']}, Network {primary['network_idx']})")

# Save stats
with open(os.path.join(output_patterns_dir, "extraction_stats.json"), "w", encoding="utf-8") as f:
    json.dump({inst: [{"filename": o["filename"], "network_idx": o["network_idx"], "network_title": o["network_title"], "version": o["version"], "instance_db": o["instance_db"]} for o in occs] for inst, occs in found_instructions.items()}, f, indent=2)

print(f"\nCompleted extraction. Total unique instructions found: {len(found_instructions)}")
