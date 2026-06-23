# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens\Hmi.Screen.Screen_2.xml"
if not os.path.exists(xml_path):
    print(f"[ERROR] XML not found: {xml_path}")
    exit(1)

ET.register_namespace('', '')
tree = ET.parse(xml_path)
root = tree.getroot()

# Determine max ID to generate new unique IDs
max_id = 0
for elem in root.iter():
    id_attr = elem.get("ID")
    if id_attr:
        try:
            val = int(id_attr, 16)
            if val > max_id:
                max_id = val
        except ValueError:
            pass

id_counter = max_id + 2000
def get_next_id():
    global id_counter
    res = hex(id_counter)[2:].upper()
    id_counter += 1
    return res

# We will collect parents and items to duplicate to avoid modifying the tree while iterating
items_to_duplicate = []

for parent in root.iter():
    objs = parent.find("ObjectList")
    if objs is not None:
        for item in list(objs):
            culture_el = item.find("AttributeList/Culture")
            if culture_el is not None and culture_el.text == "en-US":
                items_to_duplicate.append((objs, item))

print(f"Found {len(items_to_duplicate)} items to translate from en-US to vi-VN.")

# Duplicate each item
duplicated_count = 0
for objs, item in items_to_duplicate:
    # Check if a vi-VN translation already exists in objs
    has_vn = False
    for child in objs:
        child_culture = child.find("AttributeList/Culture")
        if child_culture is not None and child_culture.text == "vi-VN":
            has_vn = True
            break
            
    if not has_vn:
        # Clone item
        import copy
        clone = copy.deepcopy(item)
        clone.set("ID", get_next_id())
        
        # Update Culture to vi-VN
        clone_culture = clone.find("AttributeList/Culture")
        clone_culture.text = "vi-VN"
        
        # If it's a FontItem or MultilingualTextItem, update sub-object IDs if any
        for sub_child in clone.iter():
            if sub_child != clone and sub_child.get("ID"):
                sub_child.set("ID", get_next_id())
                
        objs.append(clone)
        duplicated_count += 1

print(f"Duplicated {duplicated_count} items to vi-VN.")

# Save XML
tree.write(xml_path, encoding="utf-8", xml_declaration=True)
print(f"[SUCCESS] Updated Screen_2 XML with Vietnamese translations at: {xml_path}")
