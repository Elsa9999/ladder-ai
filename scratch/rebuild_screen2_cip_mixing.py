# -*- coding: utf-8 -*-
"""
rebuild_screen2_cip_mixing.py
============================================================
Tạo lại HMI Tags đúng chuẩn AI_ và gán vào IO fields của Screen_2
cho hệ thống CIP-MIXING 4 bồn theo yêu cầu bài thi SCADA.

Đề bài yêu cầu (trích ảnh Facebook):
  - Nhiệt độ: 50-80°C
  - Áp suất: 7-8 bar
  - Lưu lượng: 100-200 L/h
  - Tần số: 20-30 Hz

Layout màn hình (4 cột x 2 hàng, 1920x1080):
  Col 1 (L≈217):  BON TRON 1 → TT3204 (°C, top) + LT3203 (%, bottom)
  Col 2 (L≈789):  BON TRON 2 → TT3208 (°C, top) + PT3208 (bar, bottom)
  Col 3 (L≈1243): BON TRON 3 → TT3214 (°C, top) + FT3213 (L/h, bottom)
  Col 4 (L≈1715): BON TRON 4 → TT3219 (°C, top) + FS51 (Hz, bottom)
============================================================
"""
import xml.etree.ElementTree as ET
import os, sys

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# ĐƯỜNG DẪN
# ============================================================
INPUT_SCREEN = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\active_screen_2_export.xml"
OUTPUT_DIR   = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens"
OUTPUT_SCREEN= os.path.join(OUTPUT_DIR, "Hmi.Screen.Screen_2.xml")
OUTPUT_TAGS  = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\AI_HMI_Tags_CIP_Mixing.xml"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# MAPPING IO FIELD → TAG AI_ ĐÃ PHÂN TÍCH TỪ ẢNH
# field_1 (L=217,  T=281): Hàng trên, Col 1 → BON TRON 1 nhiệt độ
# field_2 (L=789,  T=300): Hàng trên, Col 2 → BON TRON 2 nhiệt độ
# field_5 (L=1243, T=300): Hàng trên, Col 3 → BON TRON 3 nhiệt độ
# field_7 (L=1715, T=304): Hàng trên, Col 4 → BON TRON 4 nhiệt độ
# field_3 (L=216,  T=492): Hàng dưới, Col 1 → Áp suất hệ thống 1
# field_6 (L=787,  T=483): Hàng dưới, Col 2 → Áp suất hệ thống 2
# field_4 (L=1252, T=490): Hàng dưới, Col 3 → Lưu lượng
# field_8 (L=1715, T=486): Hàng dưới, Col 4 → Tần số bơm
# ============================================================
FIELD_MAPPINGS = {
    # IO Field Name     : (Tag AI_ Name,         Unit,  Format,  Min,   Max,   Mô tả)
    "I/O field_1"  : ("AI_LT3203_PV",  "L",   "999.9",   0.0,  1000.0, "Muc bon tron 1"),
    "I/O field_3"  : ("AI_TT3204_PV",  "°C",  "99.9",    0.0,   100.0, "Nhiet do bon tron 1"),
    "I/O field_2"  : ("AI_LT3209_PV",  "L",   "999.9",   0.0,  1000.0, "Muc bon tron 2"),
    "I/O field_6"  : ("AI_TT3208_PV",  "°C",  "99.9",    0.0,   100.0, "Nhiet do bon tron 2"),
    "I/O field_5"  : ("AI_LT3213_PV",  "L",   "999.9",   0.0,  1000.0, "Muc bon tron 3"),
    "I/O field_4"  : ("AI_TT3214_PV",  "°C",  "99.9",    0.0,   100.0, "Nhiet do bon tron 3"),
    "I/O field_7"  : ("AI_LT3218_PV",  "L",   "999.9",   0.0,  1000.0, "Muc bon tron 4"),
    "I/O field_8"  : ("AI_TT3219_PV",  "°C",  "99.9",    0.0,   100.0, "Nhiet do bon tron 4"),
}

# ============================================================
# PARSE SCREEN XML
# ============================================================
ET.register_namespace('', '')
tree = ET.parse(INPUT_SCREEN)
root = tree.getroot()

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

id_counter = max_id + 2000
print(f"Max ID = {hex(max_id)}, counter = {hex(id_counter)}")

def next_id():
    global id_counter
    r = hex(id_counter)[2:].upper()
    id_counter += 1
    return r

def make_font(parent, family="Arial", size=13, bold=True):
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
    """Gắn tag AI_ vào ProcessValue của IOField"""
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

    # Xóa các animation cũ (gây lỗi compile vì chứa tag cũ không tồn tại)
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

# ============================================================
# BƯỚC 1: Patch tất cả IO Fields
# ============================================================
layer    = root.find(".//Hmi.Screen.ScreenLayer")
obj_list = layer.find("ObjectList")

print("\n[B1] Gán tag AI_ vào IO Fields...")
io_coords = {}

for elem in obj_list:
    if not elem.tag.endswith("IOField"):
        continue
    attrs = elem.find("AttributeList")
    name  = attrs.find("ObjectName").text
    if name not in FIELD_MAPPINGS:
        continue
    tag_name, unit, fmt, mn, mx, desc = FIELD_MAPPINGS[name]
    left = int(attrs.find("Left").text)
    top  = int(attrs.find("Top").text)
    w    = int(attrs.find("Width").text)
    h    = int(attrs.find("Height").text)
    io_coords[name] = (left, top, w, h, unit, tag_name)

    # FormatPattern
    fp = attrs.find("FormatPattern")
    if fp is not None: fp.text = fmt
    else: ET.SubElement(attrs, "FormatPattern").text = fmt

    # Alignment
    for aname, aval in [("HorizontalAlignment","Center"),("VerticalAlignment","Middle")]:
        el = attrs.find(aname)
        if el is not None: el.text = aval
        else: ET.SubElement(attrs, aname).text = aval

    bind_tag(elem, tag_name)
    print(f"  {name:20s} → {tag_name:20s}  [{fmt}] {unit}")

# ============================================================
# BƯỚC 2: Xóa unit labels cũ
# ============================================================
print("\n[B2] Xóa unit labels cũ...")
to_rm = [e for e in obj_list
         if e.tag.endswith("TextField")
         and e.find("AttributeList/ObjectName") is not None
         and e.find("AttributeList/ObjectName").text
         and e.find("AttributeList/ObjectName").text.startswith("Text_field_Unit_")]
for e in to_rm:
    obj_list.remove(e)
print(f"  Đã xóa {len(to_rm)} label cũ")

# ============================================================
# BƯỚC 3: Tạo unit labels mới (Arial 13 Bold, 8px bên phải)
# ============================================================
print("\n[B3] Tạo unit labels mới...")
for field_name, (left, top, w, h, unit, tag_name) in io_coords.items():
    tf_left = left + w + 8
    tf_name = f"Text_field_Unit_{field_name}"

    tf = ET.SubElement(obj_list, "Hmi.Screen.TextField",
                       {"ID": next_id(), "CompositionName": "ScreenItems"})
    ta = ET.SubElement(tf, "AttributeList")
    ET.SubElement(ta, "BackFillStyle").text = "Transparent"
    ET.SubElement(ta, "BorderWidth").text = "0"
    ET.SubElement(ta, "ForeColor").text = "0, 0, 0"
    ET.SubElement(ta, "Height").text = str(h)
    ET.SubElement(ta, "HorizontalAlignment").text = "Left"
    ET.SubElement(ta, "Left").text = str(tf_left)
    ET.SubElement(ta, "ObjectName").text = tf_name
    ET.SubElement(ta, "Top").text = str(top)
    ET.SubElement(ta, "VerticalAlignment").text = "Middle"
    ET.SubElement(ta, "Width").text = "60"

    ll = ET.SubElement(tf, "LinkList")
    si = ET.SubElement(ll, "StyleItem", {"TargetID": "@OpenLink"})
    ET.SubElement(si, "Name").text = "Text field"

    tobjs = ET.SubElement(tf, "ObjectList")
    make_font(tobjs, "Arial", 13, True)
    ml = ET.SubElement(tobjs, "MultilingualText",
                       {"ID": next_id(), "CompositionName": "Text"})
    mlobjs = ET.SubElement(ml, "ObjectList")
    mli = ET.SubElement(mlobjs, "MultilingualTextItem",
                        {"ID": next_id(), "CompositionName": "Items"})
    mlia = ET.SubElement(mli, "AttributeList")
    ET.SubElement(mlia, "Culture").text = "en-US"
    ET.SubElement(mlia, "Text").text = f"<body><p>{unit}</p></body>"

    print(f"  '{unit}' tại ({tf_left},{top}) cho {field_name}")

# ============================================================
# BƯỚC 4: Sửa screen Width 1980→1920 nếu cần
# ============================================================
for elem in root.iter():
    if elem.find("AttributeList/Name") is not None:
        n = elem.find("AttributeList/Name")
        if n is not None and n.text == "Screen_2":
            w_el = elem.find("AttributeList/Width")
            if w_el is not None and w_el.text != "1920":
                print(f"\n[B4] Sửa Width {w_el.text}→1920")
                w_el.text = "1920"

# ============================================================
# GHI FILE SCREEN
# ============================================================
tree.write(OUTPUT_SCREEN, encoding="utf-8", xml_declaration=True)
print(f"\n[OK] Screen XML: {OUTPUT_SCREEN}")
print(f"     Size: {os.path.getsize(OUTPUT_SCREEN):,} bytes")

# ============================================================
# TẠO HMI TAGS XML VỚI TAGS AI_ MỚI
# ============================================================
print("\n[B5] Tạo file HMI Tags mới (AI_ prefix)...")

TAGS_XML = '''<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V18" />
  <DocumentInfo>
    <Created>2026-06-12T00:00:00Z</Created>
    <ExportSetting>WithDefaults</ExportSetting>
    <InstalledProducts>
      <Product>
        <DisplayName>Totally Integrated Automation Portal</DisplayName>
        <DisplayVersion>V18</DisplayVersion>
      </Product>
    </InstalledProducts>
  </DocumentInfo>
  <Hmi.Tag.TagTable ID="0">
    <AttributeList>
      <Name>HMI_Tags</Name>
    </AttributeList>
    <ObjectList>
'''

tag_id = 1
TAG_DEFS = [
    # (Name,           Type,    Coding,        Comment)
    ("AI_LT3203_PV",  "Real",  "IEEE754Float", "Muc bon tron 1 LT3203"),
    ("AI_TT3204_PV",  "Real",  "IEEE754Float", "Nhiet do bon tron 1 TT3204"),
    ("AI_LT3209_PV",  "Real",  "IEEE754Float", "Muc bon tron 2 LT3209"),
    ("AI_TT3208_PV",  "Real",  "IEEE754Float", "Nhiet do bon tron 2 TT3208"),
    ("AI_LT3213_PV",  "Real",  "IEEE754Float", "Muc bon tron 3 LT3213"),
    ("AI_TT3214_PV",  "Real",  "IEEE754Float", "Nhiet do bon tron 3 TT3214"),
    ("AI_LT3218_PV",  "Real",  "IEEE754Float", "Muc bon tron 4 LT3218"),
    ("AI_TT3219_PV",  "Real",  "IEEE754Float", "Nhiet do bon tron 4 TT3219"),
    # Bool trạng thái thiết bị
    ("AI_BON1_Chay",  "Bool",  "Binary",       "Bon tron 1 dang hoat dong"),
    ("AI_BON2_Chay",  "Bool",  "Binary",       "Bon tron 2 dang hoat dong"),
    ("AI_BON3_Chay",  "Bool",  "Binary",       "Bon tron 3 dang hoat dong"),
    ("AI_BON4_Chay",  "Bool",  "Binary",       "Bon tron 4 dang hoat dong"),
    ("AI_PUMP3264_Chay","Bool","Binary",        "Bom PUMP3264 dang chay"),
    ("AI_PUMP3265_Chay","Bool","Binary",        "Bom PUMP3265 dang chay"),
    ("AI_Logged_In",  "Int",   "Binary",       "Trang thai dang nhap - 0:chua, 1:da dang nhap"),
]

for name, dtype, coding, comment in TAG_DEFS:
    length = 4 if dtype == "Real" else (2 if dtype == "Int" else 1)
    TAGS_XML += f'''      <Hmi.Tag.Tag ID="{tag_id}" CompositionName="Tags">
        <AttributeList>
          <AcquisitionTriggerMode>Visible</AcquisitionTriggerMode>
          <AddressAccessMode>Symbolic</AddressAccessMode>
          <Coding>{coding}</Coding>
          <ConfirmationType>None</ConfirmationType>
          <GmpRelevant>false</GmpRelevant>
          <JobNumber>0</JobNumber>
          <Length>{length}</Length>
          <LinearScaling>false</LinearScaling>
          <LogicalAddress />
          <MandatoryCommenting>false</MandatoryCommenting>
          <Name>{name}</Name>
          <Persistency>false</Persistency>
          <QualityCode>false</QualityCode>
          <StartValue />
          <SubstituteValue />
          <SubstituteValueUsage>None</SubstituteValueUsage>
          <Synchronization>false</Synchronization>
          <UpdateMode>ProjectWide</UpdateMode>
          <UseMultiplexing>false</UseMultiplexing>
        </AttributeList>
        <LinkList>
          <AcquisitionCycle TargetID="@OpenLink">
            <Name>1 s</Name>
          </AcquisitionCycle>
          <Connection TargetID="@OpenLink">
            <Name>HMI_Connection_1</Name>
          </Connection>
          <ControllerTag TargetID="@OpenLink">
            <Name>{name}</Name>
          </ControllerTag>
          <DataType TargetID="@OpenLink">
            <Name>{dtype}</Name>
          </DataType>
          <HmiDataType TargetID="@OpenLink">
            <Name>{dtype}</Name>
          </HmiDataType>
        </LinkList>
      </Hmi.Tag.Tag>
'''
    tag_id += 1

TAGS_XML += '''    </ObjectList>
  </Hmi.Tag.TagTable>
</Document>
'''

with open(OUTPUT_TAGS, 'w', encoding='utf-8') as f:
    f.write(TAGS_XML)

print(f"[OK] Tags XML: {OUTPUT_TAGS}")
print(f"     {len(TAG_DEFS)} tags đã tạo")
print("\n" + "="*55)
print("TONG KET MAPPING:")
print("="*55)
for field, (tag, unit, fmt, mn, mx, desc) in FIELD_MAPPINGS.items():
    print(f"  {field:20s} → {tag:22s}  {unit:5s}  [{mn}-{mx}]")
print("="*55)
