# -*- coding: utf-8 -*-
import os

import glob

# Scan all xml files in blocks
files = glob.glob(r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\reference_bai4_readonly_20260622\01_PLC_1\Blocks\*.xml")
print(f"Found {len(files)} XML files.")

for path in files:
    with open(path, "rb") as f:
        data = f.read()
    
    # Try decoding
    for enc in ("utf-16", "utf-8", "utf-16-le"):
        try:
            text = data.decode(enc)
            if "MB_CLIENT" in text:
                print(f"Found MB_CLIENT in: {path} using {enc}")
                lines = text.splitlines()
                for idx, line in enumerate(lines):
                    if "MB_CLIENT" in line:
                        print(f"  Line {idx}: {line}")
                        # print surrounding
                        start = max(0, idx - 5)
                        end = min(len(lines), idx + 15)
                        print("\n".join(lines[start:end]))
                        print("="*40)
                break
        except Exception as e:
            pass
else:
    print("Done scanning.")
