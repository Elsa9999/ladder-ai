# -*- coding: utf-8 -*-
import os

for root, dirs, files in os.walk(r"projects\Mixing_Nuoc_Tuong_Maggi_2026\tia_import"):
    for f in files:
        if f == "Main.xml":
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file_obj:
                content = file_obj.read()
                parts = ["GET", "PUT", "MB_COMM_LOAD", "MB_MASTER"]
                found = [p for p in parts if f'Name="{p}"' in content]
                print(f"{path} contains parts: {found}")
