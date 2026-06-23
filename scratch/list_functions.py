# -*- coding: utf-8 -*-
with open("projects/Mixing_Nuoc_Tuong_Maggi_2026/generate_mixing_project.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "def " in line:
        print(f"Line {i+1}: {line.strip()}")
