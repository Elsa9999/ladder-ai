import os
import re

blocks_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\raw_exports\PLSP_export\PLC_1\Blocks"

if not os.path.exists(blocks_dir):
    print("Blocks directory not found")
else:
    all_parts = set()
    for filename in os.listdir(blocks_dir):
        if filename.endswith(".xml"):
            filepath = os.path.join(blocks_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Check ProgrammingLanguage attribute of block
                lang_match = re.search(r'<ProgrammingLanguage>([^<]+)</ProgrammingLanguage>', content)
                lang = lang_match.group(1) if lang_match else "Unknown"
                
                # Check Part names
                part_names = re.findall(r'<Part\s+Name="([^"]+)"', content, re.IGNORECASE)
                for part in part_names:
                    all_parts.add(part)
                
                print(f"Block: {filename} | Language: {lang}")
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                
    print("\nUnique parts found in all blocks:")
    for part in sorted(list(all_parts)):
        print(f"  - {part}")
