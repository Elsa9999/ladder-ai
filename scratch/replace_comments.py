# -*- coding: utf-8 -*-
with open("projects/Mixing_Nuoc_Tuong_Maggi_2026/generate_mixing_project.py", "r", encoding="utf-8") as f:
    content = f.read()

# Perform the required replacements
replacements = {
    "PID Bồn 2 qua VFD/động cơ": "PID Bồn 2 điều khiển van hơi CV3206; VFD chỉ giữ tốc độ khuấy từ HMI",
    "PID Bồn 2 qua VFD": "PID Bồn 2 điều khiển van hơi CV3206; VFD chỉ giữ tốc độ khuấy từ HMI",
    "Bồn 2 gia nhiệt PID qua VFD/động cơ": "Bồn 2 gia nhiệt PID điều khiển van hơi CV3206; VFD chỉ giữ tốc độ khuấy từ HMI",
    "State 30 - PID Bồn 2 qua VFD": "State 30 - PID Bồn 2 điều khiển van hơi CV3206; VFD chỉ giữ tốc độ khuấy từ HMI"
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open("projects/Mixing_Nuoc_Tuong_Maggi_2026/generate_mixing_project.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Replacement done successfully!")
