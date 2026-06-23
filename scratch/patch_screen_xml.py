# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens\Hmi.Screen.Screen_1.xml"

# Parse XML
ET.register_namespace('', '') # default namespace
tree = ET.parse(xml_path)
root = tree.getroot()

# Let's find Hmi.Screen.ScreenLayer or container of ScreenItems
layer = root.find(".//Hmi.Screen.ScreenLayer")
if layer is None:
    print("[ERROR] Layer not found!")
    exit(1)

# Find ObjectList inside Layer which contains all ScreenItems
object_list = layer.find("ObjectList")
if object_list is None:
    print("[ERROR] ObjectList of Layer not found!")
    exit(1)

# Maps for binding
io_field_map = {
    "I/O field_8": "1400_FT115_PV",
    "I/O field_9": "1400_1_02_PV",
    "I/O field_7": "1400_FT101_PV",
    "I/O field_4": "1406_TX35_PV",
    "I/O field_2": "1400_FS51_PV",
    "I/O field_11": "1400_TT64_PV",
    "I/O field_1": "1400_TT32_PV",
    "I/O field_3": "1400_LGFE01_PV",
    "I/O field_10": "1400_FY301_PV"
}

circle_map = {
    "Circle_1": "1500S_Trang_Thai",
    "Circle_2": "1404T_Trang_Thai",
    "Circle_3": "CR_2013_FO_104_Trang_Thai",
    "Circle_4": "BFOC_SS_20_06_Trang_Thai",
    "Circle_6": "1400_PT91_Chay",
    "Circle_7": "PC03010T01_Trang_Thai",
    "Circle_8": "1401_Trang_Thai"
}

# Delete duplicate Circle_5
circle_5 = None
for item in object_list:
    if item.tag == "Hmi.Screen.Circle":
        attr_list = item.find("AttributeList")
        if attr_list is not None:
            obj_name = attr_list.find("ObjectName")
            if obj_name is not None and obj_name.text == "Circle_5":
                circle_5 = item
                break

if circle_5 is not None:
    object_list.remove(circle_5)
    print("[SUCCESS] Removed duplicate Circle_5")

# Generate unique IDs starting from 0x100
id_counter = 256

def get_next_id():
    global id_counter
    res = hex(id_counter)[2:].upper()
    id_counter += 1
    return res

# Bind IO fields
for item in object_list:
    if item.tag == "Hmi.Screen.IOField":
        attr_list = item.find("AttributeList")
        if attr_list is not None:
            obj_name_el = attr_list.find("ObjectName")
            if obj_name_el is not None:
                obj_name = obj_name_el.text
                if obj_name in io_field_map:
                    tag_name = io_field_map[obj_name]
                    print(f"Binding {obj_name} to tag {tag_name}")
                    
                    # Find or create ObjectList inside Hmi.Screen.IOField
                    item_obj_list = item.find("ObjectList")
                    if item_obj_list is None:
                        item_obj_list = ET.SubElement(item, "ObjectList")
                        
                    # Create Property element
                    prop = ET.SubElement(item_obj_list, "Hmi.Screen.Property", {
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

# Bind Circle appearance animations
for item in object_list:
    if item.tag == "Hmi.Screen.Circle":
        attr_list = item.find("AttributeList")
        if attr_list is not None:
            obj_name_el = attr_list.find("ObjectName")
            if obj_name_el is not None:
                obj_name = obj_name_el.text
                if obj_name in circle_map:
                    tag_name = circle_map[obj_name]
                    print(f"Adding animation to {obj_name} using tag {tag_name}")
                    
                    # Find or create ObjectList inside Hmi.Screen.Circle
                    item_obj_list = item.find("ObjectList")
                    if item_obj_list is None:
                        item_obj_list = ET.SubElement(item, "ObjectList")
                        
                    # Create Hmi.Dynamic.RangeAppearanceAnimation element
                    anim = ET.SubElement(item_obj_list, "Hmi.Dynamic.RangeAppearanceAnimation", {
                        "ID": get_next_id(),
                        "CompositionName": "Animations"
                    })
                    anim_attr = ET.SubElement(anim, "AttributeList")
                    anim_name = ET.SubElement(anim_attr, "Name")
                    anim_name.text = "RangeAppearanceAnimation"
                    
                    anim_obj = ET.SubElement(anim, "ObjectList")
                    trigger = ET.SubElement(anim_obj, "Hmi.Dynamic.TagElementTrigger", {
                        "ID": get_next_id(),
                        "CompositionName": "RangeTag"
                    })
                    trigger_links = ET.SubElement(trigger, "LinkList")
                    tag_el = ET.SubElement(trigger_links, "Tag", {
                        "TargetID": "@OpenLink"
                    })
                    tag_name_el = ET.SubElement(tag_el, "Name")
                    tag_name_el.text = tag_name
                    
                    # Range for 0 (White/Default)
                    range0 = ET.SubElement(anim_obj, "Hmi.Dynamic.Range", {
                        "ID": get_next_id(),
                        "CompositionName": "RangeValues"
                    })
                    r0_attr = ET.SubElement(range0, "AttributeList")
                    ET.SubElement(r0_attr, "BackColor").text = "255, 255, 255"
                    ET.SubElement(r0_attr, "FlashingType").text = "No"
                    ET.SubElement(r0_attr, "ForeColor").text = "0, 0, 0"
                    ET.SubElement(r0_attr, "LowerLimit").text = "0"
                    ET.SubElement(r0_attr, "UpperLimit").text = "0"
                    
                    # Range for 1 (Green)
                    range1 = ET.SubElement(anim_obj, "Hmi.Dynamic.Range", {
                        "ID": get_next_id(),
                        "CompositionName": "RangeValues"
                    })
                    r1_attr = ET.SubElement(range1, "AttributeList")
                    ET.SubElement(r1_attr, "BackColor").text = "0, 255, 0"
                    ET.SubElement(r1_attr, "FlashingType").text = "No"
                    ET.SubElement(r1_attr, "ForeColor").text = "0, 0, 0"
                    ET.SubElement(r1_attr, "LowerLimit").text = "1"
                    ET.SubElement(r1_attr, "UpperLimit").text = "1"

# Save tree
tree.write(xml_path, encoding="utf-8", xml_declaration=True)
print("[SUCCESS] Screen XML patched and saved!")
