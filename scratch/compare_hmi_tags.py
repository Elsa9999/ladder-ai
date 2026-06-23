# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os

readback_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags_readback.xml"
new_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags.xml"

def get_tag_names(path):
    names = set()
    if not os.path.exists(path):
        return names
    tree = ET.parse(path)
    root = tree.getroot()
    for tag_el in root.iter():
        if tag_el.tag.endswith("Hmi.Tag.Tag"):
            name_el = tag_el.find("AttributeList/Name")
            if name_el is not None and name_el.text:
                names.add(name_el.text.strip())
    return names

old_tags = get_tag_names(readback_path)
new_tags = get_tag_names(new_path)

print(f"Old tags count: {len(old_tags)}")
print(f"New tags count: {len(new_tags)}")

missing_in_new = old_tags - new_tags
if missing_in_new:
    print(f"Tags in old HMI tag table but MISSING in new: {missing_in_new}")
else:
    print("No old tags are missing in the new tag table.")

extra_in_new = new_tags - old_tags
print(f"New tags added: {len(extra_in_new)}")
