with open('scratch/test_plc_logic.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'class ' in line:
        print(f"Line {i+1}: {line.strip()}")
