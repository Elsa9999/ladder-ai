# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os

def get_local_tag(elem):
    return elem.tag.split("}")[-1]

for i in range(3, 8):
    xml_path = f"d:\\AI_Agent_PLC_LADDER_ONLY\\scratch\\scadabai{i}_export.xml"
    if not os.path.exists(xml_path):
        print(f"scadabai{i}: File not found")
        continue
        
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Counts
    io_count = 0
    btn_count = 0
    bar_count = 0
    gv_count = 0
    tf_count = 0
    pictures = set()
    
    for elem in root.iter():
        tag = get_local_tag(elem)
        if tag.endswith("IOField"):
            io_count += 1
        elif tag.endswith("Button"):
            btn_count += 1
        elif tag.endswith("Bar"):
            bar_count += 1
        elif tag.endswith("GraphicView"):
            gv_count += 1
            # Try to find picture name
            pic_el = elem.find(".//Picture/Name")
            if pic_el is not None and pic_el.text:
                pictures.add(pic_el.text.strip())
            else:
                pic_el2 = elem.find("AttributeList/Picture")
                if pic_el2 is not None and pic_el2.text:
                    pictures.add(pic_el2.text.strip())
        elif tag.endswith("TextField"):
            tf_count += 1
            
    print(f"=== scadabai{i} ===")
    print(f"  IO Fields    : {io_count}")
    print(f"  Buttons      : {btn_count}")
    print(f"  Bars         : {bar_count}")
    print(f"  GraphicViews : {gv_count}")
    print(f"  TextFields   : {tf_count}")
    print(f"  Pictures     : {sorted(list(pictures))}")
