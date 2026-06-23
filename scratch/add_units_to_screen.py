# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens\Hmi.Screen.Screen_2.xml"

# Parse XML
ET.register_namespace('', '') # default namespace
tree = ET.parse(xml_path)
root = tree.getroot()

# Find Layer containing all ScreenItems
layer = root.find(".//Hmi.Screen.ScreenLayer")
if layer is None:
    print("[ERROR] Layer not found!")
    exit(1)

object_list = layer.find("ObjectList")
if object_list is None:
    print("[ERROR] ObjectList of Layer not found!")
    exit(1)

# Units mapping for each IO field
units_map = {
    "I/O field_8": "L/h",   # 1400_FT115_PV
    "I/O field_9": "L/h",   # 1400_1_02_PV
    "I/O field_7": "L/h",   # 1400_FT101_PV
    "I/O field_4": "bar",   # 1406_TX35_PV
    "I/O field_2": "Hz",    # 1400_FS51_PV
    "I/O field_11": "°C",   # 1400_TT64_PV
    "I/O field_1": "°C",    # 1400_TT32_PV
    "I/O field_3": "%",     # 1400_LGFE01_PV
    "I/O field_10": "%"     # 1400_FY301_PV
}

# Unique ID counter starting at 0x1000
id_counter = 4096
def get_next_id():
    global id_counter
    res = hex(id_counter)[2:].upper()
    id_counter += 1
    return res

# First, remove any previously generated unit text fields to avoid duplicates if re-run
to_remove = []
for item in object_list:
    if item.tag == "Hmi.Screen.TextField":
        attr_list = item.find("AttributeList")
        if attr_list is not None:
            obj_name_el = attr_list.find("ObjectName")
            if obj_name_el is not None and obj_name_el.text.startswith("Text_field_Unit_"):
                to_remove.append(item)

for item in to_remove:
    object_list.remove(item)
    print(f"Removed old unit field: {item.find('AttributeList/ObjectName').text}")

# Locate each IO field and create a TextField next to it
for item in list(object_list):
    if item.tag == "Hmi.Screen.IOField":
        attr_list = item.find("AttributeList")
        if attr_list is not None:
            obj_name_el = attr_list.find("ObjectName")
            if obj_name_el is not None:
                obj_name = obj_name_el.text
                if obj_name in units_map:
                    unit_text = units_map[obj_name]
                    
                    # Read coordinates
                    left = int(attr_list.find("Left").text)
                    top = int(attr_list.find("Top").text)
                    width = int(attr_list.find("Width").text)
                    height = int(attr_list.find("Height").text)
                    
                    # Calculate TextField position (8 pixels to the right)
                    tf_left = left + width + 8
                    tf_top = top
                    tf_width = 40
                    tf_height = height
                    tf_obj_name = f"Text_field_Unit_{obj_name.replace(' ', '_').replace('/', '_')}"
                    
                    print(f"Creating TextField for unit '{unit_text}' next to {obj_name} at ({tf_left}, {tf_top})")
                    
                    # Create Hmi.Screen.TextField
                    tf = ET.SubElement(object_list, "Hmi.Screen.TextField", {
                        "ID": get_next_id(),
                        "CompositionName": "ScreenItems"
                    })
                    
                    tf_attrs = ET.SubElement(tf, "AttributeList")
                    ET.SubElement(tf_attrs, "BackColor").text = "255, 255, 255"
                    ET.SubElement(tf_attrs, "BackFillStyle").text = "Transparent"
                    ET.SubElement(tf_attrs, "BorderWidth").text = "0"
                    ET.SubElement(tf_attrs, "ForeColor").text = "0, 0, 0"
                    ET.SubElement(tf_attrs, "Height").text = str(tf_height)
                    ET.SubElement(tf_attrs, "HorizontalAlignment").text = "Left"
                    ET.SubElement(tf_attrs, "Left").text = str(tf_left)
                    ET.SubElement(tf_attrs, "ObjectName").text = tf_obj_name
                    ET.SubElement(tf_attrs, "TextOrientation").text = "Horizontal"
                    ET.SubElement(tf_attrs, "Top").text = str(tf_top)
                    ET.SubElement(tf_attrs, "VerticalAlignment").text = "Middle"
                    ET.SubElement(tf_attrs, "Width").text = str(tf_width)
                    
                    tf_objs = ET.SubElement(tf, "ObjectList")
                    
                    # Font setup
                    font = ET.SubElement(tf_objs, "Hmi.Globalization.MultiLingualFont", {
                        "ID": get_next_id(),
                        "CompositionName": "Font"
                    })
                    font_objs = ET.SubElement(font, "ObjectList")
                    font_item = ET.SubElement(font_objs, "Hmi.Globalization.FontItem", {
                        "ID": get_next_id(),
                        "CompositionName": "Items"
                    })
                    fi_attrs = ET.SubElement(font_item, "AttributeList")
                    ET.SubElement(fi_attrs, "Culture").text = "en-US"
                    ET.SubElement(fi_attrs, "FontFamily").text = "Arial"
                    ET.SubElement(fi_attrs, "FontSize").text = "13"
                    ET.SubElement(fi_attrs, "FontStyle").text = "Bold"
                    
                    # Text content setup
                    txt = ET.SubElement(tf_objs, "MultilingualText", {
                        "ID": get_next_id(),
                        "CompositionName": "Text"
                    })
                    txt_objs = ET.SubElement(txt, "ObjectList")
                    txt_item = ET.SubElement(txt_objs, "MultilingualTextItem", {
                        "ID": get_next_id(),
                        "CompositionName": "Items"
                    })
                    ti_attrs = ET.SubElement(txt_item, "AttributeList")
                    ET.SubElement(ti_attrs, "Culture").text = "en-US"
                    ET.SubElement(ti_attrs, "Text").text = f"<body><p>{unit_text}</p></body>"

# Save tree back
tree.write(xml_path, encoding="utf-8", xml_declaration=True)
print("[SUCCESS] Screen XML updated with units!")
