import os
import re

roots = [
    r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Bai_4_Profinet_encoder_patch",
    r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Bai_4_Profinet_encoder_patch_v2",
    r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Bai_4_Profinet_export_from_ap18"
]

all_parts = set()

for root in roots:
    if not os.path.exists(root):
        continue
    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith(".xml"):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    part_names = re.findall(r'<Part\s+Name="([^"]+)"', content, re.IGNORECASE)
                    for part in part_names:
                        all_parts.add(part)
                except Exception as e:
                    pass

print("Unique parts found in all Profinet/Encoder projects:")
for part in sorted(list(all_parts)):
    print(f"  - {part}")
