# -*- coding: utf-8 -*-
import os
import shutil
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
original_main_path = os.path.join(ROOT, "projects", "Mixing_Nuoc_Tuong_Maggi_2026", "tia_import", "PLC_1_Mixing_Import", "Main.xml")

temp_dir = os.path.join(ROOT, "scratch", "test_import_cardinality")

combinations = [
    # (card1200_type, card1500_type)
    ("Cardinality", "Type"),
    ("Type", "Cardinality"),
    ("Type", "Type"),
    ("Cardinality", "Cardinality")
]

# Read original Main.xml content
with open(original_main_path, "r", encoding="utf-8") as f:
    content = f.read()

# Make sure version is 3.1
content = content.replace('Name="MB_CLIENT" Version="2.1"', 'Name="MB_CLIENT" Version="3.1"')

for c1200_t, c1500_t in combinations:
    print(f"\n--- Testing card1200={c1200_t}, card1500={c1500_t} ---")
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # We will modify the TemplateValue nodes inside the parts of type MB_CLIENT
    # In the original_main_path, it currently has:
    # <TemplateValue Name="card1200" Type="Cardinality">1</TemplateValue>
    # <TemplateValue Name="card1500" Type="Type">1</TemplateValue>
    # Let's replace them based on our combo
    new_content = content
    new_content = new_content.replace(
        '<TemplateValue Name="card1200" Type="Cardinality">1</TemplateValue>',
        f'<TemplateValue Name="card1200" Type="{c1200_t}">1</TemplateValue>'
    )
    new_content = new_content.replace(
        '<TemplateValue Name="card1500" Type="Type">1</TemplateValue>',
        f'<TemplateValue Name="card1500" Type="{c1500_t}">1</TemplateValue>'
    )
    
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
    
    lines = stdout.splitlines()
    failed = False
    for i, line in enumerate(lines):
        if "FAILED!" in line:
            failed = True
            print(line)
            for j in range(1, 8):
                if i + j < len(lines):
                    print("  " + lines[i+j])
    if not failed:
        print("===> SUCCESS!")
        break

if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
