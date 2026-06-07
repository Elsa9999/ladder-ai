# -*- coding: utf-8 -*-
import re

file_path = "projects/Mixing_Nuoc_Tuong_Maggi_2026/prepare_tia_import_sets.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# DB names to rename
renames = {
    "DB_PLC1_Send_To_PLC2": "DB_PLC1_Send_To_PLC2_DB",
    "DB_PLC1_Recv_From_PLC2": "DB_PLC1_Recv_From_PLC2_DB",
    "DB_MB_TCP_Client_Conn": "DB_MB_TCP_Client_Conn_DB",
    "DB_MB_TCP_Server_Conn": "DB_MB_TCP_Server_Conn_DB",
    "DB_Modbus_Holding_Register": "DB_Modbus_Holding_Register_DB"
}

new_content = content
for old_name, new_name in renames.items():
    # Replace old_name with new_name only if it is not already ending with _DB
    # We can use regex word boundary or simple replace for old_name + ".xml" and old_name + "." etc.
    # A safe way is using word boundaries but checking if it's followed by _DB
    pattern = r'\b' + re.escape(old_name) + r'\b(?!_DB)'
    new_content = re.sub(pattern, new_name, new_content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Replacement done successfully.")
