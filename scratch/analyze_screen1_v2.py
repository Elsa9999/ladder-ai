#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
analyze_screen1_v2.py
Parser đúng cấu trúc TIA V18 XML: AttributeList/<Tag>
"""
import xml.etree.ElementTree as ET
import csv, json, math, hashlib

XML_PATH = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\screen1_export_20260622_220027\Screen_1.xml"
OUT_CSV  = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\screen1_inventory.csv"
OUT_JSON = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\screen1_inventory.json"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest().upper()

def al_text(node, tag):
    """Lấy text từ AttributeList/<tag>."""
    al = node.find("AttributeList")
    if al is None:
        return ""
    el = al.find(tag)
    return (el.text or "").strip() if el is not None else ""

def get_process_value(node):
    """
    Lấy ProcessValue từ:
      1. AttributeList/ProcessValue
      2. ObjectList/PropertyBinding[@Name='ProcessValue']/Source/TagBinding[@TagName]
      3. ObjectList/PropertyBinding[@Name='ProcessValue']/Source (text)
    """
    # 1. Direct attribute
    v = al_text(node, "ProcessValue")
    if v:
        return v

    # 2. Scan ObjectList for PropertyBinding
    ol = node.find("ObjectList")
    if ol is not None:
        for pb in ol.iter("PropertyBinding"):
            n = pb.get("Name", "")
            if n == "ProcessValue":
                # TagBinding
                for tb in pb.iter("TagBinding"):
                    tag_name = tb.get("TagName", "")
                    if tag_name:
                        return tag_name
                # text inside Source
                src = pb.find("Source")
                if src is not None and src.text:
                    return src.text.strip()
    return ""

def get_text_fields(root):
    """Thu thập tất cả TextField: name, coords, text content."""
    fields = []
    for node in root.iter("Hmi.Screen.TextField"):
        name = al_text(node, "ObjectName")
        try:
            left   = int(float(al_text(node, "Left")   or 0))
            top    = int(float(al_text(node, "Top")    or 0))
            width  = int(float(al_text(node, "Width")  or 0))
            height = int(float(al_text(node, "Height") or 0))
        except:
            left = top = width = height = 0

        # Lấy text từ MultilingualText
        text = ""
        for mt in node.iter("MultilingualText"):
            for mti in mt.iter("MultilingualTextItem"):
                mti_al = mti.find("AttributeList")
                if mti_al is not None:
                    t_el = mti_al.find("Text")
                    if t_el is not None and t_el.text:
                        text = t_el.text.strip()
                        break
            if text:
                break

        fields.append({"name": name, "left": left, "top": top,
                        "width": width, "height": height, "text": text})
    return fields

def nearest_label(cx, cy, text_fields, max_dist=150):
    best = ("", "")
    bd = 9999
    for tf in text_fields:
        tcx = tf["left"] + tf["width"] / 2
        tcy = tf["top"]  + tf["height"] / 2
        d = math.sqrt((cx - tcx)**2 + (cy - tcy)**2)
        if d < bd and d < max_dist:
            bd = d
            best = (tf["name"], tf["text"])
    return best

def main():
    print(f"SHA256: {sha256_file(XML_PATH)}")

    tree = ET.parse(XML_PATH)
    root = tree.getroot()

    text_fields = get_text_fields(root)

    io_fields      = []
    graphic_fields = []

    # --- IOField ---
    for node in root.iter("Hmi.Screen.IOField"):
        name     = al_text(node, "ObjectName")
        try:
            left   = int(float(al_text(node, "Left")   or 0))
            top    = int(float(al_text(node, "Top")    or 0))
            width  = int(float(al_text(node, "Width")  or 0))
            height = int(float(al_text(node, "Height") or 0))
        except:
            left = top = width = height = 0

        proc_val = get_process_value(node)
        fmt      = al_text(node, "FormatPattern")
        h_align  = al_text(node, "HorizontalAlignment")
        v_align  = al_text(node, "VerticalAlignment")
        mode     = al_text(node, "DisplayMode") or al_text(node, "Mode")

        cx, cy = left + width / 2, top + height / 2
        lbl_name, lbl_text = nearest_label(cx, cy, text_fields)

        io_fields.append({
            "ObjectName": name, "Type": "IOField",
            "Left": left, "Top": top, "Width": width, "Height": height,
            "ProcessValue": proc_val,
            "FormatPattern": fmt, "HorizontalAlignment": h_align,
            "VerticalAlignment": v_align, "Mode": mode,
            "NearestLabelName": lbl_name, "NearestLabelText": lbl_text,
        })

    # --- GraphicIOField ---
    for node in root.iter("Hmi.Screen.GraphicIOField"):
        name = al_text(node, "ObjectName")
        try:
            left   = int(float(al_text(node, "Left")   or 0))
            top    = int(float(al_text(node, "Top")    or 0))
            width  = int(float(al_text(node, "Width")  or 0))
            height = int(float(al_text(node, "Height") or 0))
        except:
            left = top = width = height = 0
        proc_val = get_process_value(node)
        graphic_fields.append({
            "ObjectName": name, "Type": "GraphicIOField",
            "Left": left, "Top": top, "Width": width, "Height": height,
            "ProcessValue": proc_val,
        })

    print(f"\nIOField count       : {len(io_fields)}")
    print(f"GraphicIOField count: {len(graphic_fields)}")
    print(f"TextField  count    : {len(text_fields)}")

    # Print IOField table
    print("\n" + "="*140)
    hdr = f"{'#':<3} {'ObjectName':<22} {'L':>5} {'T':>5} {'W':>4} {'H':>4}  {'ProcessValue':<45} {'Format':<10} {'H/V Align':<14} {'NearestLabel'}"
    print(hdr)
    print("="*140)
    for i, f in enumerate(io_fields, 1):
        align = f"{f['HorizontalAlignment']}/{f['VerticalAlignment']}"
        print(f"{i:<3} {f['ObjectName']:<22} {f['Left']:>5} {f['Top']:>5} {f['Width']:>4} {f['Height']:>4}  "
              f"{f['ProcessValue']:<45} {f['FormatPattern']:<10} {align:<14} {f['NearestLabelText']}")

    # Save CSV
    fieldnames = ["ObjectName","Type","Left","Top","Width","Height",
                  "ProcessValue","FormatPattern","HorizontalAlignment","VerticalAlignment",
                  "Mode","NearestLabelName","NearestLabelText"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as fout:
        w = csv.DictWriter(fout, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        for item in io_fields:
            w.writerow(item)
        for item in graphic_fields:
            row = {k: item.get(k, "") for k in fieldnames}
            w.writerow(row)

    print(f"\nCSV: {OUT_CSV}")

    with open(OUT_JSON, "w", encoding="utf-8") as fout:
        json.dump({"io_fields": io_fields,
                   "graphic_fields": graphic_fields,
                   "text_fields": text_fields}, fout, ensure_ascii=False, indent=2)
    print(f"JSON: {OUT_JSON}")

if __name__ == "__main__":
    main()
