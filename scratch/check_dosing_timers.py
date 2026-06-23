import re

file_path = r'd:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\generate_mixing_project.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
for idx, line in enumerate(lines):
    if re.search(r'dosing|5s|20s|T#|TON', line, re.IGNORECASE):
        # Remove non-ascii characters for clean printing or replace them
        safe_line = line.encode('ascii', errors='replace').decode('ascii')
        output_lines.append(f"{idx+1}: {safe_line.strip()}")

with open(r'd:\AI_Agent_PLC_LADDER_ONLY\scratch\dosing_timers_search_results.txt', 'w', encoding='utf-8') as out_f:
    out_f.write('\n'.join(output_lines))

print(f"Done, wrote {len(output_lines)} lines to results file.")
