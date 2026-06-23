# -*- coding: utf-8 -*-
from PIL import Image
import xml.etree.ElementTree as ET
import os

xml_path = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\scadabai3_export.xml"
bg_path = r"C:\Users\lienb\.gemini\antigravity-ide\brain\0123c9f4-e5bc-424b-80d8-b015956965a4\scadabai3_bg.png"
artifacts_dir = r"C:\Users\lienb\.gemini\antigravity-ide\brain\0123c9f4-e5bc-424b-80d8-b015956965a4"

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

img = Image.open(bg_path)
width_img, height_img = img.size

md_lines = []
md_lines.append("# Báo cáo Tọa độ & Nhãn IO Field của scadabai3\n")
md_lines.append("Tài liệu này hiển thị hình ảnh cắt xung quanh từng ô nhập xuất số liệu (IO Field) để đối chiếu nhãn.\n")

for i, io in enumerate(io_fields):
    x1, y1 = io["left"], io["top"]
    w, h = io["w"], io["h"]
    
    # We want to crop from x1 - 150 (to capture the label to the left) to x1 + w + 50, and y1 - 10 to y1 + h + 10
    crop_x1 = max(0, x1 - 200)
    crop_y1 = max(0, y1 - 15)
    crop_x2 = min(width_img, x1 + w + 100)
    crop_y2 = min(height_img, y1 + h + 15)
    
    cropped = img.crop((crop_x1, crop_y1, crop_x2, crop_y2))
    crop_filename = f"crop_{i+1:02d}.png"
    crop_filepath = os.path.join(artifacts_dir, crop_filename)
    cropped.save(crop_filepath)
    
    md_lines.append(f"## IO Field {i+1}: {io['name']}")
    md_lines.append(f"- **Tọa độ**: Left={x1}, Top={y1}, Width={w}, Height={h}")
    md_lines.append(f"![Crop {i+1}]({crop_filename})\n")
    md_lines.append("--- \n")

md_path = os.path.join(artifacts_dir, "scadabai3_io_crops.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print(f"[SUCCESS] Cropped images and generated markdown report at {md_path}")
