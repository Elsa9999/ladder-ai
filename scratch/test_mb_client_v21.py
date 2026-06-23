# -*- coding: utf-8 -*-
import os
import shutil
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
original_main_path = os.path.join(ROOT, "projects", "Mixing_Nuoc_Tuong_Maggi_2026", "tia_import", "PLC_1_Mixing_Import", "Main.xml")

temp_dir = os.path.join(ROOT, "scratch", "test_import_v21")
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

# Read original Main.xml content
with open(original_main_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace Version and remove the templates specifically for MB_CLIENT
new_content = content.replace('Name="MB_CLIENT" Version="3.1"', 'Name="MB_CLIENT" Version="2.1"')
new_content = new_content.replace('<TemplateValue Name="card1200" Type="Cardinality">1</TemplateValue>', '')
new_content = new_content.replace('<TemplateValue Name="card1500" Type="Type">1</TemplateValue>', '')

test_file_path = os.path.join(temp_dir, "Main.xml")
with open(test_file_path, "w", encoding="utf-8") as f:
    f.write(new_content)
    
# Run importer tool
cmd = [
    os.path.join(ROOT, "Ladder", "Agent_TIA_Importer_Generic.exe"),
    temp_dir,
    "PLC_1"
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
stdout, stderr = proc.communicate()

print(stdout)
shutil.rmtree(temp_dir)
