# -*- coding: utf-8 -*-
import os
import re
import json
import sys

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

main_xml = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\raw_exports\PLSP_export\PLC_1\Blocks\Main.xml"
patterns_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\patterns"

target_dir = os.path.join(patterns_dir, "timer_counter", "ctud")
os.makedirs(target_dir, exist_ok=True)

with open(main_xml, "r", encoding="utf-8") as f:
    content = f.read()
    
compile_unit_re = re.compile(r'(<SW\.Blocks\.CompileUnit[^>]*>.*?</SW\.Blocks\.CompileUnit>)', re.DOTALL)
compile_units = compile_unit_re.findall(content)
ctud_xml = compile_units[10] # Network 11

# Placeholders Mapping
mapping = {
    "TransferingRight": "{{BOOL_COUNT_UP}}",
    "I_At_right_exit": "{{BOOL_COUNT_DOWN}}",
    "P_At_right_exit": "{{BOOL_MEM_P}}",
    "RightCounter": "{{DB_INSTANCE}}"
}

# Apply mappings
for old, new in mapping.items():
    pattern = r'Component\s+Name\s*=\s*"' + re.escape(old) + r'"'
    ctud_xml = re.sub(pattern, f'Component Name="{new}"', ctud_xml)

# Replace Title and Comments to be more descriptive and in Vietnamese
# Remove english comments
ctud_xml = re.sub(
    r'<Text>Increment number of boxes when starting the transfer\s+Decrement when exiting</Text>',
    '<Text>Tăng số lượng sản phẩm khi vào băng tải, giảm khi đi ra.</Text>',
    ctud_xml
)
ctud_xml = re.sub(
    r'<Text>Right Conveyor</Text>',
    '<Text>Băng tải đếm sản phẩm</Text>',
    ctud_xml
)

# Re-indexing UId and ID
uid_map = {}
id_map = {}

def uid_repl(match):
    old_uid = match.group(1)
    if old_uid not in uid_map:
        uid_map[old_uid] = str(len(uid_map) + 21)
    return f'UId="{uid_map[old_uid]}"'
    
def id_repl(match):
    old_id = match.group(1)
    if old_id not in id_map:
        id_map[old_id] = str(len(id_map) + 1)
    return f'ID="{id_map[old_id]}"'

ctud_xml = re.sub(r'UId="([0-9a-zA-Z_]+)"', uid_repl, ctud_xml)
ctud_xml = re.sub(r'ID="([0-9a-zA-Z_]+)"', id_repl, ctud_xml)

# Write pattern.xml
with open(os.path.join(target_dir, "pattern.xml"), "w", encoding="utf-8") as f:
    f.write(ctud_xml)

# Write manifest.json
manifest_data = {
    "tia_version": "V18",
    "plc_family": "S7-1200",
    "language": "LAD",
    "block_instruction_name": "CTUD",
    "tested_status": "compiled",
    "required_tags": [
        {"name": "{{BOOL_COUNT_UP}}", "type": "Bool"},
        {"name": "{{BOOL_COUNT_DOWN}}", "type": "Bool"},
        {"name": "{{BOOL_MEM_P}}", "type": "Bool"}
    ],
    "required_dbs": [],
    "required_instance_db": "{{DB_INSTANCE}}",
    "required_data_types": []
}

with open(os.path.join(target_dir, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest_data, f, ensure_ascii=False, indent=2)

# Write README.md
readme_content = """# Mẫu khối CTUD
Bộ đếm tiến/lùi tích hợp CTUD (Counter Up/Down) dùng để tăng/giảm số lượng sản phẩm trên băng tải.
"""
with open(os.path.join(target_dir, "README.md"), "w", encoding="utf-8") as f:
    f.write(readme_content)

# Write compile_notes.md
compile_notes_content = """# Lưu ý biên dịch
Yêu cầu khai báo khối DB Instance kiểu IEC_COUNTER cho bộ đếm {{DB_INSTANCE}}.
"""
with open(os.path.join(target_dir, "compile_notes.md"), "w", encoding="utf-8") as f:
    f.write(compile_notes_content)

print("[SUCCESS] Integrated 'ctud' successfully into patterns/timer_counter/ctud")
