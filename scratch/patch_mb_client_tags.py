file_path = "projects/Mixing_Nuoc_Tuong_Maggi_2026/prepare_tia_import_sets.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Thay thế các tag Client tự chế thành các tag chuẩn trong tag table
replacements = {
    '"MB_TCP_Write_Req"': '"MB_TCP_REQ"',
    '"MB_TCP_Read_Req"': '"MB_TCP_REQ"',
    '"MB_TCP_Write_Done"': '"MB_TCP_DONE"',
    '"MB_TCP_Read_Done"': '"MB_TCP_DONE"',
    '"MB_TCP_Write_Error"': '"MB_TCP_ERROR"',
    '"MB_TCP_Read_Error"': '"MB_TCP_ERROR"',
    '"MB_TCP_Write_Status"': '"MB_TCP_STATUS"',
    '"MB_TCP_Read_Status"': '"MB_TCP_STATUS"',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("prepare_tia_import_sets.py Modbus Client tags patched successfully.")
