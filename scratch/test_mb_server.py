# -*- coding: utf-8 -*-
import os
import shutil
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
original_main_path = os.path.join(ROOT, "projects", "Mixing_Nuoc_Tuong_Maggi_2026", "tia_import", "PLC_2_Mixing_Import", "Main.xml")

temp_dir = os.path.join(ROOT, "scratch", "test_import_server_v31")
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

# Read original Main.xml content
with open(original_main_path, "r", encoding="utf-8") as f:
    content = f.read()

# Make sure version is 3.1, card1200=1, card1500=0
new_content = content.replace('Name="MB_SERVER" Version="3.1"', 'Name="MB_SERVER" Version="3.1"')
# In original Main.xml of PLC2, it should already be 3.1 since we regenerated, let's verify or replace
# The templates generated are:
# <TemplateValue Name="card1200" Type="Cardinality">1</TemplateValue>
# <TemplateValue Name="card1500" Type="Type">1</TemplateValue>
# Let's change card1500 Type to Cardinality and set its value to 0, card1200 to 1
new_content = new_content.replace(
    '<TemplateValue Name="card1200" Type="Cardinality">1</TemplateValue>',
    '<TemplateValue Name="card1200" Type="Cardinality">1</TemplateValue>'
)
new_content = new_content.replace(
    '<TemplateValue Name="card1500" Type="Type">1</TemplateValue>',
    '<TemplateValue Name="card1500" Type="Cardinality">0</TemplateValue>'
)

test_file_path = os.path.join(temp_dir, "Main.xml")
with open(test_file_path, "w", encoding="utf-8") as f:
    f.write(new_content)
    
# Run importer tool for PLC_2
cmd = [
    os.path.join(ROOT, "Ladder", "Agent_TIA_Importer_Generic.exe"),
    temp_dir,
    "PLC_2"
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
stdout, stderr = proc.communicate()

print(stdout)
shutil.rmtree(temp_dir)
