import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.join(ROOT, "projects", "Mixing_Nuoc_Tuong_Maggi_2026")

patterns_to_scan = [
    os.path.join(PROJECT_DIR, "generate_mixing_project.py"),
    os.path.join(PROJECT_DIR, "prepare_tia_import_sets.py"),
    os.path.join(PROJECT_DIR, "watch_tables"),
    os.path.join(ROOT, "scratch"),
    os.path.join(ROOT, "harness"),
    os.path.join(ROOT, "AGENTS.md"),
]

exclude_extensions = {'.exe', '.dll', '.pdf', '.png', '.jpg', '.zip', '.tar', '.gz', '.pyc'}
exclude_dirs = {'__pycache__', '.git', '.agent', 'post_import_export', 'tia_import', 'compat_exports', 'tia_check_export', 'output'}

tag_pattern = re.compile(r'\bAI_[A-Za-z0-9_]+\b')

results = {}

def scan_file(filepath):
    if any(filepath.endswith(ext) for ext in exclude_extensions):
        return
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception:
            return
    except Exception:
        return

    matches = tag_pattern.findall(content)
    if matches:
        rel_path = os.path.relpath(filepath, ROOT)
        results[rel_path] = {
            'count': len(matches),
            'unique_matches': sorted(list(set(matches)))
        }

def scan_dir(dirpath):
    for root, dirs, files in os.walk(dirpath):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            scan_file(os.path.join(root, file))

for path in patterns_to_scan:
    if os.path.isdir(path):
        scan_dir(path)
    elif os.path.isfile(path):
        scan_file(path)

print(f"Scanned files. Found {len(results)} files with 'AI_' identifiers:")
total_matches = 0
for file, data in sorted(results.items()):
    print(f"- {file}: {data['count']} occurrences, {len(data['unique_matches'])} unique identifiers")
    total_matches += data['count']
print(f"Total 'AI_' occurrences: {total_matches}")
