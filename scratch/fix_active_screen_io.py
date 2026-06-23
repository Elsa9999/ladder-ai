# -*- coding: utf-8 -*-
"""
fix_active_screen_io.py
Mục đích: Vá file active_screen_2_export.xml (trạng thái hiện tại sau khi user chỉnh tay),
  - Bind tag HMI đúng vào mỗi IO Field
  - Sửa FormatPattern, HorizontalAlignment=Center, VerticalAlignment=Middle
  - Xóa và tạo lại Unit Label đúng (8px offset, Arial 13 Bold)
  - Giữ nguyên tất cả vị trí (Left/Top) user đã chỉnh
  - Kết quả xuất ra: hmi_export/Screens/Hmi.Screen.Screen_2.xml
"""
import xml.etree.ElementTree as ET
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# =========================================================
# ĐƯỜNG DẪN
# =========================================================
# Dùng file export active hiện tại từ TIA Portal làm nguồn
input_xml  = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\active_screen_2_export.xml"
output_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens"
output_xml = os.path.join(output_dir, "Hmi.Screen.Screen_2.xml")

if not os.path.exists(input_xml):
    print(f"[ERROR] Source XML not found: {input_xml}")
    sys.exit(1)

os.makedirs(output_dir, exist_ok=True)

# =========================================================
# MAPPING IO FIELD -> (TAG HMI, ĐƠN VỊ, FORMAT)
# 8 trường trong màn hình active: 1,2,3,4,5,6,7,8
# Layout bảng 4 cột x 2 hàng dựa vào tọa độ:
#   Col1 (~X=114-117): field_1(row1) + field_3(row2)
#   Col2 (~X=407-408): field_2(row1) + field_4(row2)
#   Col3 (~X=647-653): field_5(row1) + field_6(row2)
#   Col4 (~X=913):     field_7(row1) + field_8(row2)
# =========================================================
FIELD_MAPPINGS = {
    "I/O field_1": ("1400_TT32_PV",    "°C",  "99.9"),   # Nhiệt độ lò 1
    "I/O field_2": ("1400_FS51_PV",    "Hz",  "99.9"),   # Tần số bơm 1
    "I/O field_3": ("1400_LGFE01_PV",  "%",   "999.9"),  # Lưu lượng 1
    "I/O field_4": ("1406_TX35_PV",    "°C",  "99.9"),   # Nhiệt độ cảm biến TX35
    "I/O field_5": ("1400_FT101_PV",   "Bar", "999.9"),  # Áp suất FT101
    "I/O field_6": ("1400_FY301_PV",   "%",   "999.9"),  # % điều chỉnh FY301
    "I/O field_7": ("1400_FT115_PV",   "°C",  "999.9"),  # Nhiệt độ FT115
    "I/O field_8": ("1400_TT64_PV",    "°C",  "99.9"),   # Nhiệt độ TT64
}

# =========================================================
# ANIMATION RANGES (màu cảnh báo)
# =========================================================
ANIMATIONS = {
    "I/O field_1": ("1400_TT32_PV", [
        (0,  74, "255, 255, 255", "0, 0, 0",   "No"),
        (75, 77, "245, 158, 11",  "0, 0, 0",   "No"),
        (78, 150,"220, 38, 38",   "255, 255, 255","Fast"),
    ]),
    "I/O field_4": ("1406_TX35_PV", [
        (0, 6,  "255, 255, 255", "0, 0, 0",   "No"),
        (7, 7,  "245, 158, 11",  "0, 0, 0",   "No"),
        (8, 15, "220, 38, 38",   "255, 255, 255","Fast"),
    ]),
}

# =========================================================
# PARSE XML
# =========================================================
ET.register_namespace('', '')
tree = ET.parse(input_xml)
root = tree.getroot()

# Tìm max ID hiện tại để tránh xung đột
max_id = 0
for elem in root.iter():
    id_attr = elem.get("ID")
    if id_attr:
        try:
            val = int(id_attr, 16)
            if val > max_id:
                max_id = val
        except ValueError:
            pass

id_counter = max_id + 1000
print(f"Max ID hex={hex(max_id)}, counter starts at {hex(id_counter)}")

def get_next_id():
    global id_counter
    res = hex(id_counter)[2:].upper()
    id_counter += 1
    return res

# =========================================================
# HÀM TẠO XML NODES
# =========================================================
def create_font(parent, family="Arial", size=13, bold=True):
    font = ET.SubElement(parent, "Hmi.Globalization.MultiLingualFont", {
        "ID": get_next_id(), "CompositionName": "Font"})
    fobjs = ET.SubElement(font, "ObjectList")
    fitem = ET.SubElement(fobjs, "Hmi.Globalization.FontItem", {
        "ID": get_next_id(), "CompositionName": "Items"})
    fattrs = ET.SubElement(fitem, "AttributeList")
    ET.SubElement(fattrs, "Culture").text = "en-US"
    ET.SubElement(fattrs, "FontFamily").text = family
    ET.SubElement(fattrs, "FontSize").text = str(size)
    ET.SubElement(fattrs, "FontStyle").text = "Bold" if bold else "Regular"
    return font

def create_multilingual_text(parent, comp_name, text_val):
    txt = ET.SubElement(parent, "MultilingualText", {
        "ID": get_next_id(), "CompositionName": comp_name})
    tobjs = ET.SubElement(txt, "ObjectList")
    titem = ET.SubElement(tobjs, "MultilingualTextItem", {
        "ID": get_next_id(), "CompositionName": "Items"})
    tattrs = ET.SubElement(titem, "AttributeList")
    ET.SubElement(tattrs, "Culture").text = "en-US"
    ET.SubElement(tattrs, "Text").text = f"<body><p>{text_val}</p></body>"
    return txt

def bind_tag_to_iofield(iofield_el, tag_name):
    """Gắn tag_name vào ProcessValue của IOField"""
    objs = iofield_el.find("ObjectList")
    if objs is None:
        objs = ET.SubElement(iofield_el, "ObjectList")

    # Tìm property ProcessValue
    prop_val = None
    for p in objs:
        if p.tag.endswith("Property"):
            n = p.find("AttributeList/Name")
            if n is not None and n.text == "ProcessValue":
                prop_val = p
                break

    if prop_val is None:
        prop_val = ET.SubElement(objs, "Hmi.Screen.Property", {
            "ID": get_next_id(), "CompositionName": "Properties"})
        pa = ET.SubElement(prop_val, "AttributeList")
        ET.SubElement(pa, "Name").text = "ProcessValue"

    pobjs = prop_val.find("ObjectList")
    if pobjs is None:
        pobjs = ET.SubElement(prop_val, "ObjectList")

    # Xóa tag connection cũ nếu có
    for tc in list(pobjs):
        if "TagConnectionDynamic" in tc.tag:
            pobjs.remove(tc)

    # Tạo mới
    conn = ET.SubElement(pobjs, "Hmi.Dynamic.TagConnectionDynamic", {
        "ID": get_next_id(), "CompositionName": "Dynamic"})
    cattr = ET.SubElement(conn, "AttributeList")
    ET.SubElement(cattr, "Indirect").text = "false"
    links = ET.SubElement(conn, "LinkList")
    tag_el = ET.SubElement(links, "Tag", {"TargetID": "@OpenLink"})
    ET.SubElement(tag_el, "Name").text = tag_name

def add_appearance_animation(element, tag_name, limits_ranges):
    objs = element.find("ObjectList")
    if objs is None:
        objs = ET.SubElement(element, "ObjectList")

    # Xóa animation cũ
    for item in list(objs):
        if "RangeAppearanceAnimation" in item.tag:
            objs.remove(item)

    anim = ET.SubElement(objs, "Hmi.Dynamic.RangeAppearanceAnimation", {
        "ID": get_next_id(), "CompositionName": "Animations"})
    aattrs = ET.SubElement(anim, "AttributeList")
    ET.SubElement(aattrs, "Name").text = "RangeAppearanceAnimation"
    aobjs = ET.SubElement(anim, "ObjectList")

    trigger = ET.SubElement(aobjs, "Hmi.Dynamic.TagElementTrigger", {
        "ID": get_next_id(), "CompositionName": "RangeTag"})
    tlinks = ET.SubElement(trigger, "LinkList")
    tv = ET.SubElement(tlinks, "Tag", {"TargetID": "@OpenLink"})
    ET.SubElement(tv, "Name").text = tag_name

    for low, high, bg_color, fg_color, flashing in limits_ranges:
        r = ET.SubElement(aobjs, "Hmi.Dynamic.Range", {
            "ID": get_next_id(), "CompositionName": "RangeValues"})
        rattrs = ET.SubElement(r, "AttributeList")
        ET.SubElement(rattrs, "BackColor").text = bg_color
        ET.SubElement(rattrs, "FlashingType").text = flashing
        ET.SubElement(rattrs, "ForeColor").text = fg_color
        ET.SubElement(rattrs, "LowerLimit").text = str(int(low))
        ET.SubElement(rattrs, "UpperLimit").text = str(int(high))

# =========================================================
# XỬ LÝ LAYER VÀ OBJECT LIST
# =========================================================
layer = root.find(".//Hmi.Screen.ScreenLayer")
if layer is None:
    print("[ERROR] Layer not found!")
    sys.exit(1)

object_list = layer.find("ObjectList")
if object_list is None:
    print("[ERROR] ObjectList not found!")
    sys.exit(1)

# =========================================================
# BƯỚC 1: Patch tất cả IO Fields - tag, format, alignment
# =========================================================
print("\n[Bước 1] Patch IO Fields...")
io_coords = {}  # lưu lại coords để tạo unit label sau

for item in object_list:
    if not item.tag.endswith("IOField"):
        continue
    attrs = item.find("AttributeList")
    if attrs is None:
        continue
    name_el = attrs.find("ObjectName")
    if name_el is None:
        continue
    obj_name = name_el.text

    if obj_name not in FIELD_MAPPINGS:
        print(f"  SKIP (không có mapping): {obj_name}")
        continue

    tag_name, unit_val, fmt = FIELD_MAPPINGS[obj_name]
    left = int(attrs.find("Left").text)
    top  = int(attrs.find("Top").text)
    w    = int(attrs.find("Width").text)
    h    = int(attrs.find("Height").text)
    io_coords[obj_name] = (left, top, w, h, unit_val)

    # FormatPattern
    fp = attrs.find("FormatPattern")
    if fp is not None: fp.text = fmt
    else: ET.SubElement(attrs, "FormatPattern").text = fmt

    # HorizontalAlignment
    ha = attrs.find("HorizontalAlignment")
    if ha is not None: ha.text = "Center"
    else: ET.SubElement(attrs, "HorizontalAlignment").text = "Center"

    # VerticalAlignment
    va = attrs.find("VerticalAlignment")
    if va is not None: va.text = "Middle"
    else: ET.SubElement(attrs, "VerticalAlignment").text = "Middle"

    # Bind tag
    bind_tag_to_iofield(item, tag_name)

    # Animation cảnh báo
    if obj_name in ANIMATIONS:
        anim_tag, anim_ranges = ANIMATIONS[obj_name]
        add_appearance_animation(item, anim_tag, anim_ranges)
        print(f"  {obj_name} → {tag_name} [{fmt}] {unit_val} + animation")
    else:
        print(f"  {obj_name} → {tag_name} [{fmt}] {unit_val}")

# =========================================================
# BƯỚC 2: Xóa unit labels cũ
# =========================================================
print("\n[Bước 2] Xóa unit labels cũ...")
to_remove = []
for item in object_list:
    if item.tag.endswith("TextField"):
        n = item.find("AttributeList/ObjectName")
        if n is not None and n.text and n.text.startswith("Text_field_Unit_"):
            to_remove.append(item)
for item in to_remove:
    object_list.remove(item)
    print(f"  Removed: {item.find('AttributeList/ObjectName').text}")

# =========================================================
# BƯỚC 3: Tạo lại unit labels đúng vị trí
# =========================================================
print("\n[Bước 3] Tạo lại unit labels...")
for obj_name, (left, top, w, h, unit_val) in io_coords.items():
    tf_left = left + w + 8
    tf_top  = top
    tf_name = f"Text_field_Unit_{obj_name}"

    unit_tf = ET.SubElement(object_list, "Hmi.Screen.TextField", {
        "ID": get_next_id(), "CompositionName": "ScreenItems"})

    uta = ET.SubElement(unit_tf, "AttributeList")
    ET.SubElement(uta, "BackColor").text = "255, 255, 255"
    ET.SubElement(uta, "BackFillStyle").text = "Transparent"
    ET.SubElement(uta, "BorderWidth").text = "0"
    ET.SubElement(uta, "ForeColor").text = "0, 0, 0"
    ET.SubElement(uta, "Height").text = str(h)
    ET.SubElement(uta, "HorizontalAlignment").text = "Left"
    ET.SubElement(uta, "Left").text = str(tf_left)
    ET.SubElement(uta, "ObjectName").text = tf_name
    ET.SubElement(uta, "Top").text = str(tf_top)
    ET.SubElement(uta, "VerticalAlignment").text = "Middle"
    ET.SubElement(uta, "Width").text = "55"

    link_list = ET.SubElement(unit_tf, "LinkList")
    style_item = ET.SubElement(link_list, "StyleItem", {"TargetID": "@OpenLink"})
    ET.SubElement(style_item, "Name").text = "Text field"

    utobjs = ET.SubElement(unit_tf, "ObjectList")
    create_font(utobjs, family="Arial", size=13, bold=True)

    ml_text = ET.SubElement(utobjs, "MultilingualText", {
        "ID": get_next_id(), "CompositionName": "Text"})
    ml_objs = ET.SubElement(ml_text, "ObjectList")
    ml_item = ET.SubElement(ml_objs, "MultilingualTextItem", {
        "ID": get_next_id(), "CompositionName": "Items"})
    item_attrs = ET.SubElement(ml_item, "AttributeList")
    ET.SubElement(item_attrs, "Culture").text = "en-US"
    ET.SubElement(item_attrs, "Text").text = f"<body><p>{unit_val}</p></body>"

    print(f"  Unit '{unit_val}' tại ({tf_left},{tf_top}) cho {obj_name}")

# =========================================================
# BƯỚC 4: Sửa background graphic link (nếu cần)
# =========================================================
print("\n[Bước 4] Kiểm tra background graphic link...")
for elem in root.iter():
    if elem.tag.endswith("GraphicView"):
        obj_name_el = elem.find("AttributeList/ObjectName")
        if obj_name_el is not None and obj_name_el.text == "Graphic view_1":
            pic = elem.find("LinkList/Picture/Name")
            if pic is not None:
                old_link = pic.text
                if old_link != "9e382997-af09-41cf-ab1c-3299fad62071":
                    pic.text = "9e382997-af09-41cf-ab1c-3299fad62071"
                    print(f"  Đã cập nhật link background từ '{old_link}' → '9e382997-af09-41cf-ab1c-3299fad62071'")
                else:
                    print(f"  Background link đúng rồi: {old_link}")

# =========================================================
# BƯỚC 5: Sửa Width màn hình (1980 → 1920 nếu cần)
# =========================================================
print("\n[Bước 5] Kiểm tra screen dimensions...")
for elem in root.iter():
    if "Screen" in elem.tag and elem.find("AttributeList/Name") is not None:
        name_el = elem.find("AttributeList/Name")
        if name_el is not None and name_el.text == "Screen_2":
            w_el = elem.find("AttributeList/Width")
            h_el = elem.find("AttributeList/Height")
            if w_el is not None:
                if w_el.text != "1920":
                    print(f"  Sửa Width {w_el.text} → 1920")
                    w_el.text = "1920"
                else:
                    print(f"  Width đã đúng: 1920")
            if h_el is not None:
                print(f"  Height: {h_el.text}")

# =========================================================
# XUẤT FILE
# =========================================================
tree.write(output_xml, encoding="utf-8", xml_declaration=True)
print(f"\n[SUCCESS] Đã xuất file vá sang: {output_xml}")
print(f"  Kích thước: {os.path.getsize(output_xml):,} bytes")
print("\nBước tiếp theo: Chạy Ladder\\import_screen_only.exe để nạp vào TIA Portal!")
