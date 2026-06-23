path = r"projects/Mixing_Nuoc_Tuong_Maggi_2026/tia_import/PLC_1_Mixing_Import/PLC_Tags.xml"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if "VFD_Bon2_MB_DataAddr" in line:
        print(f"Line {i}: {line.strip()}")
        # print surrounding lines
        for j in range(max(0, i-5), min(len(lines), i+15)):
            print(f"  {j+1}: {lines[j].strip()}")
