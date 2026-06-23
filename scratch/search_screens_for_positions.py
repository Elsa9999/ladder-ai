# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import glob
import os

screens_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens"
xml_files = glob.glob(os.path.join(screens_dir, "*.xml"))

print(f"Searching {len(xml_files)} screen files for tag bindings...")

target_tags = ["LT3203", "TT3204", "FQ3200", "V3230", "LT3302", "PI3308", "FT3309"]

for xml_path in xml_files:
    file_name = os.path.basename(xml_path)
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Check all screen items
        found = []
        for elem in root.iter():
            tag_local = elem.tag.split('}')[-1]
            # Check ObjectName
            attrs = elem.find("AttributeList")
            obj_name = ""
            if attrs is not None:
                obj_name_el = attrs.find("ObjectName")
                if obj_name_el is not None:
                    obj_name = obj_name_el.text
                    
            # Check if there are tag links
            links = elem.find("LinkList")
            tag_names = []
            if links is not None:
                for tag_el in links.findall(".//Tag"):
                    name_el = tag_el.find("Name")
                    if name_el is not None:
                        tag_names.append(name_el.text)
                        
            objs = elem.find("ObjectList")
            if objs is not None:
                for prop in objs.findall(".//Hmi.Screen.Property") + objs.findall(".//Property"):
                    for tag_conn in prop.findall(".//Hmi.Dynamic.TagConnectionDynamic") + prop.findall(".//TagConnectionDynamic"):
                        t_el = tag_conn.find(".//Tag")
                        if t_el is not None:
                            n_el = t_el.find("Name")
                            if n_el is not None:
                                tag_names.append(n_el.text)
                                
            for tname in tag_names:
                for target in target_tags:
                    if target.lower() in tname.lower():
                        left = attrs.find("Left").text if attrs is not None and attrs.find("Left") is not None else "N/A"
                        top = attrs.find("Top").text if attrs is not None and attrs.find("Top") is not None else "N/A"
                        found.append((obj_name, tag_local, left, top, tname))
                        
        if found:
            print(f"\nScreen: {file_name} has {len(found)} matches:")
            for item_name, type_local, left, top, tname in found[:20]:
                print(f"  - Item: {item_name} ({type_local}) at ({left}, {top}) -> Bound Tag: {tname}")
            if len(found) > 20:
                print(f"  ... and {len(found) - 20} more matches.")
    except Exception as e:
        print(f"Error parsing {file_name}: {e}")
