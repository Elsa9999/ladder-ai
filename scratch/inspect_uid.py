# -*- coding: utf-8 -*-
import os

path = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\tia_import\PLC_1_Mixing_Import\Main.xml"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find('UId="1239"')
if idx != -1:
    text = content[idx-1000:idx+1500]
    print(text.encode('ascii', errors='ignore').decode('ascii'))
else:
    print("UID 1239 not found")
