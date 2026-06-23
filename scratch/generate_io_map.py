# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import xml.etree.ElementTree as ET
import os

xml_path = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\scadabai3_export.xml"
bg_path = r"C:\Users\lienb\.gemini\antigravity-ide\brain\0123c9f4-e5bc-424b-80d8-b015956965a4\scadabai3_bg.png"
out_path = r"C:\Users\lienb\.gemini\antigravity-ide\brain\0123c9f4-e5bc-424b-80d8-b015956965a4\scadabai3_io_map.png"

if not os.path.exists(bg_path):
    print("Error: Background image not found!")
    exit(1)

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

# Open image
img = Image.open(bg_path)
draw = ImageDraw.Draw(img)

# Try to load a font, fallback to default if not found
try:
    font = ImageFont.truetype("arial.ttf", 15)
except IOError:
    font = ImageFont.load_default()

for i, io in enumerate(io_fields):
    x1, y1 = io["left"], io["top"]
    x2, y2 = x1 + io["w"], y1 + io["h"]
    
    # Draw outline
    draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
    
    # Draw label text
    lbl = f"{i+1}:{io['name']}"
    # Draw text background
    draw.rectangle([x1, y1 - 18, x1 + 100, y1], fill="black")
    draw.text((x1 + 2, y1 - 16), lbl, fill="yellow", font=font)

img.save(out_path)
print(f"[SUCCESS] Labeled IO map saved to {out_path}")
