# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os

hmi_tags_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags.xml"

if not os.path.exists(hmi_tags_path):
    print(f"Error: {hmi_tags_path} not found!")
    exit(1)

print("Reading and parsing Screen1_HMI_Tags.xml...")
tree = ET.parse(hmi_tags_path)
root = tree.getroot()

# Register namespaces to preserve format
namespaces = {node[0]: node[1] for _, node in ET.iterparse(hmi_tags_path, events=['start-ns'])}
for prefix, uri in namespaces.items():
    ET.register_namespace(prefix, uri)

ns_prefix = ""
if root.tag.startswith("{"):
    ns_prefix = root.tag.split('}')[0] + "}"

time_tags = [
    "HMI_SP_Time_Khuay_Bon1",
    "HMI_SP_Time_Khuay_Bon3",
    "HMI_SP_Time_Fwd",
    "HMI_SP_Time_Rev",
    "HMI_SP_Time_Sterilize"
]

updated_count = 0
for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    if tag_local == "Tag" or tag_local == "Hmi.Tag.Tag":
        name_el = elem.find(f".//{ns_prefix}Name")
        if name_el is not None and name_el.text in time_tags:
            tag_name = name_el.text
            print(f"Updating Time tag: {tag_name}...")
            
            # Sửa DataType trong LinkList thành Time
            dtype_el = elem.find(f".//{ns_prefix}LinkList/{ns_prefix}DataType/{ns_prefix}Name")
            if dtype_el is not None:
                dtype_el.text = "Time"
                
            # Sửa HmiDataType trong LinkList thành DInt
            hdtype_el = elem.find(f".//{ns_prefix}LinkList/{ns_prefix}HmiDataType/{ns_prefix}Name")
            if hdtype_el is not None:
                hdtype_el.text = "DInt"
                
            # Sửa Length trong AttributeList thành 4
            len_el = elem.find(f".//{ns_prefix}AttributeList/{ns_prefix}Length")
            if len_el is not None:
                len_el.text = "4"
                
            # Sửa Coding trong AttributeList thành Binary
            cod_el = elem.find(f".//{ns_prefix}AttributeList/{ns_prefix}Coding")
            if cod_el is not None:
                cod_el.text = "Binary"
                
            updated_count += 1

print(f"Saving updated XML, total modified: {updated_count}")
tree.write(hmi_tags_path, encoding="utf-8", xml_declaration=True)
print("[PASS] Successfully updated Time tags XML structure!")
