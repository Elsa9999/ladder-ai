# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai1\HMI\hmi_export\Screens\Hmi.Screen.Screen_1.xml"

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

# Remove old buttons to avoid duplicates if re-run
to_remove = []
for item in object_list:
    if item.tag == "Hmi.Screen.Button":
        attr_list = item.find("AttributeList")
        if attr_list is not None:
            obj_name_el = attr_list.find("ObjectName")
            if obj_name_el is not None and obj_name_el.text in ("Btn_Login", "Btn_Logout"):
                to_remove.append(item)

for item in to_remove:
    object_list.remove(item)
    print(f"Removed old button: {item.find('AttributeList/ObjectName').text}")

# Generate unique IDs
max_id = 8192
for item in object_list:
    if "ID" in item.attrib:
        try:
            val = int(item.attrib["ID"], 16)
            if val > max_id:
                max_id = val
        except ValueError:
            pass

id_counter = max_id + 1
def get_next_id():
    global id_counter
    res = hex(id_counter)[2:].upper()
    id_counter += 1
    return res

def create_system_button(name, text, left, top, width, height, system_function_name):
    # Create Button element
    btn = ET.Element("Hmi.Screen.Button", {
        "ID": get_next_id(),
        "CompositionName": "ScreenItems"
    })
    
    # Attributes
    attrs = ET.SubElement(btn, "AttributeList")
    ET.SubElement(attrs, "BackColor").text = "88, 90, 103"  # Sleek dark gray
    ET.SubElement(attrs, "BackFillStyle").text = "Solid"
    ET.SubElement(attrs, "BorderColor").text = "0, 0, 0"
    ET.SubElement(attrs, "BorderWidth").text = "1"
    ET.SubElement(attrs, "CornerRadius").text = "4"
    ET.SubElement(attrs, "EdgeStyle").text = "Solid"
    ET.SubElement(attrs, "Enabled").text = "true"
    ET.SubElement(attrs, "ForeColor").text = "255, 255, 255"
    ET.SubElement(attrs, "Height").text = str(height)
    ET.SubElement(attrs, "HorizontalAlignment").text = "Center"
    ET.SubElement(attrs, "Left").text = str(left)
    ET.SubElement(attrs, "ObjectName").text = name
    ET.SubElement(attrs, "TabIndex").text = "100"
    ET.SubElement(attrs, "TextOrientation").text = "Horizontal"
    ET.SubElement(attrs, "Top").text = str(top)
    ET.SubElement(attrs, "VerticalAlignment").text = "Middle"
    ET.SubElement(attrs, "Width").text = str(width)
    
    objs = ET.SubElement(btn, "ObjectList")
    
    # Event definition
    evt = ET.SubElement(objs, "Hmi.Event.Event", {
        "ID": get_next_id(),
        "CompositionName": "Events"
    })
    ET.SubElement(evt, "AttributeList").append(ET.Element("Name"))
    evt.find("AttributeList/Name").text = "Click"
    
    evt_objs = ET.SubElement(evt, "ObjectList")
    handler = ET.SubElement(evt_objs, "Hmi.Event.FunctionListEventHandler", {
        "ID": get_next_id(),
        "CompositionName": "EventHandler"
    })
    handler_objs = ET.SubElement(handler, "ObjectList")
    entry = ET.SubElement(handler_objs, "Hmi.Event.FunctionListEntry", {
        "ID": get_next_id(),
        "CompositionName": "FunctionListEntries"
    })
    entry_attrs = ET.SubElement(entry, "AttributeList")
    ET.SubElement(entry_attrs, "Name").text = system_function_name
    ET.SubElement(entry_attrs, "Type").text = "SystemFunction"
    
    # Font
    font = ET.SubElement(objs, "Hmi.Globalization.MultiLingualFont", {
        "ID": get_next_id(),
        "CompositionName": "Font"
    })
    font_objs = ET.SubElement(font, "ObjectList")
    font_item = ET.SubElement(font_objs, "Hmi.Globalization.FontItem", {
        "ID": get_next_id(),
        "CompositionName": "Items"
    })
    fi_attrs = ET.SubElement(font_item, "AttributeList")
    ET.SubElement(fi_attrs, "Culture").text = "en-US"
    ET.SubElement(fi_attrs, "FontFamily").text = "Arial"
    ET.SubElement(fi_attrs, "FontSize").text = "12"
    ET.SubElement(fi_attrs, "FontStyle").text = "Bold"
    
    # Text
    txt = ET.SubElement(objs, "MultilingualText", {
        "ID": get_next_id(),
        "CompositionName": "TextOff"
    })
    txt_objs = ET.SubElement(txt, "ObjectList")
    txt_item = ET.SubElement(txt_objs, "MultilingualTextItem", {
        "ID": get_next_id(),
        "CompositionName": "Items"
    })
    ti_attrs = ET.SubElement(txt_item, "AttributeList")
    ET.SubElement(ti_attrs, "Culture").text = "en-US"
    ET.SubElement(ti_attrs, "Text").text = f"<body><p>{text}</p></body>"
    
    return btn

# Position the buttons on the top right area (e.g. Left: 1720 and 1810, Top: 70 - below header logo)
login_btn = create_system_button("Btn_Login", "Login", 1720, 70, 80, 26, "ShowLogonDialog")
logout_btn = create_system_button("Btn_Logout", "Logout", 1810, 70, 80, 26, "Logoff")

object_list.append(login_btn)
object_list.append(logout_btn)
print("Created and appended Btn_Login and Btn_Logout to the Screen XML!")

# Save XML
tree.write(xml_path, encoding="utf-8", xml_declaration=True)
print("[SUCCESS] Screen XML patched with Logon/Logoff buttons!")
