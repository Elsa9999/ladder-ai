import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('projects/Mixing_Nuoc_Tuong_Maggi_2026/generate_mixing_project.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

keyword = "Khuay_Active"
for i, line in enumerate(lines):
    if keyword in line:
        print(f"Line {i+1}: {line.strip()}")
        # print 5 lines before and 10 lines after
        for j in range(-5, 15):
            idx = i + j
            if 0 <= idx < len(lines):
                print(f"  {idx+1}: {lines[idx].strip()}")
        print("-" * 40)
