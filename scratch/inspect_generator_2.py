# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("projects/Mixing_Nuoc_Tuong_Maggi_2026/generate_mixing_project.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

search_terms = ["DB_MB_TCP_Client_Conn_DB", "DB_MB_TCP_Server_Conn_DB", "build_tcon", "build_conn", "Client_Conn", "Server_Conn", "write_xml", "generate_xml"]

for term in search_terms:
    print(f"=== Matches for '{term}' ===")
    for i, line in enumerate(lines):
        if term in line:
            print(f"Line {i+1}: {line.strip()}")
