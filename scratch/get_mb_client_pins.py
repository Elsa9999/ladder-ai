# -*- coding: utf-8 -*-
import os

path = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\post_import_export_manual\PLC_1\Blocks\Main.xml"
if not os.path.exists(path):
    path = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\post_import_export\PLC_1\Blocks\Main.xml"

if os.path.exists(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Tìm khối MB_CLIENT
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if 'Part Name="MB_CLIENT"' in line:
            uid = ""
            # Tìm UId
            import re
            m = re.search(r'UId="(\d+)"', line)
            if m:
                uid = m.group(1)
            print(f"Found MB_CLIENT block with UId {uid} at line {idx}")
            
            # Quét các dòng tiếp theo tìm NameCon UId="{uid}"
            print("Connections:")
            for j in range(idx + 1, min(len(lines), idx + 200)):
                if f'UId="{uid}"' in lines[j] and 'NameCon' in lines[j]:
                    print(f"  Line {j}: {lines[j].strip()}")
                if '</Wires>' in lines[j]:
                    break
            print("="*40)
