import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/test_plc_logic.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("PLC1 tick() lines:")
in_tick = False
for i, line in enumerate(lines[:1034]):
    if 'def tick(' in line:
        in_tick = True
    elif in_tick and 'def ' in line:
        in_tick = False
    if in_tick:
        if 'mb_' in line.lower() or 'tcp' in line.lower() or 'holding' in line.lower() or 'buffer' in line.lower():
            print(f"  Line {i+1}: {line.strip()}")

print("\nPLC2 tick() lines:")
in_tick = False
for i, line in enumerate(lines[1035:]):
    idx = i + 1035
    line = lines[idx]
    if 'def tick(' in line:
        in_tick = True
    elif in_tick and 'def ' in line:
        in_tick = False
    if in_tick:
        if 'mb_' in line.lower() or 'tcp' in line.lower() or 'holding' in line.lower() or 'buffer' in line.lower():
            print(f"  Line {idx+1}: {line.strip()}")
