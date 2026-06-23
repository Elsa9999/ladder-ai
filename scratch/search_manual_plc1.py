import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

filepath = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\generate_mixing_project.py"

with open(filepath, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if "FC_Manual_Control_PLC1" in line:
            print(f"Line {idx+1}: {line.strip()}")
