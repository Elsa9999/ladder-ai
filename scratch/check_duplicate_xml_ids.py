import re
from collections import Counter

path = r"projects/Mixing_Nuoc_Tuong_Maggi_2026/tia_import/PLC_1_Mixing_Import/Main.xml"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

compile_units = re.findall(r'<SW.Blocks.CompileUnit ID="([^"]+)"[^>]*>(.*?)</SW.Blocks.CompileUnit>', content, re.DOTALL)

print(f"Total compile units: {len(compile_units)}")
any_dups = False

for cu_id, cu_content in compile_units:
    uids = re.findall(r'UId="([^"]+)"', cu_content)
    uid_counts = Counter(uids)
    dup_uids = {k: v for k, v in uid_counts.items() if v > 1}
    if dup_uids:
        print(f"CompileUnit ID {cu_id} has duplicate UIds:")
        for k, v in dup_uids.items():
            print(f"  UId {k}: {v} times")
        any_dups = True

if not any_dups:
    print("No duplicate UIds found within any individual CompileUnit!")
