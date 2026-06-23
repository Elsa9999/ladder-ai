# -*- coding: utf-8 -*-
import csv
import xml.etree.ElementTree as ET
import os
import sys

csv_numeric_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\screen1_mapping_dry_run.csv"
csv_graphic_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\graphic_mapping_dry_run.csv"
screen_xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen_1_readback.xml"
patched_xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen_1_patched.xml"

if not os.path.exists(csv_numeric_path):
    print(f"Error: Numeric CSV mapping not found at {csv_numeric_path}")
    sys.exit(1)

if not os.path.exists(csv_graphic_path):
    print(f"Error: Graphic CSV mapping not found at {csv_graphic_path}")
    sys.exit(1)

if not os.path.exists(screen_xml_path):
    print(f"Error: Screen XML not found at {screen_xml_path}")
    sys.exit(1)

# Read Numeric CSV mapping
numeric_mapping = {}
with open(csv_numeric_path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if not row or row[0].startswith('#'):
            continue
        obj_name = row[1].strip()
        if obj_name == "ObjectName" or obj_name == "(missing)" or not obj_name:
            continue
        numeric_mapping[obj_name] = {
            "TagName": row[8].strip(),
            "FormatPattern": row[6].strip(),
        }

# Read Graphic CSV mapping
graphic_mapping = {}
with open(csv_graphic_path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if not row or row[0].startswith('#'):
            continue
        obj_name = row[0].strip()
        if obj_name == "ObjectName" or obj_name == "(missing)" or not obj_name:
            continue
        graphic_mapping[obj_name] = {
            "TagName": row[6].strip()
        }

print(f"Loaded {len(numeric_mapping)} numeric mapping entries.")
print(f"Loaded {len(graphic_mapping)} graphic mapping entries.")

# Parse XML
ET.register_namespace('', '') # default namespace
tree = ET.parse(screen_xml_path)
root = tree.getroot()

# Determine max ID to prevent ID conflict
existing_ids = []
for elem in root.iter():
    id_val = elem.get("ID")
    if id_val is not None:
        try:
            val = int(id_val, 16)
            existing_ids.append(val)
        except ValueError:
            pass

id_counter = max(existing_ids) + 1 if existing_ids else 1000

def get_next_id():
    global id_counter
    res = hex(id_counter)[2:].upper()
    id_counter += 1
    return res

def set_or_update_attr(attr_list, name, value):
    el = attr_list.find(name)
    if el is None:
        el = ET.SubElement(attr_list, name)
    el.text = str(value)

def bind_process_value(elem, tag_name):
    # Add or update ProcessValue binding in ObjectList
    obj_list = elem.find("ObjectList")
    if obj_list is None:
        obj_list = ET.SubElement(elem, "ObjectList")
    
    # Remove any existing ProcessValue property bindings
    props_to_remove = []
    for prop in obj_list.findall("Hmi.Screen.Property"):
        pname_el = prop.find("AttributeList/Name")
        if pname_el is not None and pname_el.text == "ProcessValue":
            props_to_remove.append(prop)
    for prop in props_to_remove:
        obj_list.remove(prop)
        
    # Create new Property element for ProcessValue
    prop = ET.SubElement(obj_list, "Hmi.Screen.Property", {
        "ID": get_next_id(),
        "CompositionName": "Properties"
    })
    prop_attr = ET.SubElement(prop, "AttributeList")
    prop_name = ET.SubElement(prop_attr, "Name")
    prop_name.text = "ProcessValue"
    
    prop_obj = ET.SubElement(prop, "ObjectList")
    dyn = ET.SubElement(prop_obj, "Hmi.Dynamic.TagConnectionDynamic", {
        "ID": get_next_id(),
        "CompositionName": "Dynamic"
    })
    dyn_attr = ET.SubElement(dyn, "AttributeList")
    dyn_indir = ET.SubElement(dyn_attr, "Indirect")
    dyn_indir.text = "false"
    
    dyn_links = ET.SubElement(dyn, "LinkList")
    tag_el = ET.SubElement(dyn_links, "Tag", {
        "TargetID": "@OpenLink"
    })
    tag_name_el = ET.SubElement(tag_el, "Name")
    tag_name_el.text = tag_name

patched_iofields = 0
patched_graphicfields = 0

# Scan elements
for elem in root.iter():
    local_tag = elem.tag.split('}')[-1]
    
    # 1. IOFields
    if local_tag == "Hmi.Screen.IOField":
        attrs = elem.find("AttributeList")
        if attrs is not None:
            obj_name_elem = attrs.find("ObjectName")
            if obj_name_elem is not None and obj_name_elem.text:
                obj_name = obj_name_elem.text.strip()
                if obj_name in numeric_mapping:
                    map_info = numeric_mapping[obj_name]
                    
                    # Update alignment and FormatPattern
                    set_or_update_attr(attrs, "HorizontalAlignment", "Center")
                    set_or_update_attr(attrs, "VerticalAlignment", "Middle")
                    set_or_update_attr(attrs, "FormatPattern", map_info["FormatPattern"])
                    
                    # Bind process value
                    bind_process_value(elem, map_info["TagName"])
                    patched_iofields += 1
                    
    # 2. GraphicIOFields
    elif local_tag == "Hmi.Screen.GraphicIOField":
        attrs = elem.find("AttributeList")
        if attrs is not None:
            obj_name_elem = attrs.find("ObjectName")
            if obj_name_elem is not None and obj_name_elem.text:
                obj_name = obj_name_elem.text.strip()
                
                # Adjust Top coordinate of Graphic I/O field_27 to prevent screen overflow
                if obj_name == "Graphic I/O field_27":
                    set_or_update_attr(attrs, "Top", 822)
                    print("Adjusted Graphic I/O field_27 Top to 822")
                    
                if obj_name in graphic_mapping:
                    map_info = graphic_mapping[obj_name]
                    
                    # Update Mode to Output
                    set_or_update_attr(attrs, "Mode", "Output")
                    
                    # Bind process value
                    bind_process_value(elem, map_info["TagName"])
                    patched_graphicfields += 1

    # 3. GraphicViews (to adjust coordinates for overflow)
    elif local_tag == "Hmi.Screen.GraphicView":
        attrs = elem.find("AttributeList")
        if attrs is not None:
            obj_name_elem = attrs.find("ObjectName")
            if obj_name_elem is not None and obj_name_elem.text:
                obj_name = obj_name_elem.text.strip()
                if obj_name == "Graphic view_82":
                    set_or_update_attr(attrs, "Top", 853)
                    print("Adjusted Graphic view_82 Top to 853")

print(f"Patched IOFields: {patched_iofields} / 24")
print(f"Patched GraphicIOFields: {patched_graphicfields} / 41")

if patched_iofields != 24:
    print(f"Error: Expected 24 patched IOFields, but got {patched_iofields}.")
    sys.exit(1)

if patched_graphicfields != 41:
    print(f"Error: Expected 41 patched GraphicIOFields, but got {patched_graphicfields}.")
    sys.exit(1)

# Save patched XML
tree.write(patched_xml_path, encoding="utf-8", xml_declaration=True)
print(f"Successfully saved patched screen to {patched_xml_path}.")
sys.exit(0)
