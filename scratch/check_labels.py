import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

screens = ["scadabai3", "scadabai4", "scadabai5", "scadabai6", "scadabai7"]

for sc in screens:
    path = f"d:/AI_Agent_PLC_LADDER_ONLY/scratch/{sc}_export.xml"
    print(f"\n=== Labels in {sc} ===")
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        text_vals = []
        for elem in root.findall(".//{http://www.siemens.com/automation/Openness/SW/Interface/v5}TextField") or root.findall(".//Hmi.Screen.TextField"):
            text_el = elem.find(".//Text")
            if text_el is not None:
                txt = "".join(text_el.itertext()).strip()
                if txt:
                    text_vals.append(txt)
        print("First 20 labels:")
        for t in sorted(list(set(text_vals)))[:20]:
            print("  ", t)
    except Exception as e:
        print("Error:", e)
