import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('projects/Mixing_Nuoc_Tuong_Maggi_2026/generate_mixing_project.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for line_idx in [1006, 1016, 1023, 1031, 1173, 1178, 1185, 1190, 2351, 2961, 3531]:
    idx = line_idx - 1
    print(f"--- Line {line_idx} ---")
    for j in range(-2, 4):
        cur = idx + j
        if 0 <= cur < len(lines):
            print(f"  {cur+1}: {lines[cur].strip()}")
