import os
import re

dir_path = r'd:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026'

output = []
for root, dirs, files in os.walk(dir_path):
    if 'post_import_export' in root or 'tia_import' in root or 'tia_current_export' in root or 'tia_check_export' in root:
        continue
    for file in files:
        if file.endswith(('.py', '.md')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                lines = content.splitlines()
                for idx, line in enumerate(lines):
                    if re.search(r'Bon2|B\xf4n\s*2', line, re.IGNORECASE):
                        safe_line = line.encode('ascii', errors='replace').decode('ascii')
                        output.append(f"{os.path.basename(path)}:{idx+1}: {safe_line.strip()}")
            except Exception as e:
                output.append(f"Error reading {file}: {e}")

with open(r'd:\AI_Agent_PLC_LADDER_ONLY\scratch\bon2_mentions_utf8.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("Done writing mentions")
