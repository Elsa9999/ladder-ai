# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Login_out.xml"
output_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens\Hmi.Screen.Login_out.xml"

# Ensure output directory exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Parse XML
ET.register_namespace('', '') # default namespace
tree = ET.parse(xml_path)
root = tree.getroot()

# Find Screen layer containing ScreenItems
layer = root.find(".//Hmi.Screen.ScreenLayer")
if layer is None:
    print("[ERROR] Layer not found!")
    exit(1)

object_list = layer.find("ObjectList")
if object_list is None:
    print("[ERROR] ObjectList of Layer not found!")
    exit(1)

# Button config map
button_configs = {
    "Btn_Login": {"top": 350, "width": 650, "height": 85, "left": 635},
    "Btn_Enter_System": {"top": 460, "width": 650, "height": 85, "left": 635},
    "Btn_Logout": {"top": 570, "width": 650, "height": 85, "left": 635},
    "Btn_Exit": {"top": 680, "width": 650, "height": 85, "left": 635}
}

# Iterate over items to find and update buttons
for item in object_list:
    if item.tag == "Hmi.Screen.Button":
        attr_list = item.find("AttributeList")
        if attr_list is not None:
            obj_name_el = attr_list.find("ObjectName")
            if obj_name_el is not None and obj_name_el.text in button_configs:
                cfg = button_configs[obj_name_el.text]
                print(f"Resizing and repositioning button: {obj_name_el.text}")
                
                # Update attributes
                for attr in attr_list:
                    if attr.tag == "Width":
                        attr.text = str(cfg["width"])
                    elif attr.tag == "Height":
                        attr.text = str(cfg["height"])
                    elif attr.tag == "Left":
                        attr.text = str(cfg["left"])
                    elif attr.tag == "Top":
                        attr.text = str(cfg["top"])
                
                # Remove Event handler for Btn_Exit to let the user map StopRuntime safely in TIA Portal UI
                if obj_name_el.text == "Btn_Exit":
                    btn_objs = item.find("ObjectList")
                    if btn_objs is not None:
                        evt_el = btn_objs.find("Hmi.Event.Event")
                        if evt_el is not None:
                            btn_objs.remove(evt_el)
                            print("  Removed faulty StopRuntime event handler from Btn_Exit to fix compile error.")
                
                # Update font size in ObjectList/Font
                font_item = item.find(".//Hmi.Globalization.FontItem")
                if font_item is not None:
                    font_attrs = font_item.find("AttributeList")
                    if font_attrs is not None:
                        font_size_el = font_attrs.find("FontSize")
                        if font_size_el is not None:
                            font_size_el.text = "26"  # Much larger bold font
                            print(f"  Updated Font Size to 26 for {obj_name_el.text}")

# Save the updated XML
tree.write(output_path, encoding="utf-8", xml_declaration=True)
print(f"[SUCCESS] Resized buttons saved to {output_path}")
