# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

xml_path = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\scadabai3_export.xml"
if not os.path.exists(xml_path):
    print("Error: file not found at", xml_path)
    exit(1)

tree = ET.parse(xml_path)
root = tree.getroot()

def get_local_tag(elem):
    return elem.tag.split("}")[-1]

def find_local(elem, name):
    for child in elem:
        if get_local_tag(child) == name:
            return child
    return None

# Find ScreenLayer
layer = None
for elem in root.iter():
    if get_local_tag(elem) == "Hmi.Screen.ScreenLayer":
        layer = elem
        break

if layer is None:
    print("Error: Hmi.Screen.ScreenLayer not found")
    exit(1)

object_list = find_local(layer, "ObjectList")
if object_list is None:
    print("Error: ObjectList not found")
    exit(1)

print("=== SCREEN ELEMENTS IN scadabai3 ===")
for elem in object_list:
    tag = get_local_tag(elem)
    attrs = find_local(elem, "AttributeList")
    if attrs is None:
        continue
    
    name_el = find_local(attrs, "ObjectName")
    left_el = find_local(attrs, "Left")
    top_el = find_local(attrs, "Top")
    width_el = find_local(attrs, "Width")
    height_el = find_local(attrs, "Height")
    
    name = name_el.text if name_el is not None else "Unknown"
    left = int(left_el.text) if left_el is not None else 0
    top = int(top_el.text) if top_el is not None else 0
    width = int(width_el.text) if width_el is not None else 0
    height = int(height_el.text) if height_el is not None else 0
    
    extra = ""
    if tag == "Hmi.Screen.Button":
        # Check multilingual text
        objs = find_local(elem, "ObjectList")
        if objs is not None:
            ml_text = find_local(objs, "MultilingualText")
            if ml_text is not None:
                ml_objs = find_local(ml_text, "ObjectList")
                if ml_objs is not None:
                    ml_item = find_local(ml_objs, "MultilingualTextItem")
                    if ml_item is not None:
                        m_attrs = find_local(ml_item, "AttributeList")
                        if m_attrs is not None:
                            txt_el = find_local(m_attrs, "Text")
                            if txt_el is not None and txt_el.text:
                                extra = f"Text: '{txt_el.text.strip()}'"
    elif tag == "Hmi.Screen.GraphicView":
        # Check picture name
        pic_el = find_local(attrs, "Picture")
        if pic_el is not None and pic_el.text:
            extra = f"Picture: '{pic_el.text.strip()}'"
    elif tag == "Hmi.Screen.Bar":
        # Check process value tag
        objs = find_local(elem, "ObjectList")
        tag_conn_name = "NONE"
        if objs is not None:
            for prop in objs:
                if get_local_tag(prop) == "Hmi.Screen.Property":
                    p_attrs = find_local(prop, "AttributeList")
                    if p_attrs is not None:
                        p_name = find_local(p_attrs, "Name")
                        if p_name is not None and p_name.text == "ProcessValue":
                            p_objs = find_local(prop, "ObjectList")
                            if p_objs is not None:
                                conn = find_local(p_objs, "Hmi.Dynamic.TagConnectionDynamic")
                                if conn is not None:
                                    links = find_local(conn, "LinkList")
                                    if links is not None:
                                        tag_el = find_local(links, "Tag")
                                        if tag_el is not None:
                                            t_name_el = find_local(tag_el, "Name")
                                            if t_name_el is not None:
                                                tag_conn_name = t_name_el.text
        extra = f"Tag bound: {tag_conn_name}"
        
    print(f"Tag: {tag:22s} | Name: {name:20s} | Left: {left:4d} | Top: {top:4d} | W: {width:3d} | H: {height:3d} | {extra}")
