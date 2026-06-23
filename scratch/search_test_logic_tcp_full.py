import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/test_plc_logic.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'MB_TCP_' in line:
        print(f"Line {i+1}: {line.strip()}")
