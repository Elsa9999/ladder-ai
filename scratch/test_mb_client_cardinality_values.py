# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
original_main_path = os.path.join(ROOT, "projects", "Mixing_Nuoc_Tuong_Maggi_2026", "tia_import", "PLC_1_Mixing_Import", "Main.xml")

temp_dir = os.path.join(ROOT, "scratch", "test_import_client_no_connect")
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

# Read original Main.xml content
with open(original_main_path, "r", encoding="utf-8") as f:
    content = f.read()

# Make sure version is 3.1, card1200=1, card1500=0
new_content = content.replace('Name="MB_CLIENT" Version="2.1"', 'Name="MB_CLIENT" Version="3.1"')
new_content = new_content.replace(
    '<TemplateValue Name="card1200" Type="Cardinality">1</TemplateValue>',
    '<TemplateValue Name="card1200" Type="Cardinality">1</TemplateValue>'
)
new_content = new_content.replace(
    '<TemplateValue Name="card1500" Type="Type">1</TemplateValue>',
    '<TemplateValue Name="card1500" Type="Cardinality">0</TemplateValue>'
)

# Now remove the CONNECT pin input and wire.
# In Main.xml:
# The CONNECT input is UID 761 (first call) and UID 787 (second call)
# Let's remove them from <Parts>:
# <Access Scope="GlobalVariable" UId="761"><Symbol><Component Name="DB_MB_TCP_Client_Conn_DB" /><Component Name="MB_TCP" /></Symbol></Access>
# <Access Scope="GlobalVariable" UId="787"><Symbol><Component Name="DB_MB_TCP_Client_Conn_DB" /><Component Name="MB_TCP" /></Symbol></Access>
# And from <Wires>:
# <Wire UId="762"><IdentCon UId="761" /><NameCon UId="746" Name="CONNECT" /></Wire>
# <Wire UId="788"><IdentCon UId="787" /><NameCon UId="772" Name="CONNECT" /></Wire>

# We can do this using simple string replacement or regex
# Let's remove the Access tags:
new_content = re.sub(r'<Access Scope="GlobalVariable" UId="(761|787|817|843)"><Symbol><Component Name="DB_MB_TCP_Client_Conn_DB".*?</Access>', '', new_content)
# Let's remove the Wire tags:
new_content = re.sub(r'<Wire UId="(762|788|818|844)"><IdentCon UId="\d+" /><NameCon UId="\d+" Name="CONNECT" /></Wire>', '', new_content)

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
