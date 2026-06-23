# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

xml_path = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\scadabai3_export.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

def get_local_tag(elem):
    return elem.tag.split("}")[-1]

screen = root.find(".//Hmi.Screen.Screen")
if screen is not None:
    attrs = screen.find("AttributeList")
    if attrs is not None:
        for c in attrs:
            print(f"{get_local_tag(c)}: {c.text}")
else:
    print("Hmi.Screen.Screen not found!")
