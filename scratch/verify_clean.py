# -*- coding: utf-8 -*-
import os

import_dir = "projects/Mixing_Nuoc_Tuong_Maggi_2026/tia_import"
is_clean = True

for root, dirs, files in os.walk(import_dir):
    for f in files:
        if f.endswith(".xml"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file_obj:
                content = file_obj.read()
                
                # Check for GET or PUT block calls in TIA Openness XML
                # In SimaticML, GET/PUT calls will be like <CallInfo Name="GET" ...> or <CallInfo Name="PUT" ...>
                # and NOT comments or family names. Let's do a strict check:
                if 'Name="GET"' in content or 'Name="PUT"' in content:
                    print(f"  [FAIL] File {f} contains GET/PUT block call!")
                    is_clean = False

if is_clean:
    print("Verification success: No GET/PUT block calls found in any XML files.")
else:
    print("Verification failed: GET/PUT references were found.")
