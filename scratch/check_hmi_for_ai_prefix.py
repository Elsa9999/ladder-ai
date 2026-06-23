import os
import csv
import re

def main():
    map_path = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\migration_map.csv"
    migration_map = {}
    if os.path.exists(map_path):
        with open(map_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None) # skip header
            for row in reader:
                if len(row) >= 2:
                    migration_map[row[0].strip()] = row[1].strip()
    else:
        print(f"WARNING: migration_map.csv not found at {map_path}")
        return

    # Directories to check
    dirs_to_check = [
        r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual",
        r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens",
        r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Tags",
    ]

    print("=========================================================")
    print(" SCANNING HMI EXPORTS FOR MAPPED LEGACY AI_ TAG REFERENCES")
    print("=========================================================")

    ai_tag_pattern = re.compile(r'\b(AI_[A-Za-z0-9_]+)\b')
    total_matches = 0
    found_by_file = {}

    for d in dirs_to_check:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            for file in files:
                if not file.lower().endswith('.xml'):
                    continue
                file_path = os.path.join(root, file)
                # Try reading as utf-8 or utf-16
                content = ""
                for encoding in ['utf-8', 'utf-16', 'latin-1']:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except Exception:
                        continue
                
                if not content:
                    continue

                lines = content.splitlines()
                for line_idx, line in enumerate(lines, 1):
                    # Find all words starting with AI_
                    matches = ai_tag_pattern.findall(line)
                    for m in matches:
                        if m in migration_map:
                            mapped = migration_map[m]
                            if file_path not in found_by_file:
                                found_by_file[file_path] = []
                            found_by_file[file_path].append((line_idx, m, mapped, line.strip()[:100]))
                            total_matches += 1

    if total_matches == 0:
        print("[OK] No mapped legacy AI_ tags found in HMI exports!")
    else:
        print(f"Found {total_matches} occurrences of mapped legacy AI_ tags in HMI:")
        for fp, occurrences in found_by_file.items():
            print(f"\nFile: {os.path.basename(fp)}")
            # Group by tag name to be concise
            unique_tags = {}
            for line_no, tag, mapped, snippet in occurrences:
                if tag not in unique_tags:
                    unique_tags[tag] = []
                unique_tags[tag].append((line_no, mapped))
            
            for tag, infos in unique_tags.items():
                lines_str = ", ".join(str(i[0]) for i in infos[:5])
                if len(infos) > 5:
                    lines_str += f", ... (total {len(infos)} times)"
                mapped_name = infos[0][1]
                print(f"  · {tag} -> {mapped_name} at lines: {lines_str}")

    print("=========================================================")

if __name__ == "__main__":
    main()
