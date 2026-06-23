# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys
import os

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Man Tong Quan.xml"
out_txt = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\man_tong_quan_coords.txt"

if not os.path.exists(xml_path):
    print(f"File not found: {xml_path}")
    sys.exit(1)

tree = ET.parse(xml_path)
root = tree.getroot()

items = []
for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    attrs = elem.find("AttributeList")
    if attrs is not None:
        obj_name = attrs.find("ObjectName")
        if obj_name is not None:
            left = int(attrs.find("Left").text) if attrs.find("Left") is not None else 0
            top = int(attrs.find("Top").text) if attrs.find("Top") is not None else 0
            width = int(attrs.find("Width").text) if attrs.find("Width") is not None else 0
            height = int(attrs.find("Height").text) if attrs.find("Height") is not None else 0
            
            pic_list = ""
            links = elem.find("LinkList")
            if links is not None:
                pic_el = links.find(".//PictureList") or links.find(".//Picture")
                if pic_el is not None:
                    name_el = pic_el.find("Name")
                    if name_el is not None:
                        pic_list = name_el.text
            
            items.append((tag_local, obj_name.text, left, top, width, height, pic_list))

# Sort by Left, then Top
items.sort(key=lambda x: (x[2], x[3]))

with open(out_txt, "w", encoding="utf-8") as f:
    f.write("=== MAN TONG QUAN COORDINATES ===\n")
    for tag_local, name, left, top, w, h, pic in items:
        f.write(f"Type: {tag_local:25s} | Name: {name:25s} | Left: {left:4d} | Top: {top:4d} | Size: {w:3d}x{h:3d} | PicList/Pic: {pic}\n")

print("Done listing coordinates.")
