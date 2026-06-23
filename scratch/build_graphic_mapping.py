# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import csv
import math
import os

screen_xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen_1_readback.xml"
csv_out_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\graphic_mapping_dry_run.csv"

# Parse screen readback
tree = ET.parse(screen_xml_path)
root = tree.getroot()

# 1. Parse TextFields (labels)
labels = []
for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    if tag_local == "Hmi.Screen.TextField":
        attrs = elem.find("AttributeList")
        if attrs is not None:
            obj_name = attrs.find("ObjectName").text if attrs.find("ObjectName") is not None else ""
            left = int(attrs.find("Left").text) if attrs.find("Left") is not None else 0
            top = int(attrs.find("Top").text) if attrs.find("Top") is not None else 0
            w = int(attrs.find("Width").text) if attrs.find("Width") is not None else 0
            h = int(attrs.find("Height").text) if attrs.find("Height") is not None else 0
            
            # Find multilingual text value
            text_val = ""
            mult_txt = elem.find(".//MultilingualTextItem")
            if mult_txt is not None:
                txt_elem = mult_txt.find("AttributeList/Text")
                if txt_elem is not None:
                    raw_text = "".join(txt_elem.itertext()).strip()
                    text_val = raw_text
            
            labels.append({
                "ObjectName": obj_name,
                "Left": left,
                "Top": top,
                "Width": w,
                "Height": h,
                "Text": text_val
            })

# 2. Parse GraphicIOFields
graphic_fields = []
for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    if tag_local == "Hmi.Screen.GraphicIOField":
        attrs = elem.find("AttributeList")
        if attrs is not None:
            obj_name = attrs.find("ObjectName").text if attrs.find("ObjectName") is not None else ""
            left = int(attrs.find("Left").text) if attrs.find("Left") is not None else 0
            top = int(attrs.find("Top").text) if attrs.find("Top") is not None else 0
            w = int(attrs.find("Width").text) if attrs.find("Width") is not None else 0
            h = int(attrs.find("Height").text) if attrs.find("Height") is not None else 0
            
            pic_list = "None"
            links = elem.find("LinkList")
            if links is not None:
                pic_el = links.find(".//PictureList") or links.find(".//Picture")
                if pic_el is not None:
                    name_el = pic_el.find("Name")
                    if name_el is not None:
                        pic_list = name_el.text
            
            # Check current Mode
            mode = attrs.find("Mode").text if attrs.find("Mode") is not None else "Input/output"
            
            graphic_fields.append({
                "ObjectName": obj_name,
                "Left": left,
                "Top": top,
                "Width": w,
                "Height": h,
                "GraphicList": pic_list,
                "CurrentMode": mode
            })

# 3. Define the proposed HMI mapping (as requested by user)
proposed_mappings = {
    # A. MUC DICH BON
    "Graphic I/O field_10": ("HMI_Anim_Bon1_MucDich", "PLC1", "HMI_Connection_1", "Int"),
    "Graphic I/O field_3":  ("HMI_Anim_Bon2_MucDich", "PLC1", "HMI_Connection_1", "Int"),
    "Graphic I/O field_4":  ("HMI_Anim_Bon4_MucDich", "PLC2", "HMI_Connection_2", "Int"),
    "Graphic I/O field_6":  ("HMI_Anim_Bon3_MucDich", "PLC2", "HMI_Connection_2", "Int"),
    "Graphic I/O field_9":  ("HMI_Anim_BonChua1_MucDich", "PLC1", "HMI_Connection_1", "Int"),
    "Graphic I/O field_2":  ("HMI_Anim_BonChua2_MucDich", "PLC1", "HMI_Connection_1", "Int"),
    # B. CANH KHUAY
    "Graphic I/O field_38": ("HMI_Anim_Bon1_Frame", "PLC1", "HMI_Connection_1", "Int"),
    "Graphic I/O field_39": ("HMI_Anim_Bon2_Frame", "PLC1", "HMI_Connection_1", "Int"),
    "Graphic I/O field_40": ("HMI_Anim_Bon4_Frame", "PLC2", "HMI_Connection_2", "Int"),
    "Graphic I/O field_41": ("HMI_Anim_Bon3_Frame", "PLC2", "HMI_Connection_2", "Int"),
    # C. VAN BON TRON
    # Bon 1
    "Graphic I/O field_5":  ("V3230_Nuoc_Bon1", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_8":  ("V3232_Xa_Bon1", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_7":  ("V3233_Xa_Bon1", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_11": ("V3234_Xa_Bon1", "PLC1", "HMI_Connection_1", "Bool"),
    # Bon 2
    "Graphic I/O field_12": ("V3235_Nuoc_Bon2", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_15": ("V3237_Xa_Bon2", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_17": ("V3238_Xa_Bon2", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_16": ("V3239_Xa_Bon2", "PLC1", "HMI_Connection_1", "Bool"),
    # Bon 4
    "Graphic I/O field_13": ("V3245_Nuoc_Bon4", "PLC2", "HMI_Connection_2", "Bool"),
    "Graphic I/O field_18": ("V3247_Xa_Bon4", "PLC2", "HMI_Connection_2", "Bool"),
    "Graphic I/O field_22": ("V3248_Xa_Bon4", "PLC2", "HMI_Connection_2", "Bool"),
    "Graphic I/O field_20": ("V3249_Xa_Bon4", "PLC2", "HMI_Connection_2", "Bool"),
    # Bon 3
    "Graphic I/O field_14": ("V3240_Nuoc_Bon3", "PLC2", "HMI_Connection_2", "Bool"),
    "Graphic I/O field_19": ("V3242_Xa_Bon3", "PLC2", "HMI_Connection_2", "Bool"),
    "Graphic I/O field_23": ("V3243_Xa_Bon3", "PLC2", "HMI_Connection_2", "Bool"),
    "Graphic I/O field_21": ("V3244_Xa_Bon3", "PLC2", "HMI_Connection_2", "Bool"),
    # D. BON CHUA, HEAT EXCHANGER, FILTER
    "Graphic I/O field_24": ("V3331_Xa_BonChua1", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_30": ("V3332_Xa_BonChua1", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_27": ("V3333_DieuHuong_BonChua1", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_25": ("V3334_DieuHuong_BonChua1", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_26": ("V3335_DieuHuong_BonChua1", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_28": ("V3338_Xa_BonChua2", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_31": ("V3339_Xa_BonChua2", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_32": ("V3340_Duong_Filter", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_29": ("V3341_Duong_Filter", "PLC1", "HMI_Connection_1", "Bool"),
    # E. BOM
    "Graphic I/O field_33": ("Pump3264_Chuyen_Nhanh1", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_37": ("Pump3265_Chuyen_Nhanh2", "PLC2", "HMI_Connection_2", "Bool"),
    "Graphic I/O field_34": ("Pump3361_LuanChuyen_BonChua1", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_1":  ("Pump3362_Xa_BonChua1", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_35": ("Pump3364_Filter", "PLC1", "HMI_Connection_1", "Bool"),
    "Graphic I/O field_36": ("Pump3365_Filter", "PLC1", "HMI_Connection_1", "Bool")
}

# 4. Process matching and generate dry-run output
with open(csv_out_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "ObjectName", "Left", "Top", "Width", "Height", "GraphicList", "ProposedTag",
        "PLC_Owner", "Connection", "DataType", "CurrentMode", "ProposedMode",
        "Confidence", "NearestLabel"
    ])
    
    for field in sorted(graphic_fields, key=lambda x: x["ObjectName"]):
        name = field["ObjectName"]
        left = field["Left"]
        top = field["Top"]
        w = field["Width"]
        h = field["Height"]
        glist = field["GraphicList"]
        cur_mode = field["CurrentMode"]
        
        # Proposed values
        if name in proposed_mappings:
            tag, owner, conn, dtype = proposed_mappings[name]
        else:
            tag, owner, conn, dtype = "N/A", "N/A", "N/A", "N/A"
            
        # Find nearest label
        nearest_lbl = "None"
        min_dist = float("inf")
        # Center of GraphicIOField
        cx = left + w / 2
        cy = top + h / 2
        
        for lbl in labels:
            lx = lbl["Left"] + lbl["Width"] / 2
            ly = lbl["Top"] + lbl["Height"] / 2
            dist = math.sqrt((cx - lx)**2 + (cy - ly)**2)
            if dist < min_dist:
                min_dist = dist
                nearest_lbl = f"{lbl['ObjectName']} ('{lbl['Text']}') at ({lbl['Left']},{lbl['Top']})"
        
        # Proposed Mode must always be Output
        prop_mode = "Output"
        
        writer.writerow([
            name, left, top, w, h, glist, tag,
            owner, conn, dtype, cur_mode, prop_mode,
            "100%" if name in proposed_mappings else "0%", nearest_lbl
        ])

print(f"Generated {csv_out_path} with nearest labels and proposed bindings.")
