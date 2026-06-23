import os
import re

templates_dir = r"d:\AI_Agent_PLC_LADDER_ONLY\templates\TIA_Dataset_XML"
part_names = set()

# Regular expression to extract Part Name="..."
part_regex = re.compile(r'<Part\s+Name="([^"]+)"')

for filename in os.listdir(templates_dir):
    if not filename.endswith(".xml"):
        continue
    filepath = os.path.join(templates_dir, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        matches = part_regex.findall(content)
        for m in matches:
            part_names.add(m)
    except Exception as e:
        pass

print("Unique Part Names found in templates:")
for p in sorted(list(part_names)):
    print(f"  - {p}")
