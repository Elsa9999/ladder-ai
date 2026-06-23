import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

for idx in [1, 2, 3, 4]:
    path = f"D:\\AI_Agent_PLC_LADDER_ONLY\\scratch\\bon_tron_{idx}_export.xml"
    tree = ET.parse(path)
    root = tree.getroot()
    
    print(f"\n=== BỒN TRỘN {idx} ===")
    for elem in root.iter():
        tag_local = elem.tag.split('}')[-1]
        if tag_local.endswith("SymbolLibrary"):
            attrs = elem.find("AttributeList")
            if attrs is not None:
                name = attrs.find("ObjectName").text
                left = int(attrs.find("Left").text)
                top = int(attrs.find("Top").text)
                w = int(attrs.find("Width").text)
                h = int(attrs.find("Height").text)
                
                # Check for valve-like dimensions (w < 50 and h < 50) and top < 250 (upper part of screen)
                if w < 50 and h < 50 and top < 250:
                    # Find closest label
                    labels = []
                    for lbl_el in root.iter():
                        lbl_local = lbl_el.tag.split('}')[-1]
                        if lbl_local.endswith("TextField"):
                            lbl_attrs = lbl_el.find("AttributeList")
                            if lbl_attrs is not None:
                                lbl_name = lbl_attrs.find("ObjectName").text
                                lbl_left = int(lbl_attrs.find("Left").text)
                                lbl_top = int(lbl_attrs.find("Top").text)
                                lbl_w = int(lbl_attrs.find("Width").text)
                                lbl_h = int(lbl_attrs.find("Height").text)
                                txt = ""
                                mult = lbl_el.find(".//{*}MultilingualTextItem")
                                if mult is not None:
                                    txt_el = mult.find(".//{*}Text")
                                    if txt_el is not None:
                                        txt = "".join(txt_el.itertext()).strip()
                                labels.append((lbl_left, lbl_top, lbl_w, lbl_h, txt))
                                
                    closest_lbl = "None"
                    min_d = 9999
                    cx = left + w/2
                    cy = top + h/2
                    for lx, ly, lw, lh, txt in labels:
                        if txt:
                            d = ((cx - (lx+lw/2))**2 + (cy - (ly+lh/2))**2)**0.5
                            if d < min_d:
                                min_d = d
                                closest_lbl = f"'{txt}' at ({lx},{ly})"
                                
                    print(f"  SL: '{name}' at ({left},{top}) size {w}x{h} | Closest label: {closest_lbl} (dist {round(min_d,1)})")
