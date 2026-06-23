import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

filepath = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\test_plc_logic.py"

with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "timer_dryrun_bon" in line or "Timer_DryRun" in line:
        print(f"Line {idx+1}: {line.strip()}")
