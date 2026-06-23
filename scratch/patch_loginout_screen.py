# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os

# Input path from actual export of project loginlogoutscada
actual_export_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Login_out.xml"
# Output path for importer
output_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens"
output_loginout_path = os.path.join(output_dir, "Hmi.Screen.Login_out.xml")
# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Delete other xml files in target directory to avoid importing unneeded screens
for f in os.listdir(output_dir):
    if f.endswith(".xml") and f not in ("Hmi.Screen.Login_out.xml",):
        try:
            os.remove(os.path.join(output_dir, f))
            print("[CLEANUP] Removed old XML: " + f.encode('ascii', errors='replace').decode('ascii'))
        except Exception as e:
            print("[CLEANUP] Failed to remove XML file")

# Parse the actual export XML
ET.register_namespace('', '') # default namespace
tree = ET.parse(actual_export_path)
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

# Generate unique IDs starting at 0x5000
id_counter = 20480
def get_next_id():
    global id_counter
    res = hex(id_counter)[2:].upper()
    id_counter += 1
    return res

def create_styled_button(name, text, left, top, width, height, system_function_name, is_navigation=False, navigation_target="Screen_1", back_color="30, 41, 59", border_color="71, 85, 105"):
    btn = ET.Element("Hmi.Screen.Button", {
        "ID": get_next_id(),
        "CompositionName": "ScreenItems"
    })
    
    attrs = ET.SubElement(btn, "AttributeList")
    ET.SubElement(attrs, "BackColor").text = back_color
    ET.SubElement(attrs, "BackFillStyle").text = "Solid"
    ET.SubElement(attrs, "BorderColor").text = border_color
    ET.SubElement(attrs, "BorderWidth").text = "1"
    ET.SubElement(attrs, "CornerRadius").text = "6"
    ET.SubElement(attrs, "EdgeStyle").text = "Solid"
    ET.SubElement(attrs, "Enabled").text = "true"
    ET.SubElement(attrs, "ForeColor").text = "255, 255, 255"
    ET.SubElement(attrs, "Height").text = str(height)
    ET.SubElement(attrs, "HorizontalAlignment").text = "Center"
    ET.SubElement(attrs, "Left").text = str(left)
    ET.SubElement(attrs, "ObjectName").text = name
    ET.SubElement(attrs, "TabIndex").text = "1"
    ET.SubElement(attrs, "TextOrientation").text = "Horizontal"
    ET.SubElement(attrs, "Top").text = str(top)
    ET.SubElement(attrs, "VerticalAlignment").text = "Middle"
    ET.SubElement(attrs, "Width").text = str(width)
    
    objs = ET.SubElement(btn, "ObjectList")
    
    # Event Click
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
    
    if is_navigation:
        entry_objs = ET.SubElement(entry, "ObjectList")
        # Parameter: Screen name
        p1 = ET.SubElement(entry_objs, "Hmi.Event.FunctionListEntryParameter", {
            "ID": get_next_id(),
            "CompositionName": "Parameters"
        })
        p1_attrs = ET.SubElement(p1, "AttributeList")
        ET.SubElement(p1_attrs, "Name").text = "Screen name"
        p1_links = ET.SubElement(p1, "LinkList")
        val = ET.SubElement(p1_links, "Value", {"TargetID": "@OpenLink"})
        ET.SubElement(val, "Name").text = navigation_target
        
        # Parameter: Object number
        p2 = ET.SubElement(entry_objs, "Hmi.Event.FunctionListEntryParameter", {
            "ID": get_next_id(),
            "CompositionName": "Parameters"
        })
        p2_attrs = ET.SubElement(p2, "AttributeList")
        ET.SubElement(p2_attrs, "Name").text = "Object number"
        ET.SubElement(p2_attrs, "Value", {"Type": "System.Int32"}).text = "0"
        
    elif system_function_name == "StopRuntime":
        # Do not add parameters for StopRuntime to avoid type resolution issues
        pass
        
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
    ET.SubElement(fi_attrs, "FontSize").text = "14"
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

# Remove existing buttons to avoid accumulation
to_remove = []
for item in object_list:
    if item.tag == "Hmi.Screen.Button":
        attr_list = item.find("AttributeList")
        if attr_list is not None:
            obj_name = attr_list.find("ObjectName")
            if obj_name is not None and obj_name.text in ("Btn_Login_Mockup", "Btn_Enter_System", "Btn_Login", "Btn_Logout", "Btn_Exit"):
                to_remove.append(item)
for item in to_remove:
    object_list.remove(item)

# Create and append buttons (Centered inside the new glassmorphic panel)
# Panel horizontal center is 1920/2 = 960. If button width is 300, Left = 960 - 150 = 810.
btn_login = create_styled_button("Btn_Login", "ĐĂNG NHẬP (LOGIN)", 810, 380, 300, 50, "ShowLogonDialog", back_color="30, 41, 59", border_color="71, 85, 105")
btn_enter = create_styled_button("Btn_Enter_System", "VÀO HỆ THỐNG (SCADA)", 810, 450, 300, 50, "ActivateScreen", is_navigation=True, navigation_target="Screen_2", back_color="16, 185, 129", border_color="52, 211, 153")
btn_logout = create_styled_button("Btn_Logout", "ĐĂNG XUẤT (LOGOFF)", 810, 520, 300, 50, "Logoff", back_color="75, 85, 99", border_color="156, 163, 175")

object_list.append(btn_login)
object_list.append(btn_enter)
object_list.append(btn_logout)

# Save the updated Login_out.xml
tree.write(output_loginout_path, encoding="utf-8", xml_declaration=True)
print(f"[SUCCESS] Patched Hmi.Screen.Login_out.xml saved to {output_loginout_path}")

# Done patching Login_out.xml
