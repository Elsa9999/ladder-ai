# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens\Hmi.Screen.Screen_2.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

gv = None
for elem in root.iter():
    if elem.tag.endswith("GraphicView"):
        name_el = elem.find("AttributeList/ObjectName")
        if name_el is not None and name_el.text == "Graphic view_1":
            gv = elem
            break

if gv is not None:
    print(f"Tag Name: {gv.tag}")
    print("Attributes:")
    for k, v in gv.attrib.items():
        print(f"  {k} = {v}")
    
    # Print XML string
    ET.indent(gv)
    xml_str = ET.tostring(gv, encoding="utf-8").decode("utf-8")
    print("\n--- XML STRUCTURE ---")
    print(xml_str[:1500])
else:
    print("No Graphic view_1 found!")
