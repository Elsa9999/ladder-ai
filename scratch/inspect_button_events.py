# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\active_screen_2_export.xml"

tree = ET.parse(xml_path)
root = tree.getroot()

for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    if tag_local == "Hmi.Screen.Button":
        attrs = elem.find("AttributeList")
        if attrs is not None:
            name_el = attrs.find("ObjectName")
            if name_el is not None and name_el.text == "Button_10":
                print("--- BUTTON_10 XML ---")
                ET.indent(elem)
                # Find all children elements recursively
                for child in elem.iter():
                    child_tag = child.tag.split('}')[-1]
                    print(f"Child tag: {child_tag}")
                    if child.attrib:
                        print(f"  Attribs: {child.attrib}")
                    name_attr = child.find("AttributeList/Name")
                    if name_attr is not None:
                        print(f"  Name attr: {name_attr.text}")
                    # Print Text value if present
                    if child.text and child.text.strip():
                        print(f"  Text: {child.text.strip()[:100]}")
                break
