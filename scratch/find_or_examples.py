import os
import glob

files = glob.glob("**/*.xml", recursive=True)
found = 0
for f in files:
    if "node_modules" in f or ".git" in f:
        continue
    try:
        with open(f, "r", encoding="utf-8") as file:
            for line_no, line in enumerate(file, 1):
                if '<Part Name="O"' in line:
                    print(f"{f}:{line_no} -> {line.strip()}")
                    found += 1
                    if found > 20:
                        break
    except Exception:
        pass
    if found > 20:
        break
