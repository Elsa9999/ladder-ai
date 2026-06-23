import os
import json

raw_patterns_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\raw_patterns"
targets = ["f_trig", "invert", "norm_x", "n_trig", "or", "p_trig", "r_trig", "scale_x", "sr", "tof", "tonr", "tp"]

for target in sorted(targets):
    manifest_path = os.path.join(raw_patterns_dir, target, "manifest.raw.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"=== {target.upper()} ===")
        print(f"Block Instruction Name: {data.get('block_instruction_name')}")
        print(f"Required Instance DB: {data.get('required_instance_db')}")
        print("Required Tags:")
        for tag in data.get("required_tags", []):
            print(f"  - {tag['name']} ({tag.get('type')})")
        print()
