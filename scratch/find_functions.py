import re
import sys

with open(r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\generate_mixing_project.py", "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if line.strip().startswith("def build_") or "def " in line:
            print(f"Line {i}: {line.strip()}")
