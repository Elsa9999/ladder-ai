# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

input_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Screen_2.xml"
output_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Screen_2_scaled.xml"

if not os.path.exists(input_path):
    print(f"[ERROR] Input XML not found: {input_path}")
    exit(1)

ET.register_namespace('', '')
tree = ET.parse(input_path)
root = tree.getroot()

# Scaling factors
X_SCALE = 1024.0 / 1920.0  # 0.533333
Y_SCALE = 768.0 / 1080.0   # 0.711111

print(f"Scaling XML from 1920x1080 to 1024x768...")
print(f"  X-scale: {X_SCALE:.6f}")
print(f"  Y-scale: {Y_SCALE:.6f}")

# 1. Update Screen width and height
screen_el = None
for elem in root.iter():
    if elem.tag.endswith("Screen"):
        screen_el = elem
        break

if screen_el is not None:
    width_el = screen_el.find("AttributeList/Width")
    height_el = screen_el.find("AttributeList/Height")
    if width_el is not None:
        width_el.text = "1024"
    if height_el is not None:
        height_el.text = "768"
    print("  Updated Screen dimensions to 1024x768.")

# 2. Iterate through all screen items in layers and scale coordinates
scaled_items = 0
for elem in root.iter():
    # Check if this element is a screen item (usually has ObjectName in AttributeList)
    obj_name_el = elem.find("AttributeList/ObjectName")
    if obj_name_el is not None:
        # Scale Left and Top
        left_el = elem.find("AttributeList/Left")
        top_el = elem.find("AttributeList/Top")
        width_el = elem.find("AttributeList/Width")
        height_el = elem.find("AttributeList/Height")
        
        item_name = obj_name_el.text
        
        if left_el is not None and top_el is not None:
            left_val = float(left_el.text)
            top_val = float(top_el.text)
            
            # If it's the background GraphicView, set size exactly to 1024x768
            if item_name == "Graphic view_1" and elem.tag.endswith("GraphicView"):
                left_el.text = "0"
                top_el.text = "0"
                if width_el is not None:
                    width_el.text = "1032"  # 1024 + 8 margin
                if height_el is not None:
                    height_el.text = "770"  # 768 + 2 margin
                # Also link it to the correct project graphic 9e382997-af09-41cf-ab1c-3299fad62071
                pic_name_el = elem.find("LinkList/Picture/Name")
                if pic_name_el is not None:
                    pic_name_el.text = "9e382997-af09-41cf-ab1c-3299fad62071"
                print(f"  Scaled background graphic view to 1032x770 and linked to 9e382997-af09-41cf-ab1c-3299fad62071")
            else:
                # Normal screen item - scale Left and Top
                new_left = int(round(left_val * X_SCALE))
                new_top = int(round(top_val * Y_SCALE))
                
                left_el.text = str(new_left)
                top_el.text = str(new_top)
                
                # Scale width/height of certain custom containers if needed (optional)
                # But for standard buttons and IO fields, we keep sizes as is
                scaled_items += 1

print(f"  Successfully scaled coordinates of {scaled_items} screen elements.")

# Save scaled XML
tree.write(output_path, encoding="utf-8", xml_declaration=True)
print(f"[SUCCESS] Saved scaled HMI screen XML at: {output_path}")
