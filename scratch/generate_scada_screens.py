# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os

output_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens"
os.makedirs(output_dir, exist_ok=True)

id_counter = 40960 # 0xA000
def get_next_id():
    global id_counter
    res = hex(id_counter)[2:].upper()
    id_counter += 1
    return res

def create_multilingual_text(parent, comp_name, text_val, id_val=None):
    if not id_val:
        id_val = get_next_id()
    txt = ET.SubElement(parent, "MultilingualText", {
        "ID": id_val,
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
    
    # Tag Trigger
    trigger = ET.SubElement(anim_objs, "Hmi.Dynamic.TagElementTrigger", {
        "ID": get_next_id(),
        "CompositionName": "VisibilityTag"
    })
    trigger_links = ET.SubElement(trigger, "LinkList")
    val = ET.SubElement(trigger_links, "Tag", {"TargetID": "@OpenLink"})
    ET.SubElement(val, "Name").text = tag_name

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

    # 3. Header Logged_In Text Label
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

    # 4. Header Logged_In IOField (Output mode)
    op_field = ET.SubElement(object_list, "Hmi.Screen.IOField", {
        "ID": get_next_id(),
        "CompositionName": "ScreenItems"
    })
    of_attrs = ET.SubElement(op_field, "AttributeList")
    ET.SubElement(of_attrs, "BackColor").text = "30, 41, 59"
    ET.SubElement(of_attrs, "BackFillStyle").text = "Solid"
    ET.SubElement(of_attrs, "BorderColor").text = "71, 85, 105"
    ET.SubElement(of_attrs, "BorderWidth").text = "1"
    ET.SubElement(of_attrs, "ForeColor").text = "34, 197, 94" # Green value text
    ET.SubElement(of_attrs, "Height").text = "40"
    ET.SubElement(of_attrs, "HorizontalAlignment").text = "Center"
    ET.SubElement(of_attrs, "Left").text = "1410"
    ET.SubElement(of_attrs, "Mode").text = "Output"
    ET.SubElement(of_attrs, "ObjectName").text = "Header_Operator_Field"
    ET.SubElement(of_attrs, "Top").text = "30"
    ET.SubElement(of_attrs, "VerticalAlignment").text = "Middle"
    ET.SubElement(of_attrs, "Width").text = "120"
    of_objs = ET.SubElement(op_field, "ObjectList")
    create_font(of_objs, size=16, bold=True)
    create_multilingual_text(of_objs, "HelpText", "")
    
    # ProcessValue tag connection
    prop = ET.SubElement(of_objs, "Hmi.Screen.Property", {
        "ID": get_next_id(),
        "CompositionName": "Properties"
    })
    ET.SubElement(prop, "AttributeList").append(ET.Element("Name"))
    prop.find("AttributeList/Name").text = "ProcessValue"
    prop_objs = ET.SubElement(prop, "ObjectList")
    conn = ET.SubElement(prop_objs, "Hmi.Dynamic.TagConnectionDynamic", {
        "ID": get_next_id(),
        "CompositionName": "Dynamic"
    })
    ET.SubElement(conn, "AttributeList").append(ET.Element("Indirect"))
    conn.find("AttributeList/Indirect").text = "false"
    conn_links = ET.SubElement(conn, "LinkList")
    val_tag = ET.SubElement(conn_links, "Tag", {"TargetID": "@OpenLink"})
    ET.SubElement(val_tag, "Name").text = "Logged_In"

    # 5. Header Logout Button (Calls Logoff)
    logout_btn = create_btn_xml(object_list, "Header_Logout_Btn", "ĐĂNG XUẤT", 1550, 25, 150, 50, "Logoff", back_color="75, 85, 99", border_color="107, 114, 128")

    # 6. Footer background bar (y: 980 to 1080)
    footer = ET.SubElement(object_list, "Hmi.Screen.Rectangle", {
        "ID": get_next_id(),
        "CompositionName": "ScreenItems"
    })
    f_attrs = ET.SubElement(footer, "AttributeList")
    ET.SubElement(f_attrs, "BackColor").text = "15, 23, 42" # Dark slate
    ET.SubElement(f_attrs, "BackFillStyle").text = "Solid"
    ET.SubElement(f_attrs, "BorderColor").text = "51, 65, 85"
    ET.SubElement(f_attrs, "BorderWidth").text = "1"
    ET.SubElement(f_attrs, "Height").text = "100"
    ET.SubElement(f_attrs, "Left").text = "0"
    ET.SubElement(f_attrs, "ObjectName").text = "Footer_Bg"
    ET.SubElement(f_attrs, "Top").text = "980"
    ET.SubElement(f_attrs, "Width").text = "1920"

    # 7. Navigation Buttons
    # Home (Always visible)
    btn_home = create_btn_xml(object_list, "Footer_Home_Btn", "MÀN HÌNH ĐĂNG NHẬP / HOME", 100, 995, 350, 70, "ActivateScreen", navigation_target="Login/out", back_color="30, 41, 59", border_color="71, 85, 105")
    
    # Menu (Only visible when logged in)
    btn_menu = create_btn_xml(object_list, "Footer_Menu_Btn", "BẢNG ĐIỀU KHIỂN CHÍNH (MENU)", 550, 995, 380, 70, "ActivateScreen", navigation_target="Menu_Lựa_chọn", back_color="51, 65, 85", border_color="71, 85, 105")
    add_visibility_animation(btn_menu)
    
    # SCADA Technology (Only visible when logged in)
    btn_scada = create_btn_xml(object_list, "Footer_SCADA_Btn", "MÀN HÌNH CÔNG NGHỆ (SCADA)", 1030, 995, 380, 70, "ActivateScreen", navigation_target="Screen_2", back_color="16, 185, 129", border_color="52, 211, 153")
    add_visibility_animation(btn_scada)
    
    # Alarms (Only visible when logged in)
    btn_alarms = create_btn_xml(object_list, "Footer_Alarms_Btn", "HỆ THỐNG CẢNH BÁO (ALARMS)", 1510, 995, 350, 70, "ActivateScreen", navigation_target="Alarms", back_color="239, 68, 68", border_color="248, 113, 113")
    add_visibility_animation(btn_alarms)


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


# ==========================================
# 1. GENERATE Menu_Lựa_chọn Screen
# ==========================================
def generate_menu_screen():
    root = ET.Element("Document")
    ET.SubElement(root, "Engineering", {"version": "V18"})
    doc_info = ET.SubElement(root, "DocumentInfo")
    ET.SubElement(doc_info, "Created").text = "2026-06-11T12:00:00Z"
    ET.SubElement(doc_info, "ExportSetting").text = "WithDefaults"
    
    screen = ET.SubElement(root, "Hmi.Screen.Screen", {"ID": "0"})
    attrs = ET.SubElement(screen, "AttributeList")
    ET.SubElement(attrs, "ActiveLayer").text = "0"
    ET.SubElement(attrs, "BackColor").text = "30, 41, 59" # Slate 800 background
    ET.SubElement(attrs, "Height").text = "1080"
    ET.SubElement(attrs, "Name").text = "Menu_Lựa_chọn"
    ET.SubElement(attrs, "Number").text = "3"
    ET.SubElement(attrs, "Visible").text = "true"
    ET.SubElement(attrs, "Width").text = "1920"
    
    objs = ET.SubElement(screen, "ObjectList")
    create_multilingual_text(objs, "HelpText", "")
    
    # Layer
    layer = ET.SubElement(objs, "Hmi.Screen.ScreenLayer", {"ID": "3", "CompositionName": "Layers"})
    layer_attrs = ET.SubElement(layer, "AttributeList")
    ET.SubElement(layer_attrs, "Index").text = "0"
    ET.SubElement(layer_attrs, "VisibleES").text = "true"
    
    layer_objs = ET.SubElement(layer, "ObjectList")
    
    # Create Header & Footer elements
    create_header_footer_items(layer_objs, "BẢNG ĐIỀU KHIỂN VÀ LỰA CHỌN BÀI THI SCADA")
    
    # 8-screen buttons layout coordinates (2 rows, 4 columns)
    # Row 1 at Y = 360, Row 2 at Y = 580
    # X coordinates: 200, 600, 1000, 1400. Width: 320, Height: 120
    buttons_data = [
        # Text, Target Screen
        ("BÀI 1: BỒN TRỘN NƯỚC TƯƠNG", "Screen_2", 200, 360),
        ("BÀI 2: ĐIỀU KHIỂN NHIỆT ĐỘ", "Screen_2", 600, 360),
        ("BÀI 3: GIÁM SÁT ÁP SUẤT", "Screen_2", 1000, 360),
        ("BÀI 4: ĐIỀU KHIỂN TẦN SỐ", "Screen_2", 1400, 360),
        ("BÀI 5: HỆ THỐNG CẢNH BÁO", "Alarms", 200, 580),
        ("BÀI 6: MÔ PHỎNG PLC", "Screen_2", 600, 580),
        ("BÀI 7: TRUYỀN THÔNG MODBUS", "Screen_2", 1000, 580),
        ("BÀI 8: TRẠM GIÁM SÁT RTU", "Screen_2", 1400, 580)
    ]
    
    for i, data in enumerate(buttons_data):
        text, target, x, y = data
        btn = create_btn_xml(layer_objs, f"Menu_Btn_{i+1}", text, x, y, 320, 120, "ActivateScreen", navigation_target=target, back_color="30, 41, 59", border_color="71, 85, 105")
        add_visibility_animation(btn)
        
    # Unlogged warning message
    warn = ET.SubElement(layer_objs, "Hmi.Screen.TextField", {
        "ID": get_next_id(),
        "CompositionName": "ScreenItems"
    })
    w_attrs = ET.SubElement(warn, "AttributeList")
    ET.SubElement(w_attrs, "BackFillStyle").text = "Transparent"
    ET.SubElement(w_attrs, "BorderWidth").text = "0"
    ET.SubElement(w_attrs, "ForeColor").text = "239, 68, 68" # Red warning
    ET.SubElement(w_attrs, "Height").text = "100"
    ET.SubElement(w_attrs, "HorizontalAlignment").text = "Center"
    ET.SubElement(w_attrs, "Left").text = "360"
    ET.SubElement(w_attrs, "ObjectName").text = "Menu_Unlogged_Warning"
    ET.SubElement(w_attrs, "Top").text = "480"
    ET.SubElement(w_attrs, "VerticalAlignment").text = "Middle"
    ET.SubElement(w_attrs, "Width").text = "1200"
    w_objs = ET.SubElement(warn, "ObjectList")
    create_font(w_objs, size=32, bold=True)
    create_multilingual_text(w_objs, "Text", "VUI LÒNG ĐĂNG NHẬP ĐỂ SỬ DỤNG HỆ THỐNG!")
    add_visibility_animation(warn, min_val=0, max_val=0) # Visible ONLY when Logged_In = 0
    
    # Save file
    file_path = os.path.join(output_dir, "Hmi.Screen.Menu_Lựa_chọn.xml")
    tree = ET.ElementTree(root)
    tree.write(file_path, encoding="utf-8", xml_declaration=True)
    print("[SUCCESS] Generated Menu_Lua_Chon screen XML")


# ==========================================
# 2. GENERATE Alarms Screen
# ==========================================
def generate_alarms_screen():
    root = ET.Element("Document")
    ET.SubElement(root, "Engineering", {"version": "V18"})
    doc_info = ET.SubElement(root, "DocumentInfo")
    ET.SubElement(doc_info, "Created").text = "2026-06-11T12:00:00Z"
    ET.SubElement(doc_info, "ExportSetting").text = "WithDefaults"
    
    screen = ET.SubElement(root, "Hmi.Screen.Screen", {"ID": "0"})
    attrs = ET.SubElement(screen, "AttributeList")
    ET.SubElement(attrs, "ActiveLayer").text = "0"
    ET.SubElement(attrs, "BackColor").text = "30, 41, 59" # Slate 800 background
    ET.SubElement(attrs, "Height").text = "1080"
    ET.SubElement(attrs, "Name").text = "Alarms"
    ET.SubElement(attrs, "Number").text = "4"
    ET.SubElement(attrs, "Visible").text = "true"
    ET.SubElement(attrs, "Width").text = "1920"
    
    objs = ET.SubElement(screen, "ObjectList")
    create_multilingual_text(objs, "HelpText", "")
    
    # Layer
    layer = ET.SubElement(objs, "Hmi.Screen.ScreenLayer", {"ID": "3", "CompositionName": "Layers"})
    layer_attrs = ET.SubElement(layer, "AttributeList")
    ET.SubElement(layer_attrs, "Index").text = "0"
    ET.SubElement(layer_attrs, "VisibleES").text = "true"
    
    layer_objs = ET.SubElement(layer, "ObjectList")
    
    # Create Header & Footer elements
    create_header_footer_items(layer_objs, "HỆ THỐNG CẢNH BÁO BÁO ĐỘNG (ALARMS)")
    
    # Note: Alarm view control is not supported by TIA Openness XML import.
    # The user will drag and drop the "Alarm view" control manually in TIA Portal.
    
    # Unlogged warning message
    warn = ET.SubElement(layer_objs, "Hmi.Screen.TextField", {
        "ID": get_next_id(),
        "CompositionName": "ScreenItems"
    })
    w_attrs = ET.SubElement(warn, "AttributeList")
    ET.SubElement(w_attrs, "BackFillStyle").text = "Transparent"
    ET.SubElement(w_attrs, "BorderWidth").text = "0"
    ET.SubElement(w_attrs, "ForeColor").text = "239, 68, 68"
    ET.SubElement(w_attrs, "Height").text = "100"
    ET.SubElement(w_attrs, "HorizontalAlignment").text = "Center"
    ET.SubElement(w_attrs, "Left").text = "360"
    ET.SubElement(w_attrs, "ObjectName").text = "Alarms_Unlogged_Warning"
    ET.SubElement(w_attrs, "Top").text = "480"
    ET.SubElement(w_attrs, "VerticalAlignment").text = "Middle"
    ET.SubElement(w_attrs, "Width").text = "1200"
    w_objs = ET.SubElement(warn, "ObjectList")
    create_font(w_objs, size=32, bold=True)
    create_multilingual_text(w_objs, "Text", "VUI LÒNG ĐĂNG NHẬP ĐỂ XEM BẢNG CẢNH BÁO!")
    add_visibility_animation(warn, min_val=0, max_val=0) # Visible ONLY when Logged_In = 0
    
    # Save file
    file_path = os.path.join(output_dir, "Hmi.Screen.Alarms.xml")
    tree = ET.ElementTree(root)
    tree.write(file_path, encoding="utf-8", xml_declaration=True)
    print("[SUCCESS] Generated Alarms screen XML")

if __name__ == "__main__":
    generate_menu_screen()
    generate_alarms_screen()
