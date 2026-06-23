import os
import json
import xml.etree.ElementTree as ET

blocks_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\raw_exports\PLSP_export\PLC_1\Blocks"
output_patterns_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\raw_patterns"
os.makedirs(output_patterns_dir, exist_ok=True)

target_instructions = {
    # Timers & Counters
    "TP": "TP", "TOF": "TOF", "TONR": "TONR", "CTD": "CTD", "CTUD": "CTUD", "TON": "TON", "CTU": "CTU",
    # Triggers
    "R_TRIG": "R_TRIG", "F_TRIG": "F_TRIG", "P_TRIG": "P_TRIG", "N_TRIG": "N_TRIG",
    "PContact": "P_TRIG", "NContact": "N_TRIG",
    # Flip-Flops
    "SR": "SR", "RS": "RS",
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
    "SHR": "SHR", "SHL": "SHL", "ROR": "ROR", "ROL": "ROL"
}

# Keep track of findings
found_instructions = {}

# Parse XML files
for filename in os.listdir(blocks_dir):
    if not filename.endswith(".xml"):
        continue
    filepath = os.path.join(blocks_dir, filename)
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        # Find all CompileUnits using wildcard namespace
        compile_units = root.findall('.//{*}CompileUnit')
            
        for cu_idx, cu in enumerate(compile_units):
            # Find all Parts inside this compile unit
            parts = cu.findall('.//{*}Part')
                
            for part in parts:
                part_name = part.attrib.get('Name')
                if part_name in target_instructions:
                    mapped_name = target_instructions[part_name]
                    
                    # Extract version
                    version = part.attrib.get('Version', '1.0')
                    
                    # Extract instance DB if any
                    instance_db = ""
                    instance = part.find('.//{*}Instance')
                    if instance is not None:
                        component = instance.find('.//{*}Component')
                        if component is not None:
                            instance_db = component.attrib.get('Name', '')
                            
                    # Extract raw XML representing the CompileUnit (Network)
                    cu_xml = ET.tostring(cu, encoding='utf-8').decode('utf-8')
                    
                    # Get network title
                    title = ""
                    title_elem = cu.find('.//{*}Title//{*}-Item') # check for MultilingualTextItem or Title
                    if title_elem is None:
                        title_elem = cu.find('.//{*}Title')
                    if title_elem is not None:
                        # Try to find Text element inside Title
                        text_elem = title_elem.find('.//{*}Text')
                        if text_elem is not None:
                            title = text_elem.text or ""
                            
                    # Parse referenced tags in this Network
                    referenced_tags = []
                    accesses = cu.findall('.//{*}Access')
                    for access in accesses:
                        scope = access.attrib.get('Scope', '')
                        if scope == 'GlobalVariable':
                            symbol = access.find('.//{*}Symbol')
                            if symbol is not None:
                                components = symbol.findall('.//{*}Component')
                                tag_name = '.'.join([c.attrib.get('Name', '') for c in components])
                                if tag_name and tag_name not in referenced_tags:
                                    referenced_tags.append(tag_name)
                                    
                    # Store info
                    if mapped_name not in found_instructions:
                        found_instructions[mapped_name] = []
                        
                    found_instructions[mapped_name].append({
                        "filename": filename,
                        "network_idx": cu_idx + 1,
                        "network_title": title,
                        "version": version,
                        "instance_db": instance_db,
                        "xml_content": cu_xml,
                        "referenced_tags": referenced_tags
                    })
    except Exception as e:
        print(f"Error parsing {filename}: {e}")

# Save found patterns
print("\n--- EXTRACTING PATTERNS ---")
for inst, occurrences in found_instructions.items():
    # We take the first occurrence as the primary pattern
    primary = occurrences[0]
    
    inst_dir = os.path.join(output_patterns_dir, inst.lower())
    os.makedirs(inst_dir, exist_ok=True)
    
    # 1. Save pattern.raw.xml
    xml_path = os.path.join(inst_dir, "pattern.raw.xml")
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(primary["xml_content"].strip())
        
    # 2. Save manifest.raw.json
    manifest = {
        "tia_version": "V18",
        "plc_family": "S7-1200",
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

# Save execution stats for report creation
with open(os.path.join(output_patterns_dir, "extraction_stats.json"), "w", encoding="utf-8") as f:
    json.dump({inst: [{"filename": o["filename"], "network_idx": o["network_idx"], "network_title": o["network_title"], "version": o["version"], "instance_db": o["instance_db"]} for o in occs] for inst, occs in found_instructions.items()}, f, indent=2)

print(f"\nCompleted extraction. Total unique instructions found: {len(found_instructions)}")
