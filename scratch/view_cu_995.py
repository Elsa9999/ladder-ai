import re

path = r"projects/Mixing_Nuoc_Tuong_Maggi_2026/tia_import/PLC_1_Mixing_Import/Main.xml"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'<SW.Blocks.CompileUnit ID="995"[^>]*>(.*?)</SW.Blocks.CompileUnit>', content, re.DOTALL)
if match:
    print(match.group(0)[:3000])
else:
    print("Not found")
