import os
import re

download_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\downloaded_projects"
valid_xml_blocks = []

block_pattern = re.compile(r'<SW\.Blocks\.(FB|FC|OB|DB|InstanceDB|InstanceDBOf)', re.IGNORECASE)

for root_dir, dirs, files in os.walk(download_dir):
    for filename in files:
        if not filename.endswith(".xml"):
            continue
        filepath = os.path.join(root_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                # Read first 1000 characters to check if it's a TIA block XML
                head = f.read(1000)
                if block_pattern.search(head):
                    valid_xml_blocks.append(filepath)
        except Exception as e:
            pass

print(f"--- SCAN COMPLETED ---")
print(f"Found {len(valid_xml_blocks)} valid TIA Portal XML block files:")
for path in valid_xml_blocks[:15]:
    print(f"  - {os.path.relpath(path, download_dir)}")
if len(valid_xml_blocks) > 15:
    print(f"  ... and {len(valid_xml_blocks) - 15} more block XML files.")
