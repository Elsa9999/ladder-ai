# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens\Hmi.Screen.Screen_2.xml"

if not os.path.exists(xml_path):
    print(f"[ERROR] XML file not found at {xml_path}")
    exit(1)

# Parse XML
ET.register_namespace('', '') # default namespace
tree = ET.parse(xml_path)
root = tree.getroot()

# Find Layer containing all ScreenItems
layer = root.find(".//Hmi.Screen.ScreenLayer")
if layer is None:
    print("[ERROR] Layer not found!")
    exit(1)

object_list = layer.find("ObjectList")
if object_list is None:
    print("[ERROR] ObjectList of Layer not found!")
    exit(1)

# Active IO fields and their format patterns
# Flow and Percentage need 3 integer digits (999.9) to prevent ### at >= 100.0
# Temp, Pressure, Frequency need 2 integer digits (99.9)
io_field_formats = {
    "I/O field_8": "999.9",   # 1400_FT115_PV (Flow)
    "I/O field_9": "999.9",   # 1400_1_02_PV (Flow)
    "I/O field_7": "999.9",   # 1400_FT101_PV (Flow)
    "I/O field_4": "99.9",    # 1406_TX35_PV (Pressure)
    "I/O field_2": "99.9",    # 1400_FS51_PV (Frequency)
    "I/O field_11": "99.9",   # 1400_TT64_PV (Temp)
    "I/O field_1": "99.9",    # 1400_TT32_PV (Temp)
    "I/O field_3": "999.9",   # 1400_LGFE01_PV (Percentage)
    "I/O field_10": "999.9"   # 1400_FY301_PV (Percentage)
}

modified_count = 0

for item in object_list:
    if item.tag == "Hmi.Screen.IOField":
        attr_list = item.find("AttributeList")
        if attr_list is not None:
            obj_name_el = attr_list.find("ObjectName")
            if obj_name_el is not None:
                obj_name = obj_name_el.text
                if obj_name in io_field_formats:
                    target_pattern = io_field_formats[obj_name]
                    print(f"Modifying {obj_name}:")
                    
                    # 1. FormatPattern
                    fp_el = attr_list.find("FormatPattern")
                    if fp_el is not None:
                        old_val = fp_el.text
                        fp_el.text = target_pattern
                        print(f"  FormatPattern: {old_val} -> {target_pattern}")
                    else:
                        fp_el = ET.SubElement(attr_list, "FormatPattern")
                        fp_el.text = target_pattern
                        print(f"  FormatPattern: [NEW] -> {target_pattern}")
                        
                    # 2. HorizontalAlignment
                    ha_el = attr_list.find("HorizontalAlignment")
                    if ha_el is not None:
                        old_val = ha_el.text
                        ha_el.text = "Center"
                        print(f"  HorizontalAlignment: {old_val} -> Center")
                    else:
                        ha_el = ET.SubElement(attr_list, "HorizontalAlignment")
                        ha_el.text = "Center"
                        print(f"  HorizontalAlignment: [NEW] -> Center")
                        
                    # 3. VerticalAlignment
                    va_el = attr_list.find("VerticalAlignment")
                    if va_el is not None:
                        old_val = va_el.text
                        va_el.text = "Middle"
                        print(f"  VerticalAlignment: {old_val} -> Middle")
                    else:
                        va_el = ET.SubElement(attr_list, "VerticalAlignment")
                        va_el.text = "Middle"
                        print(f"  VerticalAlignment: [NEW] -> Middle")
                        
                    modified_count += 1

# Save tree back
if modified_count > 0:
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    print(f"[SUCCESS] Patched format and alignment for {modified_count} IO fields in Screen XML!")
else:
    print("[WARN] No matching IO fields modified.")
