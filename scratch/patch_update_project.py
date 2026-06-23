import os

path = r'scratch/update_tia_project.cs'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. PLC1 Imports
text = text.replace(
    '"DB_PLC1_MB_Buffer_DB.xml",',
    '"DB_MB_TCP_Client_Conn_DB.xml",\n            "DB_PLC1_MB_Word_Buffer_DB.xml",\n            "DB_PLC1_MB_Buffer_DB.xml",'
)

# 2. PLC2 Imports
text = text.replace(
    '"DB_Modbus_Holding_Register_DB.xml",',
    '"DB_MB_TCP_Server_Conn_DB.xml",\n            "DB_PLC2_MB_Holding_Word_DB.xml",\n            "DB_Modbus_Holding_Register_DB.xml",'
)

# 3. PLC1 Exports
text = text.replace(
    '"DB_PLC1_MB_Buffer_DB",',
    '"DB_MB_TCP_Client_Conn_DB",\n            "DB_PLC1_MB_Word_Buffer_DB",\n            "DB_PLC1_MB_Buffer_DB",'
)

# 4. PLC2 Exports
text = text.replace(
    '"DB_Modbus_Holding_Register_DB",',
    '"DB_MB_TCP_Server_Conn_DB",\n            "DB_PLC2_MB_Holding_Word_DB",\n            "DB_Modbus_Holding_Register_DB",'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Patched successfully!')
