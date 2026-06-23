# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

plc1_xml = r"D:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\output\PLC_Tags_PLC1.xml"
plc2_xml = r"D:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\output\PLC_Tags_PLC2.xml"
out_txt = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\plc_tags_list.txt"

def parse_tags_xml(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return []
    
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    tags = []
    # Use namespace-independent traversal
    for elem in root.iter():
        tag_local = elem.tag.split('}')[-1]
        if tag_local.endswith("PlcTag"):
            name = ""
            dtype = ""
            address = ""
            comment = ""
            
            # Look inside this specific PlcTag
            for child in elem:
                child_local = child.tag.split('}')[-1]
                if child_local == "AttributeList":
                    name_el = child.find(".//{*}Name")
                    if name_el is not None: name = name_el.text
                    
                    dtype_el = child.find(".//{*}DataTypeName")
                    if dtype_el is not None: dtype = dtype_el.text
                    
                    addr_el = child.find(".//{*}LogicalAddress")
                    if addr_el is not None: address = addr_el.text
                    
                elif child_local == "ObjectList":
                    # Look for Comment
                    for c_el in child:
                        c_local = c_el.tag.split('}')[-1]
                        if c_local == "Comment":
                            # Look for Value
                            val_el = c_el.find(".//{*}Value")
                            if val_el is not None:
                                comment += val_el.text + " "
                                
            tags.append((name, dtype, address, comment.strip()))
    return tags

with open(out_txt, "w", encoding="utf-8") as f:
    f.write("=== PLC 1 TAGS ===\n")
    plc1_tags = parse_tags_xml(plc1_xml)
    for name, dtype, addr, comment in sorted(plc1_tags):
        f.write(f"Name: {name} | Type: {dtype} | Addr: {addr} | Comment: {comment}\n")
        
    f.write("\n=== PLC 2 TAGS ===\n")
    plc2_tags = parse_tags_xml(plc2_xml)
    for name, dtype, addr, comment in sorted(plc2_tags):
        f.write(f"Name: {name} | Type: {dtype} | Addr: {addr} | Comment: {comment}\n")

print(f"Done parsing. PLC1: {len(plc1_tags)} tags, PLC2: {len(plc2_tags)} tags.")
