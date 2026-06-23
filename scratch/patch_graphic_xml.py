# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\exported_bg_graphic.xml"
if not os.path.exists(xml_path):
    print(f"[ERROR] XML not found: {xml_path}")
    exit(1)

ET.register_namespace('', '')
tree = ET.parse(xml_path)
root = tree.getroot()

# Find the Hmi.Globalization.MultiLingualGraphic element
graphic_el = None
for elem in root.iter():
    if elem.tag.endswith("MultiLingualGraphic"):
        graphic_el = elem
        break

if graphic_el is None:
    print("[ERROR] MultiLingualGraphic element not found in XML!")
    exit(1)

# Find ObjectList
objs = graphic_el.find("ObjectList")
if objs is None:
    # If ObjectList doesn't exist, create it
    objs = ET.SubElement(graphic_el, "ObjectList")

# Find the en-US GraphicItem
en_item = None
has_vn = False
max_id = 0

for item in objs:
    if item.tag.endswith("GraphicItem"):
        id_attr = item.get("ID")
        if id_attr:
            try:
                max_id = max(max_id, int(id_attr, 16))
            except ValueError:
                pass
        
        culture_el = item.find("AttributeList/Culture")
        if culture_el is not None:
            if culture_el.text == "en-US":
                en_item = item
            elif culture_el.text == "vi-VN":
                has_vn = True

if has_vn:
    print("[INFO] vi-VN translation already exists in the graphic.")
else:
    if en_item is None:
        print("[ERROR] en-US GraphicItem not found, cannot duplicate!")
        exit(1)
        
    import copy
    vn_item = copy.deepcopy(en_item)
    
    # Set unique ID
    new_id = hex(max_id + 1)[2:].upper()
    vn_item.set("ID", new_id)
    
    # Update culture to vi-VN
    culture_el = vn_item.find("AttributeList/Culture")
    culture_el.text = "vi-VN"
    
    objs.append(vn_item)
    print(f"[SUCCESS] Added vi-VN GraphicItem with ID: {new_id}")

# Save XML
tree.write(xml_path, encoding="utf-8", xml_declaration=True)
print(f"[SUCCESS] Saved updated XML at: {xml_path}")
