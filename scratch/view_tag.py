import re

path = r"projects/Mixing_Nuoc_Tuong_Maggi_2026/tia_import/PLC_1_Mixing_Import/PLC_Tags.xml"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

m = re.search(r'<PlcTag.*?Name="VFD_Bon2_MB_DataAddr".*?</PlcTag>', content, re.DOTALL)
if m:
    print(m.group(0))
else:
    print("Not found")
