# -*- coding: utf-8 -*-
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    import pytesseract
    from PIL import Image
    print("pytesseract is available")
except ImportError:
    pytesseract = None
    print("pytesseract is NOT available")

if pytesseract:
    # Check if tesseract path is set or needs to be pointed to
    # On Windows, Tesseract is typically installed in Program Files
    tess_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    ]
    for path in tess_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print("Found tesseract at", path)
            break
            
    xml_path = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\scadabai3_export.xml"
    bg_path = r"C:\Users\lienb\.gemini\antigravity-ide\brain\0123c9f4-e5bc-424b-80d8-b015956965a4\scadabai3_bg.png"
    
    import xml.etree.ElementTree as ET
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
                    "name": name, "left": left, "top": top, "w": width, "h": height
                })
                
    io_fields.sort(key=lambda x: (x["top"], x["left"]))
    img = Image.open(bg_path)
    
    print("\n--- OCR RESULTS ---")
    for i, io in enumerate(io_fields):
        x1, y1 = io["left"], io["top"]
        w, h = io["w"], io["h"]
        
        # Crop context
        crop_x1 = max(0, x1 - 250)
        crop_y1 = max(0, y1 - 20)
        crop_x2 = min(img.width, x1 + w + 120)
        crop_y2 = min(img.height, y1 + h + 20)
        
        cropped = img.crop((crop_x1, crop_y1, crop_x2, crop_y2))
        try:
            text = pytesseract.image_to_string(cropped, lang='eng').strip()
            # Clean up whitespace
            text_clean = " | ".join([l.strip() for l in text.split("\n") if l.strip()])
            print(f"IO Field {i+1:2d} ({io['name']}) at ({x1}, {y1}): OCR -> {text_clean}")
        except Exception as e:
            print(f"IO Field {i+1:2d} ({io['name']}): OCR Failed -> {e}")
else:
    print("Cannot perform OCR without pytesseract.")
