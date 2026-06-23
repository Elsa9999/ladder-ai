# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen_1_readback.xml"

tree = ET.parse(xml_path)
root = tree.getroot()

for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    if tag_local == "Hmi.Screen.GraphicIOField":
        attrs = elem.find("AttributeList")
        if attrs is not None:
            name_el = attrs.find("ObjectName")
            if name_el is not None and name_el.text == "Graphic I/O field_38":
                print("--- FOUND GRAPHIC I/O FIELD_38 ---")
                ET.indent(elem)
                xml_str = ET.tostring(elem, encoding="utf-8").decode("utf-8")
                print(xml_str[:1500])
                break
