# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os

screen_xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen_1_patched.xml"
hmi_tags_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags.xml"

# Parse HMI tags
hmi_tags = set()
tree = ET.parse(hmi_tags_path)
root = tree.getroot()
for tag_el in root.iter():
    if tag_el.tag.endswith("Hmi.Tag.Tag"):
        name = tag_el.find("AttributeList/Name").text
        hmi_tags.add(name.strip())

# Parse Screen_1 bindings
screen_tree = ET.parse(screen_xml_path)
screen_root = screen_tree.getroot()

bound_tags = set()
for elem in screen_root.iter():
    tag_local = elem.tag.split('}')[-1]
    if tag_local in ["Hmi.Screen.IOField", "Hmi.Screen.GraphicIOField"]:
        # Find bound tag
        obj_list = elem.find("ObjectList")
        if obj_list is not None:
            for prop in obj_list.findall("Hmi.Screen.Property"):
                pname_el = prop.find("AttributeList/Name")
                if pname_el is not None and pname_el.text == "ProcessValue":
                    dyn = prop.find("ObjectList/Hmi.Dynamic.TagConnectionDynamic")
                    if dyn is not None:
                        tag_el = dyn.find("LinkList/Tag")
                        if tag_el is not None:
                            tag_name_el = tag_el.find("Name")
                            if tag_name_el is not None and tag_name_el.text:
                                bound_tags.add(tag_name_el.text.strip())

missing = bound_tags - hmi_tags
print(f"Total unique bound tags in Screen_1: {len(bound_tags)}")
if missing:
    print(f"Bound tags in Screen_1 but MISSING in HMI tags XML: {missing}")
else:
    print("All bound tags in Screen_1 exist in the HMI tags XML table.")
