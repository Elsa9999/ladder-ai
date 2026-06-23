import re
import sys

# Configure stdout for UTF-8 to handle Vietnamese accents in console output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

filepath = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\generate_mixing_project.py"
queries = [
    r"FC_Manual_Control",
    r"FC_HMI_Animation",
    r"Timer_DryRun",
    r"\"60\"",
    r"\"61\"",
    r"Dry_Run",
    r"Xa_Bon2_Xong",
    r"Xa_Bon4_Xong",
    r"BonChua1_Xa_Xong",
    r"BonChua2_Xa_Xong"
]

with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

for query in queries:
    print(f"=== Searching for: {query} ===")
    matches = 0
    for idx, line in enumerate(lines):
        if re.search(query, line, re.IGNORECASE):
            print(f"Line {idx+1}: {line.strip()}")
            matches += 1
            if matches > 20:
                print("... truncated ...")
                break
