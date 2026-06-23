# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys
import os

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen_1_readback.xml"

if not os.path.exists(xml_path):
    print(f"File not found: {xml_path}")
    sys.exit(1)

tree = ET.parse(xml_path)
root = tree.getroot()

gio_fields = []
for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    if tag_local.endswith("GraphicIOField"):
        attrs = elem.find("AttributeList")
        if attrs is not None:
            obj_name = attrs.find("ObjectName").text if attrs.find("ObjectName") is not None else "Unknown"
            left = attrs.find("Left").text if attrs.find("Left") is not None else "N/A"
            top = attrs.find("Top").text if attrs.find("Top") is not None else "N/A"
            width = attrs.find("Width").text if attrs.find("Width") is not None else "N/A"
            height = attrs.find("Height").text if attrs.find("Height") is not None else "N/A"
            
            pic_list = "None"
            links = elem.find("LinkList")
            if links is not None:
                pic_el = links.find(".//PictureList") or links.find(".//Picture")
                if pic_el is not None:
                    name_el = pic_el.find("Name")
                    if name_el is not None:
                        pic_list = name_el.text
            
            gio_fields.append((obj_name, left, top, width, height, pic_list))

print(f"Total GraphicIOFields: {len(gio_fields)}")
for name, left, top, width, height, pic in sorted(gio_fields, key=lambda x: (int(x[2]) if x[2] != 'N/A' else 0, int(x[1]) if x[1] != 'N/A' else 0)):
    print(f"Name: {name} | Pos: ({left}, {top}) | Size: {width}x{height} | PicList: {pic}")
