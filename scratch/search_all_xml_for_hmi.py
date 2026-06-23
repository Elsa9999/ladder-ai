# -*- coding: utf-8 -*-
import os
import glob

search_root = r"D:\AI_Agent_PLC_LADDER_ONLY"
target_term = "LT3203"

print(f"Searching all XML files under {search_root} for '{target_term}'...")

found_files = []
for root, dirs, files in os.walk(search_root):
    # Skip git and cache dirs
    if ".git" in root or "__pycache__" in root or ".gemini" in root:
        continue
    for file in files:
        if file.endswith(".xml"):
            full_path = os.path.join(root, file)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if target_term in content:
                        found_files.append((full_path, len(content)))
            except Exception as e:
                pass

print(f"Found {len(found_files)} files containing '{target_term}':")
for path, size in found_files:
    print(f"  - {os.path.relpath(path, search_root)} ({size:,} bytes)")
