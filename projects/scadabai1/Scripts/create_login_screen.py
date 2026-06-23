# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai1\HMI\hmi_export\Screens\Hmi.Screen.Screen_Login.xml"

# Ensure directory exists
os.makedirs(os.path.dirname(xml_path), exist_ok=True)

# Generate unique IDs starting at 0x3000
id_counter = 12288
def get_next_id():
    global id_counter
    res = hex(id_counter)[2:].upper()
    id_counter += 1
    return res

# Root document element
root_doc = ET.Element("Document")
ET.SubElement(root_doc, "Engineering", {"version": "V18"})

# DocumentInfo (metadata)
doc_info = ET.SubElement(root_doc, "DocumentInfo")
ET.SubElement(doc_info, "Created").text = "2026-06-11T07:10:00.0000000Z"
ET.SubElement(doc_info, "ExportSetting").text = "WithDefaults"
inst_prods = ET.SubElement(doc_info, "InstalledProducts")
prod1 = ET.SubElement(inst_prods, "Product")
ET.SubElement(prod1, "DisplayName").text = "Totally Integrated Automation Portal"
ET.SubElement(prod1, "DisplayVersion").text = "V18"
prod2 = ET.SubElement(inst_prods, "Product")
ET.SubElement(prod2, "DisplayName").text = "WinCC Professional"
ET.SubElement(prod2, "DisplayVersion").text = "V18"

# Screen Object
screen = ET.SubElement(root_doc, "Hmi.Screen.Screen", {"ID": get_next_id()})
screen_attrs = ET.SubElement(screen, "AttributeList")
ET.SubElement(screen_attrs, "ActiveLayer").text = "0"
ET.SubElement(screen_attrs, "BackColor").text = "24, 28, 49"  # Elegant Dark Navy
ET.SubElement(screen_attrs, "GridColor").text = "0, 0, 0"
ET.SubElement(screen_attrs, "Height").text = "1080"
ET.SubElement(screen_attrs, "Name").text = "Screen_Login"
ET.SubElement(screen_attrs, "Number").text = "2"
ET.SubElement(screen_attrs, "Visible").text = "true"
ET.SubElement(screen_attrs, "Width").text = "1920"

screen_objs = ET.SubElement(screen, "ObjectList")

# HelpText
help_txt = ET.SubElement(screen_objs, "MultilingualText", {"ID": get_next_id(), "CompositionName": "HelpText"})
ht_objs = ET.SubElement(help_txt, "ObjectList")
ht_item = ET.SubElement(ht_objs, "MultilingualTextItem", {"ID": get_next_id(), "CompositionName": "Items"})
ht_attrs = ET.SubElement(ht_item, "AttributeList")
ET.SubElement(ht_attrs, "Culture").text = "en-US"
ET.SubElement(ht_attrs, "Text").text = ""

# ScreenLayer
layer = ET.SubElement(screen_objs, "Hmi.Screen.ScreenLayer", {"ID": get_next_id(), "CompositionName": "Layers"})
layer_attrs = ET.SubElement(layer, "AttributeList")
ET.SubElement(layer_attrs, "Index").text = "0"
ET.SubElement(layer_attrs, "Name").text = ""
ET.SubElement(layer_attrs, "VisibleES").text = "true"

layer_objs = ET.SubElement(layer, "ObjectList")

# Function to create text field
def add_text_field(text, left, top, width, height, font_size, font_style="Regular", fore_color="255, 255, 255", alignment="Center"):
    tf = ET.SubElement(layer_objs, "Hmi.Screen.TextField", {
        "ID": get_next_id(),
        "CompositionName": "ScreenItems"
    })
    tf_attrs = ET.SubElement(tf, "AttributeList")
    ET.SubElement(tf_attrs, "BackColor").text = "255, 255, 255"
    ET.SubElement(tf_attrs, "BackFillStyle").text = "Transparent"
    ET.SubElement(tf_attrs, "BorderWidth").text = "0"
    ET.SubElement(tf_attrs, "ForeColor").text = fore_color
    ET.SubElement(tf_attrs, "Height").text = str(height)
    ET.SubElement(tf_attrs, "HorizontalAlignment").text = alignment
    ET.SubElement(tf_attrs, "Left").text = str(left)
    ET.SubElement(tf_attrs, "ObjectName").text = f"Text_field_{get_next_id()}"
    ET.SubElement(tf_attrs, "TextOrientation").text = "Horizontal"
    ET.SubElement(tf_attrs, "Top").text = str(top)
    ET.SubElement(tf_attrs, "VerticalAlignment").text = "Middle"
    ET.SubElement(tf_attrs, "Width").text = str(width)
    
    tf_objs = ET.SubElement(tf, "ObjectList")
    
    # Font
    font = ET.SubElement(tf_objs, "Hmi.Globalization.MultiLingualFont", {
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
    ET.SubElement(fi_attrs, "FontSize").text = str(font_size)
    ET.SubElement(fi_attrs, "FontStyle").text = font_style
    
    # Text
    txt = ET.SubElement(tf_objs, "MultilingualText", {
        "ID": get_next_id(),
        "CompositionName": "Text"
    })
    txt_objs = ET.SubElement(txt, "ObjectList")
    txt_item = ET.SubElement(txt_objs, "MultilingualTextItem", {
        "ID": get_next_id(),
        "CompositionName": "Items"
    })
    ti_attrs = ET.SubElement(txt_item, "AttributeList")
    ET.SubElement(ti_attrs, "Culture").text = "en-US"
    ET.SubElement(ti_attrs, "Text").text = f"<body><p>{text}</p></body>"

# Function to create button
def add_button(name, text, left, top, width, height, system_function_name, is_navigation=False, back_color="34, 38, 62", fore_color="255, 255, 255"):
    btn = ET.SubElement(layer_objs, "Hmi.Screen.Button", {
        "ID": get_next_id(),
        "CompositionName": "ScreenItems"
    })
    btn_attrs = ET.SubElement(btn, "AttributeList")
    ET.SubElement(btn_attrs, "BackColor").text = back_color
    ET.SubElement(btn_attrs, "BackFillStyle").text = "Solid"
    ET.SubElement(btn_attrs, "BorderColor").text = "71, 73, 87"
    ET.SubElement(btn_attrs, "BorderWidth").text = "1"
    ET.SubElement(btn_attrs, "CornerRadius").text = "6"
    ET.SubElement(btn_attrs, "EdgeStyle").text = "Solid"
    ET.SubElement(btn_attrs, "Enabled").text = "true"
    ET.SubElement(btn_attrs, "ForeColor").text = fore_color
    ET.SubElement(btn_attrs, "Height").text = str(height)
    ET.SubElement(btn_attrs, "HorizontalAlignment").text = "Center"
    ET.SubElement(btn_attrs, "Left").text = str(left)
    ET.SubElement(btn_attrs, "ObjectName").text = name
    ET.SubElement(btn_attrs, "TabIndex").text = "1"
    ET.SubElement(btn_attrs, "TextOrientation").text = "Horizontal"
    ET.SubElement(btn_attrs, "Top").text = str(top)
    ET.SubElement(btn_attrs, "VerticalAlignment").text = "Middle"
    ET.SubElement(btn_attrs, "Width").text = str(width)
    
    btn_objs = ET.SubElement(btn, "ObjectList")
    
    # Event
    evt = ET.SubElement(btn_objs, "Hmi.Event.Event", {
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
    
    # Parameters for event
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
        ET.SubElement(val, "Name").text = "Screen_1"
        
        # Parameter: Object number
        p2 = ET.SubElement(entry_objs, "Hmi.Event.FunctionListEntryParameter", {
            "ID": get_next_id(),
            "CompositionName": "Parameters"
        })
        p2_attrs = ET.SubElement(p2, "AttributeList")
        ET.SubElement(p2_attrs, "Name").text = "Object number"
        ET.SubElement(p2_attrs, "Value", {"Type": "System.Int32"}).text = "0"


    # Font
    font = ET.SubElement(btn_objs, "Hmi.Globalization.MultiLingualFont", {
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
    ET.SubElement(fi_attrs, "FontSize").text = "15"
    ET.SubElement(fi_attrs, "FontStyle").text = "Bold"
    
    # Text
    txt = ET.SubElement(btn_objs, "MultilingualText", {
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

# 1. Main Title
add_text_field("HỆ THỐNG ĐIỀU KHIỂN VÀ GIÁM SÁT MIXING", 360, 200, 1200, 80, 32, "Bold", "255, 255, 255")

# 2. Subtitle
add_text_field("DỰ ÁN LIÊN GIA BẢO - AREA 1400", 360, 280, 1200, 40, 16, "Regular", "170, 175, 190")

# 3. Decorative Frame (Rectangle)
rect = ET.SubElement(layer_objs, "Hmi.Screen.Rectangle", {
    "ID": get_next_id(),
    "CompositionName": "ScreenItems"
})
rect_attrs = ET.SubElement(rect, "AttributeList")
ET.SubElement(rect_attrs, "BackColor").text = "34, 38, 62"  # Lighter navy panel
ET.SubElement(rect_attrs, "BackFillStyle").text = "Solid"
ET.SubElement(rect_attrs, "BorderColor").text = "71, 73, 87"
ET.SubElement(rect_attrs, "BorderWidth").text = "1"
ET.SubElement(rect_attrs, "EdgeStyle").text = "Solid"
ET.SubElement(rect_attrs, "Flashing").text = "None"
ET.SubElement(rect_attrs, "Height").text = "280"
ET.SubElement(rect_attrs, "Left").text = "710"
ET.SubElement(rect_attrs, "ObjectName").text = f"Panel_Login_Background"
ET.SubElement(rect_attrs, "RoundCornerHeight").text = "12"
ET.SubElement(rect_attrs, "RoundCornerWidth").text = "12"
ET.SubElement(rect_attrs, "TabIndex").text = "-1"
ET.SubElement(rect_attrs, "Top").text = "380"
ET.SubElement(rect_attrs, "UseDesignColorSchema").text = "false"
ET.SubElement(rect_attrs, "Width").text = "500"

# 4. Buttons inside panel
# Logon Button
add_button("Btn_Screen_Login", "ĐĂNG NHẬP (LOGIN)", 760, 420, 400, 50, "ShowLogonDialog")

# Logoff Button
add_button("Btn_Screen_Logout", "ĐĂNG XUẤT (LOGOFF)", 760, 490, 400, 50, "Logoff")

# Enter System Button (Green SeaGreen Highlight)
add_button("Btn_Enter_System", "VÀO HỆ THỐNG (ENTER SYSTEM)", 760, 560, 400, 50, "ActivateScreen", is_navigation=True, back_color="46, 139, 87")

# Write to file
# ElementTree needs to be written out
tree = ET.ElementTree(root_doc)
tree.write(xml_path, encoding="utf-8", xml_declaration=True)
print(f"[SUCCESS] Generated Login Screen XML at {xml_path}")

# Synchronize directly to scratch folder for import
scratch_xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens\Hmi.Screen.Screen_Login.xml"
os.makedirs(os.path.dirname(scratch_xml_path), exist_ok=True)
tree.write(scratch_xml_path, encoding="utf-8", xml_declaration=True)
print(f"[SUCCESS] Copied Login Screen XML to {scratch_xml_path}")

