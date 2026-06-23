# -*- coding: utf-8 -*-
import os
import re
import shutil
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
original_main_path = os.path.join(ROOT, "projects", "Mixing_Nuoc_Tuong_Maggi_2026", "tia_import", "PLC_2_Mixing_Import", "Main.xml")

temp_dir = os.path.join(ROOT, "scratch", "test_import_server_v31")
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

with open(original_main_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace MB_SERVER version with 3.1, and add TemplateValues
# Let's find <Part Name="MB_SERVER" Version="5.3" UId="22">
# and replace it with:
# <Part Name="MB_SERVER" Version="3.1" UId="22">
#   <TemplateValue Name="card1200" Type="Cardinality">1</TemplateValue>
#   <TemplateValue Name="card1500" Type="Cardinality">0</TemplateValue>

new_content = re.sub(
    r'<Part Name="MB_SERVER" Version="[^"]+" UId="([^"]+)">(\s*)<Instance Scope="GlobalVariable" UId="([^"]+)">(\s*)<Component Name="([^"]+)" />(\s*)</Instance>',
    r'<Part Name="MB_SERVER" Version="3.1" UId="\1">\2<Instance Scope="GlobalVariable" UId="\3">\4<Component Name="\5" />\6</Instance>\2<TemplateValue Name="card1200" Type="Cardinality">1</TemplateValue>\2<TemplateValue Name="card1500" Type="Cardinality">0</TemplateValue>',
    content
)

test_file_path = os.path.join(temp_dir, "Main.xml")
with open(test_file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

cmd = [
    os.path.join(ROOT, "Ladder", "Agent_TIA_Importer_Generic.exe"),
    temp_dir,
    "PLC_2"
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
stdout, stderr = proc.communicate()

print(stdout)
shutil.rmtree(temp_dir)
