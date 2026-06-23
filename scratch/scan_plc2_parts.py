import os
import re

blocks_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\raw_exports\PLSP_export\PLC_2\Blocks"
target_instructions = {
    # Timers & Counters
    "TP": "TP", "TOF": "TOF", "TONR": "TONR", "CTD": "CTD", "CTUD": "CTUD", "TON": "TON", "CTU": "CTU",
    # Triggers
    "R_TRIG": "R_TRIG", "F_TRIG": "F_TRIG", "P_TRIG": "P_TRIG", "N_TRIG": "N_TRIG",
    "PContact": "P_TRIG", "NContact": "N_TRIG",
    "PBox": "P_TRIG", "NBox": "N_TRIG",
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
    "SHR": "SHR", "SHL": "SHL", "ROR": "ROR", "ROL": "ROL",
    # Analog Scaling
    "Normalize": "NORM_X", "Scale_X": "SCALE_X"
}

all_parts = set()
found_targets = {}

part_re = re.compile(r'<Part\s+Name="([^"]+)"', re.IGNORECASE)

for root, dirs, files in os.walk(blocks_dir):
    for f in files:
        if not f.endswith(".xml"):
            continue
        path = os.path.join(root, f)
        with open(path, "r", encoding="utf-8", errors="ignore") as file:
            content = file.read()
            parts = part_re.findall(content)
            for part in parts:
                all_parts.add(part)
                if part in target_instructions:
                    mapped = target_instructions[part]
                    if mapped not in found_targets:
                        found_targets[mapped] = []
                    found_targets[mapped].append(f)

print("--- ALL PARTS FOUND ---")
print(sorted(list(all_parts)))
print("\n--- TARGET INSTRUCTIONS FOUND ---")
for t, files in sorted(found_targets.items()):
    unique_files = sorted(list(set(files)))
    print(f"{t}: found in {len(unique_files)} files: {unique_files}")
