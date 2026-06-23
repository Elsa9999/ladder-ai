import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

filepath = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\generate_mixing_project.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Let's execute the setup block and dump the tags
# We can find tags with group == "Manual" or similar
# Let's extract the manual tag definitions by running a python command that runs generate_mixing_project.py up to tags definition
# Or we can just find them in text:
# We look for tags added with "Manual"
lines = content.splitlines()
for idx, line in enumerate(lines):
    if '"Manual"' in line or "'Manual'" in line:
        print(f"Line {idx+1}: {line.strip()}")
