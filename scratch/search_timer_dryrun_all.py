import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

scratch_dir = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch"

for filename in os.listdir(scratch_dir):
    if filename.endswith(".py") or filename.endswith(".cs"):
        filepath = os.path.join(scratch_dir, filename)
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if "Timer_DryRun" in content:
            print(f"File: {filename}")
            for idx, line in enumerate(content.splitlines()):
                if "Timer_DryRun" in line:
                    print(f"  Line {idx+1}: {line.strip()}")
