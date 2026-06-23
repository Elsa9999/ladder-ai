# -*- coding: utf-8 -*-
import hashlib
import os

files_to_hash = [
    r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_1_readback.xml",
    r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_2_readback.xml",
    r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_3_readback.xml",
    r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_4_readback.xml",
    r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags_readback.xml"
]

print("========================================")
print(" SHA256 HASHES FOR EXPORTED READBACKS")
print("========================================")

for fpath in files_to_hash:
    if os.path.exists(fpath):
        hasher = hashlib.sha256()
        with open(fpath, "rb") as f:
            buf = f.read()
            hasher.update(buf)
        print(f"{os.path.basename(fpath)}: {hasher.hexdigest()}")
    else:
        print(f"{os.path.basename(fpath)}: NOT FOUND!")
