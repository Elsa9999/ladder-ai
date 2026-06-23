# -*- coding: utf-8 -*-
import os
import shutil
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
original_main_path = os.path.join(ROOT, "projects", "Mixing_Nuoc_Tuong_Maggi_2026", "tia_import", "PLC_2_Mixing_Import", "Main.xml")

temp_dir = os.path.join(ROOT, "scratch", "test_import_server_version")
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

versions_to_test = ["3.1", "2.0", "2.1", "3.0", "4.0", "5.0", "5.1", "5.2", "5.3"]

with open(original_main_path, "r", encoding="utf-8") as f:
    content = f.read()

for ver in versions_to_test:
    print(f"\n--- Testing MB_SERVER Version: {ver} ---")
    
    # Replace Name="MB_SERVER" Version="..." with the version we are testing
    # First find whatever version is currently in the file by looking at the manifest / source
    # The source might have Name="MB_SERVER" Version="5.3"
    import re
    new_content = re.sub(r'Name="MB_SERVER" Version="[^"]+"', f'Name="MB_SERVER" Version="{ver}"', content)
    
    test_file_path = os.path.join(temp_dir, "Main.xml")
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    cmd = [
        os.path.join(ROOT, "Ladder", "Agent_TIA_Importer_Generic.exe"),
        temp_dir,
        "PLC_2"
    ]
    
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    stdout, stderr = proc.communicate()
    
    lines = stdout.splitlines()
    failed = False
    for i, line in enumerate(lines):
        if "FAILED!" in line:
            failed = True
            print(line)
            for j in range(1, 12):
                if i + j < len(lines):
                    print("  " + lines[i+j])
    if not failed:
        print(f"===> SUCCESS FOR VERSION: {ver}")

shutil.rmtree(temp_dir)
