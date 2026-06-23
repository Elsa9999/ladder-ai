# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

input_xml = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Screen_2.xml"
output_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens"
output_xml = os.path.join(output_dir, "Hmi.Screen.Screen_2.xml")

if not os.path.exists(input_xml):
    print(f"[ERROR] Source XML not found: {input_xml}")
    exit(1)

ET.register_namespace('', '')
tree = ET.parse(input_xml)
root = tree.getroot()

# 1. Parse existing IDs to find maximum ID (to prevent collision)
max_id = 0
for elem in root.iter():
    id_attr = elem.get("ID")
    if id_attr:
        try:
            # Parse hex if possible, else decimal
            val = int(id_attr, 16)
            if val > max_id:
                max_id = val
        except ValueError:
            pass

id_counter = max_id + 1000
print(f"Max existing ID in hex is {hex(max_id)}, starting counter at {hex(id_counter)}")

def get_next_id():
    global id_counter
    res = hex(id_counter)[2:].upper()
    id_counter += 1
    return res

# Helper functions for generating XML nodes (similar to generate_scada_screens.py)
def create_multilingual_text(parent, comp_name, text_val):
    txt = ET.SubElement(parent, "MultilingualText", {
        "ID": get_next_id(),
        "CompositionName": comp_name
    })
    txt_objs = ET.SubElement(txt, "ObjectList")
    txt_item = ET.SubElement(txt_objs, "MultilingualTextItem", {
        "ID": get_next_id(),
        "CompositionName": "Items"
    })
    ti_attrs = ET.SubElement(txt_item, "AttributeList")
    ET.SubElement(ti_attrs, "Culture").text = "en-US"
    ET.SubElement(ti_attrs, "Text").text = f"<body><p>{text_val}</p></body>"
    return txt

def create_font(parent, family="Arial", size=14, bold=True):
    font = ET.SubElement(parent, "Hmi.Globalization.MultiLingualFont", {
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
    ET.SubElement(fi_attrs, "FontFamily").text = family
    ET.SubElement(fi_attrs, "FontSize").text = str(size)
    if bold:
        ET.SubElement(fi_attrs, "FontStyle").text = "Bold"
    else:
        ET.SubElement(fi_attrs, "FontStyle").text = "Regular"
    return font

def add_visibility_animation(parent, tag_name="Logged_In", min_val=1, max_val=999):
    anim = ET.SubElement(parent, "Hmi.Dynamic.VisibilityAnimation", {
        "ID": get_next_id(),
        "CompositionName": "Animations"
    })
    anim_attrs = ET.SubElement(anim, "AttributeList")
    ET.SubElement(anim_attrs, "Name").text = "VisibilityAnimation"
    ET.SubElement(anim_attrs, "RangeEnd").text = str(max_val)
    ET.SubElement(anim_attrs, "RangeStart").text = str(min_val)
    ET.SubElement(anim_attrs, "Visible").text = "true"
    
    anim_objs = ET.SubElement(anim, "ObjectList")
    trigger = ET.SubElement(anim_objs, "Hmi.Dynamic.TagElementTrigger", {
        "ID": get_next_id(),
        "CompositionName": "VisibilityTag"
    })
    trigger_links = ET.SubElement(trigger, "LinkList")
    val = ET.SubElement(trigger_links, "Tag", {"TargetID": "@OpenLink"})
    ET.SubElement(val, "Name").text = tag_name

def create_btn_xml(parent, name, text, left, top, width, height, system_function_name, navigation_target=None, back_color="30, 41, 59", border_color="71, 85, 105"):
    btn = ET.SubElement(parent, "Hmi.Screen.Button", {
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
    
    if navigation_target:
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
        
    create_font(objs, size=13, bold=True)
    create_multilingual_text(objs, "TextOff", text)
    return btn

def add_appearance_animation(element, tag_name, limits_ranges):
    objs = element.find("ObjectList")
    if objs is None:
        objs = ET.SubElement(element, "ObjectList")
    
    # Remove existing RangeAppearanceAnimation if any
    to_remove = []
    for item in objs:
        if item.tag == "Hmi.Dynamic.RangeAppearanceAnimation":
            to_remove.append(item)
    for item in to_remove:
        objs.remove(item)
        
    anim = ET.SubElement(objs, "Hmi.Dynamic.RangeAppearanceAnimation", {
        "ID": get_next_id(),
        "CompositionName": "Animations"
    })
    
    attrs = ET.SubElement(anim, "AttributeList")
    ET.SubElement(attrs, "Name").text = "RangeAppearanceAnimation"
    
    anim_objs = ET.SubElement(anim, "ObjectList")
    
    trigger = ET.SubElement(anim_objs, "Hmi.Dynamic.TagElementTrigger", {
        "ID": get_next_id(),
        "CompositionName": "RangeTag"
    })
    trigger_links = ET.SubElement(trigger, "LinkList")
    val_tag = ET.SubElement(trigger_links, "Tag", {"TargetID": "@OpenLink"})
    ET.SubElement(val_tag, "Name").text = tag_name
    
    for item in limits_ranges:
        if len(item) == 4:
            low, high, bg_color, fg_color = item
            flashing = "No"
        else:
            low, high, bg_color, fg_color, flashing = item
            
        r = ET.SubElement(anim_objs, "Hmi.Dynamic.Range", {
            "ID": get_next_id(),
            "CompositionName": "RangeValues"
        })
        r_attrs = ET.SubElement(r, "AttributeList")
        ET.SubElement(r_attrs, "BackColor").text = bg_color
        ET.SubElement(r_attrs, "FlashingType").text = flashing
        ET.SubElement(r_attrs, "ForeColor").text = fg_color
        ET.SubElement(r_attrs, "LowerLimit").text = str(int(low))
        ET.SubElement(r_attrs, "UpperLimit").text = str(int(high))

def create_warning_badge_xml(parent, name, text, left, top, width, height, tag_name, limits_ranges):
    btn = ET.SubElement(parent, "Hmi.Screen.Button", {
        "ID": get_next_id(),
        "CompositionName": "ScreenItems"
    })
    
    attrs = ET.SubElement(btn, "AttributeList")
    ET.SubElement(attrs, "BackColor").text = "15, 23, 42" # Invisible by default (blends with header background)
    ET.SubElement(attrs, "BackFillStyle").text = "Solid"
    ET.SubElement(attrs, "BorderWidth").text = "0" # No border to prevent outline showing
    ET.SubElement(attrs, "CornerRadius").text = "6"
    ET.SubElement(attrs, "EdgeStyle").text = "Solid"
    ET.SubElement(attrs, "Enabled").text = "true"
    ET.SubElement(attrs, "ForeColor").text = "15, 23, 42" # Invisible text by default
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
    create_font(objs, size=13, bold=True)
    create_multilingual_text(objs, "TextOff", text)
    
    # Add appearance animation (handles blending and warning colors)
    add_appearance_animation(btn, tag_name, limits_ranges)
    
    return btn

def create_header_footer_items(object_list, screen_title):
    # 1. Header background bar (y: 0 to 100)
    bg = ET.SubElement(object_list, "Hmi.Screen.Rectangle", {
        "ID": get_next_id(),
        "CompositionName": "ScreenItems"
    })
    bg_attrs = ET.SubElement(bg, "AttributeList")
    ET.SubElement(bg_attrs, "BackColor").text = "15, 23, 42" # Dark slate
    ET.SubElement(bg_attrs, "BackFillStyle").text = "Solid"
    ET.SubElement(bg_attrs, "BorderColor").text = "51, 65, 85"
    ET.SubElement(bg_attrs, "BorderWidth").text = "1"
    ET.SubElement(bg_attrs, "Height").text = "100"
    ET.SubElement(bg_attrs, "Left").text = "0"
    ET.SubElement(bg_attrs, "ObjectName").text = "Header_Bg"
    ET.SubElement(bg_attrs, "Top").text = "0"
    ET.SubElement(bg_attrs, "Width").text = "1920"

    # 2. Header Title Text
    title = ET.SubElement(object_list, "Hmi.Screen.TextField", {
        "ID": get_next_id(),
        "CompositionName": "ScreenItems"
    })
    t_attrs = ET.SubElement(title, "AttributeList")
    ET.SubElement(t_attrs, "BackFillStyle").text = "Transparent"
    ET.SubElement(t_attrs, "BorderWidth").text = "0"
    ET.SubElement(t_attrs, "ForeColor").text = "255, 255, 255"
    ET.SubElement(t_attrs, "Height").text = "60"
    ET.SubElement(t_attrs, "HorizontalAlignment").text = "Left"
    ET.SubElement(t_attrs, "Left").text = "40"
    ET.SubElement(t_attrs, "ObjectName").text = "Header_Title"
    ET.SubElement(t_attrs, "Top").text = "20"
    ET.SubElement(t_attrs, "VerticalAlignment").text = "Middle"
    ET.SubElement(t_attrs, "Width").text = "800"
    t_objs = ET.SubElement(title, "ObjectList")
    create_font(t_objs, size=24, bold=True)
    create_multilingual_text(t_objs, "Text", screen_title)

    # 3. Header Warning Badges (visible under conditions, flashing under high limit)
    # TT32 Temperature Warning Badge
    create_warning_badge_xml(
        object_list,
        "Header_Alert_TT32",
        "⚠️ TT32 CAO",
        840, 25, 110, 50,
        tag_name="1400_TT32_PV",
        limits_ranges=[
            (0, 74, "15, 23, 42", "15, 23, 42", "No"),
            (75, 77, "245, 158, 11", "0, 0, 0", "No"),
            (78, 999, "220, 38, 38", "255, 255, 255", "Fast")
        ]
    )

    # TX35 Pressure Warning Badge
    create_warning_badge_xml(
        object_list,
        "Header_Alert_TX35",
        "⚠️ TX35 CAO",
        960, 25, 110, 50,
        tag_name="1406_TX35_PV",
        limits_ranges=[
            (0, 6, "15, 23, 42", "15, 23, 42", "No"),
            (7, 7, "245, 158, 11", "0, 0, 0", "No"),
            (8, 999, "220, 38, 38", "255, 255, 255", "Fast")
        ]
    )

    # 4. Header Logged_In Text Label
    op_label = ET.SubElement(object_list, "Hmi.Screen.TextField", {
        "ID": get_next_id(),
        "CompositionName": "ScreenItems"
    })
    ol_attrs = ET.SubElement(op_label, "AttributeList")
    ET.SubElement(ol_attrs, "BackFillStyle").text = "Transparent"
    ET.SubElement(ol_attrs, "BorderWidth").text = "0"
    ET.SubElement(ol_attrs, "ForeColor").text = "148, 163, 184"
    ET.SubElement(ol_attrs, "Height").text = "40"
    ET.SubElement(ol_attrs, "HorizontalAlignment").text = "Right"
    ET.SubElement(ol_attrs, "Left").text = "1100"
    ET.SubElement(ol_attrs, "ObjectName").text = "Header_Operator_Label"
    ET.SubElement(ol_attrs, "Top").text = "30"
    ET.SubElement(ol_attrs, "VerticalAlignment").text = "Middle"
    ET.SubElement(ol_attrs, "Width").text = "300"
    ol_objs = ET.SubElement(op_label, "ObjectList")
    create_font(ol_objs, size=14, bold=False)
    create_multilingual_text(ol_objs, "Text", "TÀI KHOẢN VẬN HÀNH:")

    # 5. Header Username IOField - dùng @CurrentUser system tag (String) để hiển thị tên user đang đăng nhập
    op_field = ET.SubElement(object_list, "Hmi.Screen.IOField", {
        "ID": get_next_id(),
        "CompositionName": "ScreenItems"
    })
    of_attrs = ET.SubElement(op_field, "AttributeList")
    ET.SubElement(of_attrs, "BackColor").text = "30, 41, 59"
    ET.SubElement(of_attrs, "BackFillStyle").text = "Solid"
    ET.SubElement(of_attrs, "BorderColor").text = "71, 85, 105"
    ET.SubElement(of_attrs, "BorderWidth").text = "1"
    ET.SubElement(of_attrs, "DataFormat").text = "String"
    ET.SubElement(of_attrs, "FormatPattern").text = "????????????????????"
    ET.SubElement(of_attrs, "FieldLength").text = "20"
    ET.SubElement(of_attrs, "ForeColor").text = "34, 197, 94"
    ET.SubElement(of_attrs, "Height").text = "40"
    ET.SubElement(of_attrs, "HorizontalAlignment").text = "Center"
    ET.SubElement(of_attrs, "Left").text = "1410"
    ET.SubElement(of_attrs, "Mode").text = "Output"
    ET.SubElement(of_attrs, "ObjectName").text = "Header_Operator_Field"
    ET.SubElement(of_attrs, "Top").text = "30"
    ET.SubElement(of_attrs, "VerticalAlignment").text = "Middle"
    ET.SubElement(of_attrs, "Width").text = "160"
    of_objs = ET.SubElement(op_field, "ObjectList")
    create_font(of_objs, size=14, bold=True)
    create_multilingual_text(of_objs, "HelpText", "")

    # ProcessValue = @CurrentUser (WinCC system tag for current logged-in username)
    prop = ET.SubElement(of_objs, "Hmi.Screen.Property", {
        "ID": get_next_id(),
        "CompositionName": "Properties"
    })
    p_attrs = ET.SubElement(prop, "AttributeList")
    ET.SubElement(p_attrs, "Name").text = "ProcessValue"
    prop_objs = ET.SubElement(prop, "ObjectList")
    conn = ET.SubElement(prop_objs, "Hmi.Dynamic.TagConnectionDynamic", {
        "ID": get_next_id(),
        "CompositionName": "Dynamic"
    })
    c_attrs = ET.SubElement(conn, "AttributeList")
    ET.SubElement(c_attrs, "Indirect").text = "false"
    conn_links = ET.SubElement(conn, "LinkList")
    val_tag = ET.SubElement(conn_links, "Tag", {"TargetID": "@OpenLink"})
    ET.SubElement(val_tag, "Name").text = "@CurrentUser"

    # 6. Header Logout Button
    logout_btn = create_btn_xml(object_list, "Header_Logout_Btn", "ĐĂNG XUẤT", 1550, 25, 150, 50, "Logoff", back_color="75, 85, 99", border_color="107, 114, 128")

    # 7. Footer background bar (y: 980 to 1080)
    footer = ET.SubElement(object_list, "Hmi.Screen.Rectangle", {
        "ID": get_next_id(),
        "CompositionName": "ScreenItems"
    })
    f_attrs = ET.SubElement(footer, "AttributeList")
    ET.SubElement(f_attrs, "BackColor").text = "15, 23, 42"
    ET.SubElement(f_attrs, "BackFillStyle").text = "Solid"
    ET.SubElement(f_attrs, "BorderColor").text = "51, 65, 85"
    ET.SubElement(f_attrs, "BorderWidth").text = "1"
    ET.SubElement(f_attrs, "Height").text = "100"
    ET.SubElement(f_attrs, "Left").text = "0"
    ET.SubElement(f_attrs, "ObjectName").text = "Footer_Bg"
    ET.SubElement(f_attrs, "Top").text = "980"
    ET.SubElement(f_attrs, "Width").text = "1920"

    # 8. Navigation Buttons - chỉ 2 màn hình: Login/out và Screen_2
    btn_home = create_btn_xml(object_list, "Footer_Home_Btn", "MÀN HÌNH ĐĂNG NHẬP / HOME", 200, 995, 400, 70, "ActivateScreen", navigation_target="Login/out", back_color="30, 41, 59", border_color="71, 85, 105")
    
    btn_scada = create_btn_xml(object_list, "Footer_SCADA_Btn", "MÀN HÌNH CÔNG NGHỆ (SCADA) - ĐANG XEM", 1320, 995, 400, 70, "ActivateScreen", navigation_target="Screen_2", back_color="16, 185, 129", border_color="52, 211, 153")


# Locate Screen Layer containing ScreenItems
layer = root.find(".//Hmi.Screen.ScreenLayer")
if layer is None:
    print("[ERROR] Layer not found!")
    exit(1)

object_list = layer.find("ObjectList")
if object_list is None:
    print("[ERROR] ObjectList of Layer not found!")
    exit(1)

# Find and apply appearance animation to Temperature and Pressure IO fields
for item in object_list:
    if item.tag == "Hmi.Screen.IOField":
        attr_list = item.find("AttributeList")
        if attr_list is not None:
            obj_name_el = attr_list.find("ObjectName")
            if obj_name_el is not None:
                obj_name = obj_name_el.text
                if obj_name == "I/O field_1":
                    print("Adding appearance animation to I/O field_1 (Nhiệt độ)")
                    add_appearance_animation(item, "1400_TT32_PV", [
                        (0, 74, "255, 255, 255", "0, 0, 0", "No"),
                        (75, 77, "245, 158, 11", "0, 0, 0", "No"),
                        (78, 150, "220, 38, 38", "255, 255, 255", "Fast")
                    ])
                elif obj_name == "I/O field_4":
                    print("Adding appearance animation to I/O field_4 (Áp suất)")
                    add_appearance_animation(item, "1406_TX35_PV", [
                        (0, 6, "255, 255, 255", "0, 0, 0", "No"),
                        (7, 7, "245, 158, 11", "0, 0, 0", "No"),
                        (8, 15, "220, 38, 38", "255, 255, 255", "Fast")
                    ])

# Remove any old header/footer/warning/alarm view elements if they exist to avoid duplication
to_remove = []
for item in object_list:
    attr_list = item.find("AttributeList")
    if attr_list is not None:
        obj_name_el = attr_list.find("ObjectName")
        if obj_name_el is not None:
            obj_name = obj_name_el.text
            if obj_name in (
                "Header_Bg", "Header_Title", "Header_Operator_Label", "Header_Operator_Field", "Header_Logout_Btn",
                "Footer_Bg", "Footer_Home_Btn", "Footer_SCADA_Btn",
                "Header_Alert_TT32", "Header_Alert_TX35", "AI_AlarmView"
            ):
                to_remove.append(item)

for item in to_remove:
    object_list.remove(item)
    print(f"Removed old element: {item.tag}")

# Create Header and Footer directly into Screen_2
create_header_footer_items(object_list, "MÀN HÌNH CHÍNH - HỆ THỐNG CÔNG NGHỆ SCADA")

# Write output XML
tree.write(output_xml, encoding="utf-8", xml_declaration=True)
print("[SUCCESS] Patched Hmi.Screen.Screen_2.xml saved successfully!")
