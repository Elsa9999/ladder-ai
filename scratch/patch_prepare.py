# -*- coding: utf-8 -*-
import re

file_path = 'projects/Mixing_Nuoc_Tuong_Maggi_2026/prepare_tia_import_sets.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace both AddressFamily assignments
# Check exact matches first
print('Original occurrences:', content.count('AddressFamily'))

content = re.sub(r'\s*\(\s*"MOVE"\s*,\s*"2"\s*,\s*"DB_MB_TCP_Client_Conn_DB\.MB_TCP\.AddressFamily"\s*\)\s*,?', '', content)
content = re.sub(r'\s*\(\s*"MOVE"\s*,\s*"2"\s*,\s*"DB_MB_TCP_Server_Conn_DB\.MB_TCP_SERVER\.AddressFamily"\s*\)\s*,?', '', content)

print('After occurrences:', content.count('AddressFamily'))

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done.')
