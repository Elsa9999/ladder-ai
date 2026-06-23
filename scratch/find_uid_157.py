import xml.etree.ElementTree as ET
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

filepath = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\tia_import\PLC_1_Mixing_Import\Main.xml"
tree = ET.parse(filepath)
root = tree.getroot()

for cu in root.findall(".//{*}SW.Blocks.CompileUnit"):
    found = False
    for elem in cu.iter():
        if elem.attrib.get("UId") == "157":
            found = True
            break
    if found:
        print(f"Found compile unit containing UId 157:")
        ET.dump(cu)
        break
