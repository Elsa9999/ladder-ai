# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

xml_path = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\scadabai3_export.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

def get_local_tag(elem):
    return elem.tag.split("}")[-1]

io_fields = []
for elem in root.iter():
    tag = get_local_tag(elem)
    if tag == "Hmi.Screen.IOField":
        attrs = elem.find("AttributeList")
        if attrs is not None:
            name = attrs.find("ObjectName").text
            left = int(attrs.find("Left").text)
            top = int(attrs.find("Top").text)
            width = int(attrs.find("Width").text)
            height = int(attrs.find("Height").text)
            io_fields.append({
                "name": name,
                "left": left,
                "top": top,
                "w": width,
                "h": height
            })

# Sort by Top, then Left
io_fields.sort(key=lambda x: (x["top"], x["left"]))

print("=== ALL IO FIELDS SORTED BY Y (TOP) ===")
for i, io in enumerate(io_fields):
    print(f"{i+1:2d}. Name: {io['name']:15s} | Left: {io['left']:4d} | Top: {io['top']:4d} | W: {io['w']:3d} | H: {io['h']:3d}")

print("\n=== CLUSTERS BY AREA ===")
# Let's group them by X ranges to find columns
# 1. Left column (X < 150): Clinker / Silo 1 related feed weight
# 2. X: 150-300: Slag/Gypsum related feed weight / parameters
# 3. X: 300-450: Separator / Setpoints / CA Fan
# 4. X: 450-600: Setpoints
# etc.
for io in io_fields:
    area = "Unknown"
    x = io["left"]
    y = io["top"]
    
    # Let's map based on coordinates:
    if x < 150 and y < 400:
        area = "Top Left (Time / date or Clinker)"
    elif x < 150 and y >= 400:
        area = "Bottom Left (LQ61 / LQ62 or similar)"
    elif 150 <= x < 300 and y < 400:
        area = "Top Slag/Gypsum feed or Trend area"
    elif 150 <= x < 300 and y >= 400:
        area = "Bottom LQ61/LQ62/LQ63 motors/hours"
    elif 300 <= x < 500 and y < 400:
        area = "CA Fan / Separator or Setpoints"
    elif 300 <= x < 500 and y >= 400:
        area = "Cement Mill parameters / Lub Stop time"
    elif 500 <= x < 650:
        area = "Setpoints / 700BC01 actual / separator bottom"
    elif 650 <= x < 1100:
        area = "Center Area (700HES01, 700FN03, 700FN10, 700CM01 A, NIBS, etc.)"
    elif 1100 <= x < 1500:
        area = "Right Area (700FN4, 800DC1, 800DC2, etc.)"
    elif x >= 1500:
        area = "Far Right (Silo 1 & 2 levels, etc.)"
        
    print(f"Name: {io['name']:15s} | Pos: ({x:4d}, {y:4d}) | Area: {area}")
