# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("Ladder/Export_Device_ByName.cs", "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if "Export" in line or "Directory" in line or "Path" in line or "Folder" in line or "Write" in line:
            print(f"Line {i}: {line.strip()}")
