# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Đường dẫn
INPUT_XML = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Man Tong Quan.xml"
BACKUP_XML = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Man Tong Quan.xml.bak"
REPORT_PATH = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\man_tong_quan_mapping_report.md"
TAGS_XML_PATH = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\AI_HMI_Tags.xml"

# Backup file gốc nếu chưa có backup
if not os.path.exists(BACKUP_XML):
    shutil.copyfile(INPUT_XML, BACKUP_XML)
    print(f"Created backup at: {BACKUP_XML}")

# Đọc XML
ET.register_namespace('', '')
tree = ET.parse(INPUT_XML)
root = tree.getroot()

# Tìm ScreenLayer và ObjectList
layer = root.find(".//Hmi.Screen.ScreenLayer")
if layer is None:
    print("[ERROR] ScreenLayer not found!")
    sys.exit(1)
object_list = layer.find("ObjectList")
if object_list is None:
    print("[ERROR] ObjectList not found!")
    sys.exit(1)

# Tự sinh ID tiếp theo
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

id_counter = max_id + 5000
print(f"Max ID in XML = {hex(max_id)}, starting counter = {hex(id_counter)}")

def next_id():
    global id_counter
    r = hex(id_counter)[2:].upper()
    id_counter += 1
    return r

# 1. Dọn dẹp các phần tử do AI sinh ra ở phiên trước để đảm bảo tính lặp lại (Idempotency)
removed_count = 0
for elem in list(object_list):
    attrs = elem.find("AttributeList")
    if attrs is not None:
        name_el = attrs.find("ObjectName")
        if name_el is not None and name_el.text and name_el.text.startswith("AI_"):
            object_list.remove(elem)
            removed_count += 1
if removed_count > 0:
    print(f"Cleaned up {removed_count} previously generated HMI elements.")

# 2. Dọn dẹp 2 ô mẫu gốc (I/O field_1 và I/O field_2) để tránh chồng lấn với ô AI mới sinh
removed_original = 0
for elem in list(object_list):
    tag_local = elem.tag.split('}')[-1]
    if tag_local == "IOField":
        attrs = elem.find("AttributeList")
        if attrs is not None:
            obj_name = attrs.find("ObjectName")
            if obj_name is not None and obj_name.text in ["I/O field_1", "I/O field_2"]:
                object_list.remove(elem)
                removed_original += 1
                print(f"Removed original template element: {obj_name.text}")

# ============================================================
# CẤU HÌNH MAPPING CHO 41 GRAPHIC IO FIELD
# ============================================================
graphic_io_field_mappings = {
    # Mức dịch 4 bồn trộn và 2 bồn chứa
    "Graphic I/O field_10": "HMI_Anim_Bon1_MucDich",       # Bồn 1
    "Graphic I/O field_3": "HMI_Anim_Bon2_MucDich",        # Bồn 2
    "Graphic I/O field_4": "HMI_Anim_Bon4_MucDich",        # Bồn 4
    "Graphic I/O field_6": "HMI_Anim_Bon3_MucDich",        # Bồn 3
    "Graphic I/O field_9": "HMI_Anim_BonChua1_MucDich",    # Bồn chứa 1
    "Graphic I/O field_2": "HMI_Anim_BonChua2_MucDich",    # Bồn chứa 2

    # Cánh khuấy 4 bồn trộn
    "Graphic I/O field_38": "HMI_Anim_Bon1_Frame",
    "Graphic I/O field_39": "HMI_Anim_Bon2_Frame",
    "Graphic I/O field_40": "HMI_Anim_Bon4_Frame",
    "Graphic I/O field_41": "HMI_Anim_Bon3_Frame",

    # Van cấp nước 4 bồn trộn (Inlet Valves)
    "Graphic I/O field_5": "V3230_Nuoc_Bon1_M",
    "Graphic I/O field_12": "V3235_Nuoc_Bon2_M",
    "Graphic I/O field_13": "V3245_Nuoc_Bon4_M",
    "Graphic I/O field_14": "V3240_Nuoc_Bon3_M",

    # Van xả đáy Bồn 1 (Draining Valves)
    "Graphic I/O field_8": "V3232_Xa_Bon1_M",
    "Graphic I/O field_11": "V3233_Xa_Bon1_M",
    "Graphic I/O field_7": "V3234_Xa_Bon1_M",

    # Van xả đáy Bồn 2
    "Graphic I/O field_15": "V3237_Xa_Bon2_M",
    "Graphic I/O field_16": "V3238_Xa_Bon2_M",
    "Graphic I/O field_17": "V3239_Xa_Bon2_M",

    # Van xả đáy Bồn 4
    "Graphic I/O field_18": "V3247_Xa_Bon4_M",
    "Graphic I/O field_20": "V3248_Xa_Bon4_M",
    "Graphic I/O field_22": "V3249_Xa_Bon4_M",

    # Van xả đáy Bồn 3
    "Graphic I/O field_19": "V3242_Xa_Bon3_M",
    "Graphic I/O field_21": "V3243_Xa_Bon3_M",
    "Graphic I/O field_23": "V3244_Xa_Bon3_M",

    # Bơm chuyển dịch Nhánh 1 & 2
    "Graphic I/O field_33": "Pump3264_Chuyen_Nhanh1_M",
    "Graphic I/O field_37": "Pump3265_Chuyen_Nhanh2_M",

    # Van xả/điều hướng Bồn chứa 1
    "Graphic I/O field_24": "V3331_Xa_BonChua1_M",
    "Graphic I/O field_30": "V3332_Xa_BonChua1_M",
    "Graphic I/O field_25": "V3333_DieuHuong_BonChua1_M",
    "Graphic I/O field_26": "V3334_DieuHuong_BonChua1_M",
    "Graphic I/O field_27": "V3335_DieuHuong_BonChua1_M",

    # Bơm Bồn chứa 1
    "Graphic I/O field_34": "Pump3361_LuanChuyen_BonChua1_M",
    "Graphic I/O field_1": "Pump3362_Xa_BonChua1_M",

    # Van xả Bồn chứa 2
    "Graphic I/O field_28": "V3338_Xa_BonChua2_M",
    "Graphic I/O field_31": "V3339_Xa_BonChua2_M",

    # Bơm màng lọc CCP & Van đường ống
    "Graphic I/O field_35": "Pump3364_Filter_M",
    "Graphic I/O field_36": "Pump3365_Filter_M",
    "Graphic I/O field_29": "V3340_Duong_Filter_M",
    "Graphic I/O field_32": "V3341_Duong_Filter_M"
}

# Tên ký hiệu hiển thị cho 31 van và bơm đồ họa (Graphic IO Fields)
graphic_labels = {
    # Van cấp nước 4 bồn trộn
    "Graphic I/O field_5": "V32.30",
    "Graphic I/O field_12": "V32.35",
    "Graphic I/O field_13": "V32.45",
    "Graphic I/O field_14": "V32.40",

    # Van xả đáy Bồn 1
    "Graphic I/O field_8": "V32.32",
    "Graphic I/O field_11": "V32.33",
    "Graphic I/O field_7": "V32.34",

    # Van xả đáy Bồn 2
    "Graphic I/O field_15": "V32.37",
    "Graphic I/O field_16": "V32.38",
    "Graphic I/O field_17": "V32.39",

    # Van xả đáy Bồn 4
    "Graphic I/O field_18": "V32.47",
    "Graphic I/O field_20": "V32.48",
    "Graphic I/O field_22": "V32.49",

    # Van xả đáy Bồn 3
    "Graphic I/O field_19": "V32.42",
    "Graphic I/O field_21": "V32.43",
    "Graphic I/O field_23": "V32.44",

    # Bơm chuyển dịch
    "Graphic I/O field_33": "Pump 32.64",
    "Graphic I/O field_37": "Pump 32.69",

    # Van Bồn chứa 1
    "Graphic I/O field_24": "V33.31",
    "Graphic I/O field_30": "V33.32",
    "Graphic I/O field_25": "V33.33",
    "Graphic I/O field_26": "V33.34",
    "Graphic I/O field_27": "V33.35",

    # Bơm Bồn chứa 1
    "Graphic I/O field_34": "Pump 33.61",
    "Graphic I/O field_1": "Pump 33.62",

    # Van Bồn chứa 2
    "Graphic I/O field_28": "V33.38",
    "Graphic I/O field_31": "V33.39",

    # Bơm màng lọc CCP & Van đường ống
    "Graphic I/O field_35": "Pump 33.64",
    "Graphic I/O field_36": "Pump 33.65",
    "Graphic I/O field_29": "V33.40",
    "Graphic I/O field_32": "V33.41"
}

# ============================================================
# HÀM BỔ TRỢ TẠO XML ELEMENT
# ============================================================
def make_font(parent, family="Tahoma", size=13, bold=True):
    font = ET.SubElement(parent, "Hmi.Globalization.MultiLingualFont",
                         {"ID": next_id(), "CompositionName": "Font"})
    fobjs = ET.SubElement(font, "ObjectList")
    fitem = ET.SubElement(fobjs, "Hmi.Globalization.FontItem",
                           {"ID": next_id(), "CompositionName": "Items"})
    fattrs = ET.SubElement(fitem, "AttributeList")
    ET.SubElement(fattrs, "Culture").text = "en-US"
    ET.SubElement(fattrs, "FontFamily").text = family
    ET.SubElement(fattrs, "FontSize").text = str(size)
    ET.SubElement(fattrs, "FontStyle").text = "Bold" if bold else "Regular"

def bind_tag(iofield_el, tag_name):
    """Gắn tag vào ProcessValue của IO Field hoặc GraphicIOField"""
    objs = iofield_el.find("ObjectList")
    if objs is None:
        objs = ET.SubElement(iofield_el, "ObjectList")

    # Xóa property ProcessValue cũ
    for p in list(objs):
        if p.tag.endswith("Property"):
            n = p.find("AttributeList/Name")
            if n is not None and n.text == "ProcessValue":
                objs.remove(p)
                break

    # Xóa các animation cũ để tránh lỗi compile do tag cũ không tồn tại
    for p in list(objs):
        if p.tag.endswith("RangeAppearanceAnimation") or p.tag.endswith("AppearanceAnimation"):
            objs.remove(p)

    prop = ET.SubElement(objs, "Hmi.Screen.Property",
                         {"ID": next_id(), "CompositionName": "Properties"})
    pa = ET.SubElement(prop, "AttributeList")
    ET.SubElement(pa, "Name").text = "ProcessValue"
    pobjs = ET.SubElement(prop, "ObjectList")
    conn = ET.SubElement(pobjs, "Hmi.Dynamic.TagConnectionDynamic",
                         {"ID": next_id(), "CompositionName": "Dynamic"})
    ca = ET.SubElement(conn, "AttributeList")
    ET.SubElement(ca, "Indirect").text = "false"
    links = ET.SubElement(conn, "LinkList")
    t = ET.SubElement(links, "Tag", {"TargetID": "@OpenLink"})
    ET.SubElement(t, "Name").text = tag_name

def verify_boundaries(name, left, top, width, height):
    """Kiểm tra nếu phần tử vượt khỏi biên màn hình 1440x900"""
    if left < 0 or left + width > 1440 or top < 0 or top + height > 900:
        raise Exception(f"[BOUNDARY ERROR] Element '{name}' is out of screen boundary (1440x900)! "
                        f"Pos: ({left}, {top}), Size: {width}x{height}")

def create_text_field(name, text, left, top, width, height, font_size=13, align="Center"):
    """Tạo nhãn TextField tĩnh"""
    verify_boundaries(name, left, top, width, height)
    
    tf = ET.SubElement(object_list, "Hmi.Screen.TextField",
                       {"ID": next_id(), "CompositionName": "ScreenItems"})
    ta = ET.SubElement(tf, "AttributeList")
    ET.SubElement(ta, "BackFillStyle").text = "Transparent"
    ET.SubElement(ta, "BorderWidth").text = "0"
    ET.SubElement(ta, "ForeColor").text = "0, 0, 0"
    ET.SubElement(ta, "Height").text = str(height)
    ET.SubElement(ta, "HorizontalAlignment").text = align
    ET.SubElement(ta, "Left").text = str(left)
    ET.SubElement(ta, "ObjectName").text = name
    ET.SubElement(ta, "Top").text = str(top)
    ET.SubElement(ta, "VerticalAlignment").text = "Middle"
    ET.SubElement(ta, "Width").text = str(width)

    ll = ET.SubElement(tf, "LinkList")
    si = ET.SubElement(ll, "StyleItem", {"TargetID": "@OpenLink"})
    ET.SubElement(si, "Name").text = "Text field"

    tobjs = ET.SubElement(tf, "ObjectList")
    make_font(tobjs, "Tahoma", font_size, True)

    ml = ET.SubElement(tobjs, "MultilingualText",
                       {"ID": next_id(), "CompositionName": "Text"})
    mlobjs = ET.SubElement(ml, "ObjectList")
    mli = ET.SubElement(mlobjs, "MultilingualTextItem",
                         {"ID": next_id(), "CompositionName": "Items"})
    mlia = ET.SubElement(mli, "AttributeList")
    ET.SubElement(mlia, "Culture").text = "en-US"
    ET.SubElement(mlia, "Text").text = f"<body><p>{text}</p></body>"
    return tf

def create_numeric_io_field(name, tag_name, left, top, fmt_pattern):
    """Tạo ô hiển thị số thực (IO Field)"""
    verify_boundaries(name, left, top, 72, 26)
    
    io = ET.SubElement(object_list, "Hmi.Screen.IOField",
                       {"ID": next_id(), "CompositionName": "ScreenItems"})
    ia = ET.SubElement(io, "AttributeList")
    ET.SubElement(ia, "BackFillStyle").text = "Solid"
    ET.SubElement(ia, "BackColor").text = "255, 255, 255"
    ET.SubElement(ia, "BorderWidth").text = "1"
    ET.SubElement(ia, "ForeColor").text = "0, 0, 0"
    ET.SubElement(ia, "Height").text = "26"
    ET.SubElement(ia, "Width").text = "72"
    ET.SubElement(ia, "Left").text = str(left)
    ET.SubElement(ia, "Top").text = str(top)
    ET.SubElement(ia, "ObjectName").text = name
    ET.SubElement(ia, "HorizontalAlignment").text = "Center"
    ET.SubElement(ia, "VerticalAlignment").text = "Middle"
    ET.SubElement(ia, "FormatPattern").text = fmt_pattern
    ET.SubElement(ia, "Mode").text = "Output"

    ll = ET.SubElement(io, "LinkList")
    si = ET.SubElement(ll, "StyleItem", {"TargetID": "@OpenLink"})
    ET.SubElement(si, "Name").text = "I/O field"

    iobjs = ET.SubElement(io, "ObjectList")
    make_font(iobjs, "Tahoma", 14, True)
    
    bind_tag(io, tag_name)
    return io

# ============================================================
# BƯỚC 1: LIÊN KẾT 41 GRAPHIC IO FIELD
# ============================================================
print("[B1] Gán tag cho 41 GraphicIOFields...")
graphic_coords = {}
for elem in object_list:
    tag_local = elem.tag.split('}')[-1]
    if tag_local.endswith("GraphicIOField"):
        attrs = elem.find("AttributeList")
        obj_name = attrs.find("ObjectName").text
        left = int(attrs.find("Left").text)
        top = int(attrs.find("Top").text)
        w = int(attrs.find("Width").text)
        h = int(attrs.find("Height").text)
        graphic_coords[obj_name] = (left, top, w, h)
        
        if obj_name in graphic_io_field_mappings:
            tag_name = graphic_io_field_mappings[obj_name]
            bind_tag(elem, tag_name)
            print(f"  Bound {obj_name} to tag: {tag_name}")

# ============================================================
# BƯỚC 2: TỰ ĐỘNG SINH NHÃN KÝ HIỆU CHO VAN/BƠM ĐỒ HỌA
# ============================================================
print("\n[B2] Sinh nhãn ký hiệu cho 31 van và bơm đồ họa...")
for obj_name, label_text in graphic_labels.items():
    if obj_name in graphic_coords:
        left, top, w, h = graphic_coords[obj_name]
        
        # Xử lý đặc biệt cho Pump 33.62 để tránh vượt biên dưới Y=900
        if obj_name == "Graphic I/O field_1":
            lbl_left = left + w + 8
            lbl_top = top + (h - 20) // 2
            lbl_w = 72
            lbl_h = 20
        # Quyết định vị trí nhãn thông thường dựa trên kích thước thiết bị
        elif h > w:  # Thiết bị đứng (van đứng)
            lbl_left = left + (w - 60) // 2
            lbl_top = top - 22
            lbl_w = 60
            lbl_h = 20
        elif w > h:  # Thiết bị ngang (van ngang)
            lbl_left = left + (w - 60) // 2
            lbl_top = top + h + 2
            lbl_w = 60
            lbl_h = 20
        else:  # Bơm hoặc thiết bị vuông
            lbl_left = left
            lbl_top = top - 22
            lbl_w = w
            lbl_h = 20
            
        lbl_name = f"AI_Lbl_{obj_name}"
        create_text_field(lbl_name, label_text, lbl_left, lbl_top, lbl_w, lbl_h, font_size=12, align="Center")
        print(f"  Created label '{label_text}' for {obj_name} at ({lbl_left}, {lbl_top})")

# ============================================================
# BƯỚC 3: TỰ ĐỘNG SINH 25 CẶP IOFIELD + TEXTFIELD SENSOR/VALVE
# ============================================================
print("\n[B3] Sinh 25 ô số hiển thị cảm biến và nhãn đo lường...")

analog_sensors = [
    # BỒN 1 (Left = 154, Top = 90)
    ("AI_IO_FT3200", "FQ3200_Bon1_Eff", 154 - 40, 90 - 20, "999.9", "L", "FT 32.00"),
    ("AI_IO_CV3201", "CV3201_Nuoc_Bon1_M", 154 - 40, 90 + 15, "999.9", "%", "CV 32.01"),
    ("AI_IO_LT3203", "LT3203_Bon1_Eff", 154 + 146, 90 + 40, "999.9", "%", "LT 32.03"),
    ("AI_IO_TT3204", "TT3204_Bon1_Eff", 154 + 146, 90 + 110, "99.9", "°C", "TT 32.04"),
    
    # BỒN 2 (Left = 486, Top = 90)
    ("AI_IO_FT3205", "FQ3205_Bon2_Eff", 486 - 40, 90 - 20, "999.9", "L", "FT 32.05"),
    ("AI_IO_CV3206", "CV3206_Hoi_Bon2_M", 486 - 40, 90 + 15, "999.9", "%", "CV 32.06"),
    ("AI_IO_LT3209", "LT3209_Bon2_Eff", 486 + 146, 90 + 40, "999.9", "%", "LT 32.09"),
    ("AI_IO_TT3208", "TT3208_Bon2_Eff", 486 + 146, 90 + 110, "99.9", "°C", "TT 32.08"),

    # BỒN 4 (Left = 811, Top = 89)
    # Nhãn đổi thành: LT 32.18 / TT 32.19 đúng theo đề
    ("AI_IO_FT3215", "FQ3215_Bon4_Eff", 811 - 40, 89 - 20, "999.9", "L", "FT 32.15"),
    ("AI_IO_CV3216", "CV3216_Hoi_Bon4_M", 811 - 40, 89 + 15, "999.9", "%", "CV 32.16"),
    ("AI_IO_LT3219", "LT3218_Bon4_Eff", 811 + 146, 89 + 40, "999.9", "%", "LT 32.18"),
    ("AI_IO_TT3218", "TT3219_Bon4_Eff", 811 + 146, 89 + 110, "99.9", "°C", "TT 32.19"),

    # BỒN 3 (Left = 1160, Top = 89)
    # Nhãn đổi thành: LT 32.13 / TT 32.14 đúng theo đề
    ("AI_IO_FT3210", "FQ3210_Bon3_Eff", 1160 - 40, 89 - 20, "999.9", "L", "FT 32.10"),
    ("AI_IO_CV3211", "CV3211_Nuoc_Bon3_M", 1160 - 40, 89 + 15, "999.9", "%", "CV 32.11"),
    ("AI_IO_LT3214", "LT3213_Bon3_Eff", 1160 + 146, 89 + 40, "999.9", "%", "LT 32.13"),
    ("AI_IO_TT3213", "TT3214_Bon3_Eff", 1160 + 146, 89 + 110, "99.9", "°C", "TT 32.14"),

    # BỒN CHỨA 1 & 2
    ("AI_IO_LT3302", "LT3302_BonChua1_Eff", 580, 570, "999.9", "%", "LT 33.02"),
    ("AI_IO_TT3301", "TT3301_BonChua1_Eff", 580, 640, "99.9", "°C", "TT 33.01"),
    ("AI_IO_LT3307", "LT3307_BonChua2_Eff", 1054, 566, "999.9", "%", "LT 33.07"),
    ("AI_IO_TT3306", "TT3306_BonChua2_Eff", 1054, 636, "99.9", "°C", "TT 33.06"),

    # HEAT EXCHANGER (BỘ TRAO ĐỔI NHIỆT)
    ("AI_IO_TT3303", "TT3303_TraoDoiNhiet_Eff", 1270, 636, "99.9", "°C", "TT 33.03"),
    ("AI_IO_CV3304", "CV3304_Nuoc_Lam_Mat_M", 1270, 706, "999.9", "%", "CV 33.04"),

    # FILTER & FILLER (BỘ LỌC VÀ CHIẾT RÓT) - Tọa độ mới chống chồng lấn & chống vượt biên (X < 1440)
    ("AI_IO_PI3308", "PI3308_Truoc_Filter_Eff", 970, 820, "99.9", "bar", "PI 33.08"),
    ("AI_IO_FT3309", "FT3309_Xa_Thanh_Pham_Eff", 1190, 740, "999.9", "L/h", "FT 33.09"),
    ("AI_IO_CVFiller", "CV_Filler_Cap_Dich_M", 1290, 820, "999.9", "%", "CV Filler"),
]

for name, tag_name, left, top, fmt_pattern, unit, label in analog_sensors:
    # 1. Tạo IOField chính
    create_numeric_io_field(name, tag_name, left, top, fmt_pattern)
    
    # 2. Tạo nhãn ký hiệu ở trên IOField
    lbl_name = f"AI_Lbl_{name}"
    create_text_field(lbl_name, label, left, top - 25, 72, 20, font_size=12, align="Center")
    
    # 3. Tạo nhãn đơn vị ở bên phải IOField đúng 8px (độ rộng nhãn đơn vị là 45px)
    unit_name = f"AI_Unit_{name}"
    create_text_field(unit_name, unit, left + 72 + 8, top, 45, 26, font_size=13, align="Left")
    
    print(f"  Created IOField {name} ({label}) -> {tag_name} [{unit}] at ({left}, {top})")

# ============================================================
# BƯỚC 4: SINH FILE XML HMI TAG TABLE (66 TAGS)
# ============================================================
def generate_hmi_tags_xml():
    print(f"\n[B4] Tạo file XML HMI Tag Table tại {TAGS_XML_PATH}...")
    
    # Tập hợp các tag
    # GraphicIOFields
    bool_tags = []
    int_tags = []
    for tag in graphic_io_field_mappings.values():
        if "MucDich" in tag or "Frame" in tag:
            int_tags.append(tag)
        else:
            bool_tags.append(tag)
            
    # Analogs
    real_tags = [tag[1] for tag in analog_sensors]
    
    # Đọc mô tả và tạo danh sách TagDef
    tag_defs = []
    
    # Bổ sung các Real tags
    for tag_name in real_tags:
        # Tìm nhãn tương ứng để làm comment
        lbl = "Analog Process Value"
        for _, tn, _, _, _, _, l in analog_sensors:
            if tn == tag_name:
                lbl = l
                break
        tag_defs.append((tag_name, "Real", "IEEE754Float", 4, f"Cảm biến/Van tuyến tính {lbl}"))
        
    # Bổ sung các Int tags
    for tag_name in int_tags:
        tag_defs.append((tag_name, "Int", "Binary", 2, f"Trạng thái hoạt hình HMI {tag_name}"))
        
    # Bổ sung các Bool tags
    for tag_name in bool_tags:
        lbl = "Van/Bơm điều khiển"
        for k, v in graphic_io_field_mappings.items():
            if v == tag_name:
                lbl = graphic_labels.get(k, "Thiết bị")
                break
        tag_defs.append((tag_name, "Bool", "Binary", 1, f"Trạng thái hoạt động {lbl}"))
        
    # Sắp xếp theo tên cho gọn
    tag_defs.sort(key=lambda x: x[0])
    
    # Khởi tạo chuỗi XML
    xml_str = '<?xml version="1.0" encoding="utf-8"?>\n'
    xml_str += '<Document>\n'
    xml_str += '  <Engineering version="V18" />\n'
    xml_str += '  <DocumentInfo>\n'
    xml_str += '    <Created>2026-06-22T00:00:00Z</Created>\n'
    xml_str += '    <ExportSetting>WithDefaults</ExportSetting>\n'
    xml_str += '    <InstalledProducts>\n'
    xml_str += '      <Product>\n'
    xml_str += '        <DisplayName>Totally Integrated Automation Portal</DisplayName>\n'
    xml_str += '        <DisplayVersion>V18</DisplayVersion>\n'
    xml_str += '      </Product>\n'
    xml_str += '    </InstalledProducts>\n'
    xml_str += '  </DocumentInfo>\n'
    xml_str += '  <Hmi.Tag.TagTable ID="0">\n'
    xml_str += '    <AttributeList>\n'
    xml_str += '      <Name>Default tag table</Name>\n'
    xml_str += '    </AttributeList>\n'
    xml_str += '    <ObjectList>\n'
    
    tag_id = 1
    for name, dtype, coding, length, comment in tag_defs:
        xml_str += f'      <Hmi.Tag.Tag ID="{tag_id}" CompositionName="Tags">\n'
        xml_str += '        <AttributeList>\n'
        xml_str += '          <AcquisitionTriggerMode>Visible</AcquisitionTriggerMode>\n'
        xml_str += '          <AddressAccessMode>Symbolic</AddressAccessMode>\n'
        xml_str += f'          <Coding>{coding}</Coding>\n'
        xml_str += '          <ConfirmationType>None</ConfirmationType>\n'
        xml_str += '          <GmpRelevant>false</GmpRelevant>\n'
        xml_str += '          <JobNumber>0</JobNumber>\n'
        xml_str += f'          <Length>{length}</Length>\n'
        xml_str += '          <LinearScaling>false</LinearScaling>\n'
        xml_str += '          <LogicalAddress />\n'
        xml_str += '          <MandatoryCommenting>false</MandatoryCommenting>\n'
        xml_str += f'          <Name>{name}</Name>\n'
        xml_str += '          <Persistency>false</Persistency>\n'
        xml_str += '          <QualityCode>false</QualityCode>\n'
        xml_str += '          <ScalingHmiHigh>100</ScalingHmiHigh>\n'
        xml_str += '          <ScalingHmiLow>0</ScalingHmiLow>\n'
        xml_str += '          <ScalingPlcHigh>10</ScalingPlcHigh>\n'
        xml_str += '          <ScalingPlcLow>0</ScalingPlcLow>\n'
        xml_str += '          <StartValue />\n'
        xml_str += '          <SubstituteValue />\n'
        xml_str += '          <SubstituteValueUsage>None</SubstituteValueUsage>\n'
        xml_str += '          <Synchronization>false</Synchronization>\n'
        xml_str += '          <UpdateMode>ProjectWide</UpdateMode>\n'
        xml_str += '          <UseMultiplexing>false</UseMultiplexing>\n'
        xml_str += '        </AttributeList>\n'
        xml_str += '        <LinkList>\n'
        xml_str += '          <AcquisitionCycle TargetID="@OpenLink">\n'
        xml_str += '            <Name>1 s</Name>\n'
        xml_str += '          </AcquisitionCycle>\n'
        xml_str += '          <Connection TargetID="@OpenLink">\n'
        xml_str += '            <Name>HMI_Connection_1</Name>\n'
        xml_str += '          </Connection>\n'
        xml_str += '          <ControllerTag TargetID="@OpenLink">\n'
        xml_str += f'            <Name>{name}</Name>\n'
        xml_str += '          </ControllerTag>\n'
        xml_str += '          <DataType TargetID="@OpenLink">\n'
        xml_str += f'            <Name>{dtype}</Name>\n'
        xml_str += '          </DataType>\n'
        xml_str += '          <HmiDataType TargetID="@OpenLink">\n'
        xml_str += f'            <Name>{dtype}</Name>\n'
        xml_str += '          </HmiDataType>\n'
        xml_str += '        </LinkList>\n'
        xml_str += '        <ObjectList>\n'
        xml_str += f'          <MultilingualText ID="{(tag_id + 1000):X}" CompositionName="Comment">\n'
        xml_str += '            <ObjectList>\n'
        xml_str += f'              <MultilingualTextItem ID="{(tag_id + 2000):X}" CompositionName="Items">\n'
        xml_str += '                <AttributeList>\n'
        xml_str += '                  <Culture>en-US</Culture>\n'
        xml_str += f'                  <Text>{comment}</Text>\n'
        xml_str += '                </AttributeList>\n'
        xml_str += '              </MultilingualTextItem>\n'
        xml_str += '            </ObjectList>\n'
        xml_str += '          </MultilingualText>\n'
        xml_str += '        </ObjectList>\n'
        xml_str += '      </Hmi.Tag.Tag>\n'
        tag_id += 1
        
    xml_str += '    </ObjectList>\n'
    xml_str += '  </Hmi.Tag.TagTable>\n'
    xml_str += '</Document>\n'
    
    with open(TAGS_XML_PATH, "w", encoding="utf-8") as f:
        f.write(xml_str)
    print(f"  [OK] Generated HMI Tag Table XML ({tag_id - 1} tags) at {TAGS_XML_PATH}")

generate_hmi_tags_xml()

# ============================================================
# LƯU XML MÀN HÌNH
# ============================================================
tree.write(INPUT_XML, encoding="utf-8", xml_declaration=True)
print(f"\n[OK] Patched XML saved successfully at: {INPUT_XML}")

# ============================================================
# XUẤT BÁO CÁO ÁNH XẠ DRY-RUN
# ============================================================
print("\n[B5] Tạo báo cáo dry-run ánh xạ HMI...")

report_lines = []
report_lines.append("# Báo cáo ánh xạ HMI (Dry-Run Mapping Report) - Màn hình Tổng quan")
report_lines.append("")
report_lines.append("Dự án: `Mixing_Nuoc_Tuong_Maggi_2026`  ")
report_lines.append(f"Màn hình sửa đổi: `Hmi.Screen.Man Tong Quan.xml`  ")
report_lines.append("")
report_lines.append("## 1. Danh sách cảm biến đo lường và van tuyến tính (25 IOFields mới sinh)")
report_lines.append("")
report_lines.append("| Ký hiệu màn hình | Tag PLC liên kết | Đơn vị | Định dạng | Vị trí HMI (X, Y) |")
report_lines.append("| :--- | :--- | :--- | :--- | :--- |")

for name, tag_name, left, top, fmt_pattern, unit, label in analog_sensors:
    report_lines.append(f"| {label} | `{tag_name}` | {unit} | `{fmt_pattern}` | ({left}, {top}) |")

report_lines.append("")
report_lines.append("## 2. Danh sách thiết bị dạng đồ họa hoạt hình (GraphicIOFields gốc - 41 thiết bị)")
report_lines.append("")
report_lines.append("| Ký hiệu thiết bị | Tên đối tượng gốc | Tag PLC liên kết | Loại thiết bị | Vị trí HMI (X, Y) |")
report_lines.append("| :--- | :--- | :--- | :--- | :--- |")

# Ghép tọa độ và xuất bảng
sorted_graphic_mappings = sorted(graphic_io_field_mappings.items(), key=lambda x: x[0])
for obj_name, tag_name in sorted_graphic_mappings:
    left, top, w, h = graphic_coords.get(obj_name, (0,0,0,0))
    lbl_text = graphic_labels.get(obj_name, "N/A")
    if "MucDich" in tag_name:
        dev_type = "Mức dịch bồn"
    elif "Frame" in tag_name:
        dev_type = "Động cơ cánh khuấy"
    elif "Pump" in tag_name:
        dev_type = "Bơm"
    else:
        dev_type = "Van ON/OFF"
    report_lines.append(f"| {lbl_text} | `{obj_name}` | `{tag_name}` | {dev_type} | ({left}, {top}) |")

with open(REPORT_PATH, "w", encoding="utf-8") as rf:
    rf.write("\n".join(report_lines))

print(f"[OK] Report exported successfully at: {REPORT_PATH}")
print(f"Tổng số IOField mới sinh: 25. Tổng số TextField mới sinh: 81 (50 cảm biến + 31 nhãn van/bơm).")
