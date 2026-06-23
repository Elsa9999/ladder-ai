# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys
import os

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Man Tong Quan.xml"
out_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\all_screen_items.txt"

if not os.path.exists(xml_path):
    print(f"File not found: {xml_path}")
    sys.exit(1)

tree = ET.parse(xml_path)
root = tree.getroot()

items = []
for elem in root.iter():
    attrs = elem.find("AttributeList")
    if attrs is not None:
        obj_name = attrs.find("ObjectName")
        if obj_name is not None:
            tag_local = elem.tag.split('}')[-1]
            items.append((tag_local, obj_name.text, elem))

# Sort items by coordinate if possible, or just write them
with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"Total elements with ObjectName: {len(items)}\n")
    f.write("=" * 60 + "\n")
    for tag_local, name, elem in items:
        attrs = elem.find("AttributeList")
        left = attrs.find("Left").text if attrs.find("Left") is not None else "N/A"
        top = attrs.find("Top").text if attrs.find("Top") is not None else "N/A"
        width = attrs.find("Width").text if attrs.find("Width") is not None else "N/A"
        height = attrs.find("Height").text if attrs.find("Height") is not None else "N/A"
        
        # Check text or bound tag if applicable
        text_val = ""
        objs = elem.find("ObjectList")
        if objs is not None:
            for txt_el in objs.findall(".//Hmi.Screen.MultilingualText") + objs.findall(".//MultilingualText"):
                pname = txt_el.find("AttributeList/Name")
                if pname is not None and pname.text == "Text":
                    for trans in txt_el.findall(".//Hmi.Screen.Translation") + txt_el.findall(".//Translation"):
                        lang_el = trans.find(".//Culture")
                        val_el = trans.find(".//Value")
                        if lang_el is not None and val_el is not None:
                            text_val += f"[{lang_el.text}: {val_el.text}] "
                            
        tag_name = "None"
        if objs is not None:
            for prop in objs.findall(".//Hmi.Screen.Property") + objs.findall(".//Property"):
                pname = prop.find("AttributeList/Name")
                if pname is not None and pname.text == "ProcessValue":
                    tag_conn = prop.find(".//Hmi.Dynamic.TagConnectionDynamic") or prop.find(".//TagConnectionDynamic")
                    if tag_conn is not None:
                        tag_el = tag_conn.find(".//Tag")
                        if tag_el is not None:
                            name_el = tag_el.find("Name")
                            if name_el is not None:
                                tag_name = name_el.text
                                
        f.write(f"Type: {tag_local} | Name: {name} | Pos: ({left}, {top}) | Size: {width}x{height}\n")
        if text_val:
            f.write(f"  Text: {text_val}\n")
        if tag_name != "None":
            f.write(f"  Bound Tag: {tag_name}\n")
        f.write("-" * 50 + "\n")

print("Done listing items.")
