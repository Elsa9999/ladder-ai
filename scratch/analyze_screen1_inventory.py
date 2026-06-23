#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
analyze_screen1_inventory.py
Phân tích Screen_1.xml để lập inventory toàn bộ IOField, GraphicIOField
và đối chiếu nhãn gần nhất từ TextField lân cận.
"""
import xml.etree.ElementTree as ET
import csv, sys, math, hashlib, os, json

XML_PATH = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\screen1_export_20260622_220027\Screen_1.xml"
OUT_CSV  = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\screen1_inventory.csv"
OUT_JSON = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\screen1_inventory.json"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest().upper()

def parse_coords(elem, ns):
    """Trả về (left, top, width, height) từ phần tử."""
    pos  = elem.find(f"{ns}Position")
    size = elem.find(f"{ns}Size")
    if pos is None:
        pos = elem.find("Position")
    if size is None:
        size = elem.find("Size")

    left   = int(float(pos.get("Left",   "0"))) if pos is not None else 0
    top    = int(float(pos.get("Top",    "0"))) if pos is not None else 0
    width  = int(float(size.get("Width", "0"))) if size is not None else 0
    height = int(float(size.get("Height","0"))) if size is not None else 0
    return left, top, width, height

def get_attr(elem, ns, path, attrib=None):
    """Lấy text hoặc attribute từ sub-element."""
    child = elem.find(f"{ns}{path}")
    if child is None:
        child = elem.find(path)
    if child is None:
        return ""
    if attrib:
        return child.get(attrib, "")
    return (child.text or "").strip()

def nearest_label(item, left, top, width, height, text_fields):
    """Tìm TextField gần nhất (trung tâm trong vòng 200px)."""
    cx = left + width / 2
    cy = top  + height / 2
    best_dist = 9999
    best_name = ""
    best_text = ""
    for tf in text_fields:
        tl, tt, tw, th = tf["coords"]
        tcx = tl + tw / 2
        tcy = tt + th / 2
        dist = math.sqrt((cx - tcx)**2 + (cy - tcy)**2)
        if dist < best_dist and dist < 200:
            best_dist = dist
            best_name = tf["name"]
            best_text = tf["text"]
    return best_name, best_text

def main():
    tree = ET.parse(XML_PATH)
    root = tree.getroot()

    # Xác định namespace
    raw_tag = root.tag
    ns = ""
    if raw_tag.startswith("{"):
        ns = raw_tag[:raw_tag.index("}") + 1]

    print(f"Root tag      : {raw_tag}")
    print(f"Namespace     : {ns!r}")
    print(f"SHA256 (XML)  : {sha256_file(XML_PATH)}")

    # Thu thập toàn bộ phần tử (duyệt đệ quy)
    io_fields      = []   # IOField
    graphic_fields = []   # GraphicIOField
    text_fields    = []   # TextField (để tìm nhãn)

    def walk(node, depth=0):
        tag_local = node.tag.replace(ns, "")
        name  = node.get("Name", "")
        otype = node.get("ObjectType", node.get("Type", ""))

        # Phát hiện theo type attribute hoặc tag name
        is_io       = ("IOField" in tag_local and "Graphic" not in tag_local) or ("IOField" in otype and "Graphic" not in otype)
        is_graphic  = "GraphicIOField" in tag_local or "GraphicIOField" in otype
        is_text     = "TextField" in tag_local or "TextField" in otype

        if is_io or is_graphic or is_text:
            try:
                left, top, width, height = parse_coords(node, ns)
            except:
                left, top, width, height = 0, 0, 0, 0

        if is_text:
            # Lấy nội dung text
            txt = ""
            for t_elem in node.iter():
                t_local = t_elem.tag.replace(ns, "")
                if "Text" in t_local and t_elem.text:
                    txt = t_elem.text.strip()
                    break
            text_fields.append({
                "name": name,
                "coords": (left, top, width, height),
                "text": txt
            })

        elif is_graphic:
            proc_val = get_attr(node, ns, "ProcessValue")
            if not proc_val:
                # Tìm trong Bindings
                for b in node.iter():
                    b_local = b.tag.replace(ns, "")
                    if "ProcessValue" in b_local and b.get("TagName"):
                        proc_val = b.get("TagName")
                        break
            graphic_fields.append({
                "name": name,
                "type": "GraphicIOField",
                "left": left, "top": top, "width": width, "height": height,
                "process_value": proc_val,
            })

        elif is_io:
            proc_val = get_attr(node, ns, "ProcessValue")
            if not proc_val:
                for b in node.iter():
                    b_local = b.tag.replace(ns, "")
                    if "ProcessValue" in b_local and b.get("TagName"):
                        proc_val = b.get("TagName")
                        break
            fmt = get_attr(node, ns, "FormatPattern")
            h_align = get_attr(node, ns, "HorizontalAlignment")
            v_align = get_attr(node, ns, "VerticalAlignment")
            mode = get_attr(node, ns, "DisplayMode") or get_attr(node, ns, "Mode")
            io_fields.append({
                "name": name,
                "type": "IOField",
                "left": left, "top": top, "width": width, "height": height,
                "process_value": proc_val,
                "format": fmt,
                "h_align": h_align,
                "v_align": v_align,
                "mode": mode,
            })

        for child in node:
            walk(child, depth + 1)

    walk(root)

    print(f"\nTotal IOField       : {len(io_fields)}")
    print(f"Total GraphicIOField: {len(graphic_fields)}")
    print(f"Total TextField     : {len(text_fields)}")

    # Gắn nhãn gần nhất cho mỗi IOField
    for item in io_fields:
        lbl_name, lbl_text = nearest_label(
            item, item["left"], item["top"], item["width"], item["height"], text_fields
        )
        item["nearest_label_name"] = lbl_name
        item["nearest_label_text"] = lbl_text

    # In bảng IOField
    print("\n" + "="*120)
    print(f"{'ObjectName':<40} {'Left':>6} {'Top':>5} {'W':>5} {'H':>5}  {'ProcessValue':<45} {'Format':<10} {'NearestLabel'}")
    print("="*120)
    for f in io_fields:
        print(f"{f['name']:<40} {f['left']:>6} {f['top']:>5} {f['width']:>5} {f['height']:>5}  "
              f"{f['process_value']:<45} {f['format']:<10} {f['nearest_label_text']}")

    print(f"\n--- GraphicIOField ({len(graphic_fields)}) ---")
    for g in graphic_fields:
        print(f"  {g['name']:<40} ({g['left']},{g['top']}) {g['width']}x{g['height']}  PV={g['process_value']}")

    # Xuất CSV
    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "ObjectName","Type","Left","Top","Width","Height",
            "ProcessValue","FormatPattern","HorizontalAlignment","VerticalAlignment",
            "Mode","NearestLabelName","NearestLabelText"
        ])
        writer.writeheader()
        for item in io_fields:
            writer.writerow({
                "ObjectName": item["name"],
                "Type": "IOField",
                "Left": item["left"], "Top": item["top"],
                "Width": item["width"], "Height": item["height"],
                "ProcessValue": item["process_value"],
                "FormatPattern": item["format"],
                "HorizontalAlignment": item["h_align"],
                "VerticalAlignment": item["v_align"],
                "Mode": item["mode"],
                "NearestLabelName": item["nearest_label_name"],
                "NearestLabelText": item["nearest_label_text"],
            })
        for item in graphic_fields:
            writer.writerow({
                "ObjectName": item["name"],
                "Type": "GraphicIOField",
                "Left": item["left"], "Top": item["top"],
                "Width": item["width"], "Height": item["height"],
                "ProcessValue": item["process_value"],
                "FormatPattern": "", "HorizontalAlignment": "",
                "VerticalAlignment": "", "Mode": "",
                "NearestLabelName": "", "NearestLabelText": "",
            })
    print(f"\nCSV saved: {OUT_CSV}")

    # Lưu JSON để dùng bước tiếp theo
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"io_fields": io_fields, "graphic_fields": graphic_fields, "text_fields": text_fields}, f, ensure_ascii=False, indent=2)
    print(f"JSON saved: {OUT_JSON}")

if __name__ == "__main__":
    main()
