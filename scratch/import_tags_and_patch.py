# -*- coding: utf-8 -*-
import subprocess
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Chạy patch_man_tong_quan.py để sinh XML màn hình và AI_HMI_Tags.xml
print("=== BƯỚC 1: Chạy patch_man_tong_quan.py ===")
res = subprocess.run([sys.executable, "scratch/patch_man_tong_quan.py"], capture_output=True, text=True, encoding="utf-8")
print(res.stdout)
if res.returncode != 0:
    print("Error: patch_man_tong_quan.py failed!")
    print(res.stderr)
    sys.exit(1)

# 2. Biên dịch C# importer
print("\n=== BƯỚC 2: Biên dịch scratch/import_hmi_tags.cs ===")
csc_path = r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
lib_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch"

cmd = [
    csc_path,
    f'/reference:{os.path.join(lib_dir, "Siemens.Engineering.dll")}',
    f'/reference:{os.path.join(lib_dir, "Siemens.Engineering.Hmi.dll")}',
    '/out:scratch\\import_hmi_tags.exe',
    'scratch\\import_hmi_tags.cs'
]

res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
print(res.stdout)
if res.returncode != 0:
    print("Error: Compilation of import_hmi_tags.cs failed!")
    print(res.stderr)
    sys.exit(1)
print("[OK] Compiled import_hmi_tags.cs to scratch/import_hmi_tags.exe")

# 3. Chạy import_hmi_tags.exe để import HMI tags vào TIA Portal
print("\n=== BƯỚC 3: Chạy scratch/import_hmi_tags.exe ===")
res = subprocess.run(["scratch\\import_hmi_tags.exe"], capture_output=True, text=True, encoding="utf-8")
print(res.stdout)
if res.returncode != 0:
    print("Error: import_hmi_tags.exe failed!")
    print(res.stderr)
    sys.exit(1)

print("\n=== HOÀN THÀNH TOÀN BỘ QUY TRÌNH HMI! ===")
