import re
import sys

with open(r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\prepare_tia_import_sets.py", "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if "def " in line:
            print(f"Line {i}: {line.strip()}")
