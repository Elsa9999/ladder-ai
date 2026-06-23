import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.join(ROOT, "projects", "Mixing_Nuoc_Tuong_Maggi_2026")
BACKUP_DIR = os.path.join(ROOT, "scratch", "backup_tags")

# Define files to refactor
files_to_refactor = [
    os.path.join(ROOT, "AGENTS.md"),
    os.path.join(PROJECT_DIR, "generate_mixing_project.py"),
    os.path.join(PROJECT_DIR, "prepare_tia_import_sets.py"),
    os.path.join(PROJECT_DIR, "DEMO_80_PERCENT_CHECKLIST.md"),
    os.path.join(PROJECT_DIR, "TIA_IMPORT_80_PERCENT_CHECKLIST.md"),
    os.path.join(PROJECT_DIR, "watch_tables", "PLC1_Watch_Fake_PLC2_Modbus_Return.csv"),
    os.path.join(PROJECT_DIR, "watch_tables", "PLC1_Watch_Fake_PLC2_Modbus_Return.md"),
    os.path.join(PROJECT_DIR, "watch_tables", "PLC1_Watch_Main_Sequence.csv"),
    os.path.join(PROJECT_DIR, "watch_tables", "PLC1_Watch_Main_Sequence.md"),
    os.path.join(PROJECT_DIR, "watch_tables", "PLC1_Watch_PID_VFD.csv"),
    os.path.join(PROJECT_DIR, "watch_tables", "PLC1_Watch_PID_VFD.md"),
    os.path.join(PROJECT_DIR, "watch_tables", "PLC2_Watch_Fake_PLC1_Modbus_Command.csv"),
    os.path.join(PROJECT_DIR, "watch_tables", "PLC2_Watch_Fake_PLC1_Modbus_Command.md"),
    os.path.join(PROJECT_DIR, "watch_tables", "PLC2_Watch_Main_Sequence.csv"),
    os.path.join(PROJECT_DIR, "watch_tables", "PLC2_Watch_Main_Sequence.md"),
    os.path.join(PROJECT_DIR, "watch_tables", "PLC2_Watch_PID_Sim.csv"),
    os.path.join(PROJECT_DIR, "watch_tables", "PLC2_Watch_PID_Sim.md"),
    os.path.join(PROJECT_DIR, "watch_tables", "WATCH_TEST_PROCEDURE.md"),
    os.path.join(PROJECT_DIR, "watch_tables", "convert_watch_csv_to_xml.py"),
    os.path.join(ROOT, "scratch", "test_plc_logic.py"),
    os.path.join(ROOT, "scratch", "verify_mixing_runtime_fixes.py"),
    os.path.join(ROOT, "scratch", "verify_post_import_export.py"),
]

overrides = {
    "AI_Tags": "PLC_Tags",
    "AI_Tags_PLC1": "PLC_Tags_PLC1",
    "AI_Tags_PLC2": "PLC_Tags_PLC2",
}

tag_pattern = re.compile(r'\bAI_[A-Za-z0-9_]+\b')

def make_backups():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    # Backup original tags XML before modification
    output_dir = os.path.join(PROJECT_DIR, "output")
    for filename in ["AI_Tags_PLC1.xml", "AI_Tags_PLC2.xml"]:
        src = os.path.join(output_dir, filename)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(BACKUP_DIR, filename))
            print(f"Backed up: {filename} to {BACKUP_DIR}")
        else:
            print(f"Warning: {filename} not found in output folder. Proceeding without it.")

def collect_identifiers():
    ai_identifiers = set()
    # Scan all files to find any tag starting with AI_
    for filepath in files_to_refactor:
        if not os.path.exists(filepath):
            continue
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
        matches = tag_pattern.findall(content)
        ai_identifiers.update(matches)
    return sorted(list(ai_identifiers))

def check_collisions(identifiers):
    migration_map = {}
    new_names = set()
    collisions = []
    
    for identifier in identifiers:
        # Avoid stripping AI_ from names like AI_FQ or AI_PLC1 if they match comments
        if identifier in overrides:
            new_name = overrides[identifier]
        else:
            new_name = identifier[3:] # Remove "AI_"
            
        if new_name in new_names:
            collisions.append(f"Duplicate mapping target: '{new_name}' (from '{identifier}')")
        new_names.add(new_name)
        migration_map[identifier] = new_name
        
    if collisions:
        print("\n[ERROR] Direct mapping collisions detected:")
        for col in collisions:
            print(f"  - {col}")
        raise ValueError("Mapping collision check failed. Cannot proceed with refactoring.")
        
    print("Direct mapping collision check passed. All target names are unique.")
    return migration_map

def write_migration_map(migration_map):
    map_path = os.path.join(PROJECT_DIR, "migration_map.csv")
    with open(map_path, 'w', encoding='utf-8') as f:
        f.write("old_identifier,new_identifier\n")
        for old, new in sorted(migration_map.items()):
            f.write(f"{old},{new}\n")
    print(f"Migration map written to: {map_path}")

def perform_refactor(migration_map):
    # Sort old names in descending order of length to avoid replacing substrings first
    sorted_mappings = sorted(migration_map.items(), key=lambda x: len(x[0]), reverse=True)
    
    for filepath in files_to_refactor:
        if not os.path.exists(filepath):
            print(f"Skip non-existing file: {filepath}")
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            encoding = 'utf-8'
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
            encoding = 'latin-1'
            
        original_content = content
        
        for old, new in sorted_mappings:
            pattern = re.compile(rf'\b{re.escape(old)}\b')
            content = pattern.sub(new, content)
            
        # Specific naming rules for XML file extensions in generate_mixing_project.py and prepare_tia_import_sets.py
        for old, new in sorted_mappings:
            content = content.replace(f"{old}.xml", f"{new}.xml")
            
        # AGENTS.md naming rule replacement
        if "AGENTS.md" in filepath:
            content = content.replace('Must start with "AI_" prefix (e.g., AI_Nut_Khoi_Dong).', 'Must start with a letter (A-Z, a-z) (e.g., Nut_Khoi_Dong).')
            content = content.replace('- **Variable/Tag Names, DB Names, HMI Tags**: Vietnamese WITHOUT accents (ASCII-only, A-Z, a-z, 0-9, underscores). Must start with "AI_" prefix (e.g., AI_Nut_Khoi_Dong).',
                                      '- **Variable/Tag Names, DB Names, HMI Tags**: Vietnamese WITHOUT accents (ASCII-only, A-Z, a-z, 0-9, underscores). Must start with a letter (A-Z, a-z).')
            
        if content != original_content:
            with open(filepath, 'w', encoding=encoding) as f:
                f.write(content)
            print(f"Refactored: {os.path.basename(filepath)}")
        else:
            print(f"No changes in: {os.path.basename(filepath)}")

def main():
    print("=================================================")
    print(" PROJECT WIDE IDENTIFIER REFACTOR (REMOVE AI_) ")
    print("=================================================")
    
    make_backups()
    
    identifiers = collect_identifiers()
    print(f"Collected {len(identifiers)} unique 'AI_' identifiers.")
    
    migration_map = check_collisions(identifiers)
    write_migration_map(migration_map)
    
    perform_refactor(migration_map)
    print("Refactoring completed successfully!")

if __name__ == "__main__":
    main()
