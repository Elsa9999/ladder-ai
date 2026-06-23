# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys
import os

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Man Tong Quan.xml"
out_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\man_tong_quan_elements.txt"

if not os.path.exists(xml_path):
    print(f"File not found: {xml_path}")
    sys.exit(1)

tree = ET.parse(xml_path)
root = tree.getroot()

text_fields = []
io_fields = []

for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    if tag_local.endswith("TextField"):
        text_fields.append(elem)
    elif tag_local.endswith("IOField") and not tag_local.endswith("GraphicIOField") and not tag_local.endswith("SymbolicIOField"):
        io_fields.append(elem)

with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"Total TextFields: {len(text_fields)}\n")
    f.write(f"Total IOFields: {len(io_fields)}\n")
    f.write("=" * 60 + "\n")

    f.write("\n--- TEXT FIELDS ---\n")
    for tf in text_fields:
        attrs = tf.find(".//AttributeList")
        if attrs is None:
            continue
        obj_name = attrs.find("ObjectName").text if attrs.find("ObjectName") is not None else "Unknown"
        left = attrs.find("Left").text if attrs.find("Left") is not None else "N/A"
        top = attrs.find("Top").text if attrs.find("Top") is not None else "N/A"
        width = attrs.find("Width").text if attrs.find("Width") is not None else "N/A"
        height = attrs.find("Height").text if attrs.find("Height") is not None else "N/A"
        
        text_val = ""
        objs = tf.find(".//ObjectList")
        if objs is not None:
            for txt_el in objs.findall(".//Hmi.Screen.MultilingualText") + objs.findall(".//MultilingualText"):
                pname = txt_el.find("AttributeList/Name")
                if pname is not None and pname.text == "Text":
                    for trans in txt_el.findall(".//Hmi.Screen.Translation") + txt_el.findall(".//Translation"):
                        lang_el = trans.find(".//Culture")
                        val_el = trans.find(".//Value")
                        if lang_el is not None and val_el is not None:
                            text_val += f"[{lang_el.text}: {val_el.text}] "
                            
        f.write(f"Name: {obj_name} | Pos: ({left}, {top}) | Size: {width}x{height}\n")
        f.write(f"  Text: {text_val}\n")
        f.write("-" * 40 + "\n")

    f.write("\n--- IO FIELDS ---\n")
    for io in io_fields:
        attrs = io.find(".//AttributeList")
        if attrs is None:
            continue
        obj_name = attrs.find("ObjectName").text if attrs.find("ObjectName") is not None else "Unknown"
        left = attrs.find("Left").text if attrs.find("Left") is not None else "N/A"
        top = attrs.find("Top").text if attrs.find("Top") is not None else "N/A"
        width = attrs.find("Width").text if attrs.find("Width") is not None else "N/A"
        height = attrs.find("Height").text if attrs.find("Height") is not None else "N/A"
        fp = attrs.find("FormatPattern").text if attrs.find("FormatPattern") is not None else "None"
        mode = attrs.find("Mode").text if attrs.find("Mode") is not None else "None"
        
        tag_name = "None"
        objs = io.find(".//ObjectList")
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
                                
        f.write(f"Name: {obj_name} | Pos: ({left}, {top}) | Size: {width}x{height}\n")
        f.write(f"  FormatPattern: {fp} | Mode: {mode}\n")
        f.write(f"  Bound Tag: {tag_name}\n")
        f.write("-" * 40 + "\n")

print("Done generating report.")
