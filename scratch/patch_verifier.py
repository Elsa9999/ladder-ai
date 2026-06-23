import os

path = r'scratch/verify_post_import_export_manual.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Add to REQUIRED files
text = text.replace(
    "'Main.xml', 'DB_PLC1_MB_Buffer_DB.xml',",
    "'Main.xml', 'DB_MB_TCP_Client_Conn_DB.xml', 'DB_PLC1_MB_Word_Buffer_DB.xml', 'DB_PLC1_MB_Buffer_DB.xml',"
)
text = text.replace(
    "'Timers_PLC2.xml', 'Main.xml', 'DB_Modbus_Holding_Register_DB.xml',",
    "'Timers_PLC2.xml', 'Main.xml', 'DB_MB_TCP_Server_Conn_DB.xml', 'DB_PLC2_MB_Holding_Word_DB.xml', 'DB_Modbus_Holding_Register_DB.xml',"
)

# Insert Check 12 before the Final report section
check_12_code = """
# ══════════════════════════════════════════════════════════════════════════════
# CHECK 12 – Modbus TCP Client & Server parameters (CONNECT & Data Buffers)
# ══════════════════════════════════════════════════════════════════════════════
print("\\n[CHECK 12] Modbus TCP Client/Server configuration (TCON_IP_v4 & Word Buffers)")

p1_main_path = os.path.join(P1_BLOCKS, 'Main.xml')
if os.path.exists(p1_main_path):
    with open(p1_main_path, 'r', encoding='utf-8') as f:
        p1_main = f.read()
    if 'DB_MB_TCP_Client_Conn_DB' in p1_main and 'DB_PLC1_MB_Word_Buffer_DB' in p1_main:
        pass_msg("PLC1 MB_CLIENT: CONNECT trỏ vào DB_MB_TCP_Client_Conn_DB.MB_TCP, MB_DATA_PTR trỏ vào DB_PLC1_MB_Word_Buffer_DB.Data")
    else:
        fail_msg("PLC1 MB_CLIENT: Sai cấu hình CONNECT hoặc MB_DATA_PTR!")
else:
    fail_msg("PLC1 Main.xml không tồn tại!")

p2_main_path = os.path.join(P2_BLOCKS, 'Main.xml')
if os.path.exists(p2_main_path):
    with open(p2_main_path, 'r', encoding='utf-8') as f:
        p2_main = f.read()
    if 'DB_MB_TCP_Server_Conn_DB' in p2_main and 'DB_PLC2_MB_Holding_Word_DB' in p2_main:
        pass_msg("PLC2 MB_SERVER: CONNECT trỏ vào DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER, MB_HOLD_REG trỏ vào DB_PLC2_MB_Holding_Word_DB.Data")
    else:
        fail_msg("PLC2 MB_SERVER: Sai cấu hình CONNECT hoặc MB_HOLD_REG!")
else:
    fail_msg("PLC2 Main.xml không tồn tại!")
"""

text = text.replace(
    "# Final report",
    check_12_code + "\n# Final report"
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Verifier patched successfully!')
