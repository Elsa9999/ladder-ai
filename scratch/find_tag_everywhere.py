import os
import re

dir_path = "projects/Mixing_Nuoc_Tuong_Maggi_2026/tia_import/PLC_1_Mixing_Import"
for root, dirs, files in os.walk(dir_path):
    for f in files:
        if f.endswith(".xml"):
            p = os.path.join(root, f)
            try:
                content = open(p, "r", encoding="utf-8").read()
                if "VFD_Bon2_MB_DataAddr" in content:
                    print(f"Found in {f}")
            except Exception:
                pass
