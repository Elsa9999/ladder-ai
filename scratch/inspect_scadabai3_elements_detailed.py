# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

xml_path = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\scadabai3_export.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

def get_local_tag(elem):
    return elem.tag.split("}")[-1]

def find_local(elem, name):
    for child in elem:
        if get_local_tag(child) == name:
            return child
    return None

layer = None
for elem in root.iter():
    if get_local_tag(elem) == "Hmi.Screen.ScreenLayer":
        layer = elem
        break

object_list = find_local(layer, "ObjectList")

print("--- BUTTONS ---")
for elem in object_list:
    tag = get_local_tag(elem)
    if tag == "Hmi.Screen.Button":
        attrs = find_local(elem, "AttributeList")
        name = find_local(attrs, "ObjectName").text if find_local(attrs, "ObjectName") is not None else "Unknown"
        left = int(find_local(attrs, "Left").text) if find_local(attrs, "Left") is not None else 0
        top = int(find_local(attrs, "Top").text) if find_local(attrs, "Top") is not None else 0
        w = int(find_local(attrs, "Width").text) if find_local(attrs, "Width") is not None else 0
        h = int(find_local(attrs, "Height").text) if find_local(attrs, "Height") is not None else 0
        
        # Get Text
        txt = ""
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
                                txt = txt_el.text.strip()
        
        print(f"Name: {name:25s} | Pos: ({left:4d}, {top:4d}) | Size: {w:3d}x{h:3d} | Text: {txt}")

print("\n--- BARS ---")
for elem in object_list:
    tag = get_local_tag(elem)
    if tag == "Hmi.Screen.Bar":
        attrs = find_local(elem, "AttributeList")
        name = find_local(attrs, "ObjectName").text if find_local(attrs, "ObjectName") is not None else "Unknown"
        left = int(find_local(attrs, "Left").text) if find_local(attrs, "Left") is not None else 0
        top = int(find_local(attrs, "Top").text) if find_local(attrs, "Top") is not None else 0
        w = int(find_local(attrs, "Width").text) if find_local(attrs, "Width") is not None else 0
        h = int(find_local(attrs, "Height").text) if find_local(attrs, "Height") is not None else 0
        print(f"Name: {name:25s} | Pos: ({left:4d}, {top:4d}) | Size: {w:3d}x{h:3d}")

print("\n--- TEXT FIELDS ---")
for elem in object_list:
    tag = get_local_tag(elem)
    if tag == "Hmi.Screen.TextField":
        attrs = find_local(elem, "AttributeList")
        name = find_local(attrs, "ObjectName").text if find_local(attrs, "ObjectName") is not None else "Unknown"
        left = int(find_local(attrs, "Left").text) if find_local(attrs, "Left") is not None else 0
        top = int(find_local(attrs, "Top").text) if find_local(attrs, "Top") is not None else 0
        w = int(find_local(attrs, "Width").text) if find_local(attrs, "Width") is not None else 0
        h = int(find_local(attrs, "Height").text) if find_local(attrs, "Height") is not None else 0
        
        # Get Text
        txt = ""
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
                                txt = txt_el.text.strip()
        print(f"Name: {name:25s} | Pos: ({left:4d}, {top:4d}) | Size: {w:3d}x{h:3d} | Text: {txt}")
