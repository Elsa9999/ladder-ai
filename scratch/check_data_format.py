# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os

screens = ["bon_tron_1", "bon_tron_2", "bon_tron_3", "bon_tron_4"]

for scr in screens:
    xml_path = f"D:\\AI_Agent_PLC_LADDER_ONLY\\scratch\\{scr}_export.xml"
    if not os.path.exists(xml_path):
        print(f"{scr} export XML not found!")
        continue
        
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    ns_prefix = ""
    if root.tag.startswith("{"):
        ns_prefix = root.tag.split('}')[0] + "}"
        
    print(f"\n--- Screen: {scr} ---")
    for elem in root.iter():
        tag_local = elem.tag.split('}')[-1]
        if tag_local == "IOField" or tag_local == "Hmi.Screen.IOField":
            attrs = elem.find("AttributeList")
            if attrs is not None:
                obj_name = attrs.find("ObjectName").text if attrs.find("ObjectName") is not None else ""
                if obj_name in ["I/O field_4", "I/O field_6"]:
                    df = attrs.find("DataFormat").text if attrs.find("DataFormat") is not None else "N/A"
                    fp = attrs.find("FormatPattern").text if attrs.find("FormatPattern") is not None else "N/A"
                    fl = attrs.find("FieldLength").text if attrs.find("FieldLength") is not None else "N/A"
                    print(f"  ObjectName: {obj_name} | DataFormat: {df} | FormatPattern: {fp} | FieldLength: {fl}")
