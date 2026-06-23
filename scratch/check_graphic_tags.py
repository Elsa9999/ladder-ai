# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os

plc1_tags_path = r"D:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\output\PLC_Tags_PLC1.xml"
plc2_tags_path = r"D:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\output\PLC_Tags_PLC2.xml"

def parse_plc_tags(path):
    tags = {}
    if not os.path.exists(path):
        return tags
    tree = ET.parse(path)
    root = tree.getroot()
    for tag_el in root.iter():
        if tag_el.tag.endswith("SW.Tags.PlcTag"):
            name = tag_el.find(".//{*}Name").text
            dtype = tag_el.find(".//{*}DataTypeName").text
            addr = tag_el.find(".//{*}LogicalAddress").text
            tags[name] = {"DataType": dtype, "LogicalAddress": addr}
    return tags

plc1_tags = parse_plc_tags(plc1_tags_path)
plc2_tags = parse_plc_tags(plc2_tags_path)

proposed_plc1 = [
    # A. MUC DICH BON
    "HMI_Anim_Bon1_MucDich", "HMI_Anim_Bon2_MucDich", "HMI_Anim_BonChua1_MucDich", "HMI_Anim_BonChua2_MucDich",
    # B. CANH KHUAY
    "HMI_Anim_Bon1_Frame", "HMI_Anim_Bon2_Frame",
    # C. VAN BON TRON Bon 1 & Bon 2
    "V3230_Nuoc_Bon1", "V3232_Xa_Bon1", "V3233_Xa_Bon1", "V3234_Xa_Bon1",
    "V3235_Nuoc_Bon2", "V3237_Xa_Bon2", "V3238_Xa_Bon2", "V3239_Xa_Bon2",
    # D. BON CHUA, HEAT EXCHANGER, FILTER
    "V3331_Xa_BonChua1", "V3332_Xa_BonChua1", "V3333_DieuHuong_BonChua1", "V3334_DieuHuong_BonChua1", "V3335_DieuHuong_BonChua1",
    "V3338_Xa_BonChua2", "V3339_Xa_BonChua2", "V3340_Duong_Filter", "V3341_Duong_Filter",
    # E. BOM
    "Pump3264_Chuyen_Nhanh1", "Pump3361_LuanChuyen_BonChua1", "Pump3362_Xa_BonChua1", "Pump3364_Filter", "Pump3365_Filter"
]

proposed_plc2 = [
    # A. MUC DICH BON
    "HMI_Anim_Bon4_MucDich", "HMI_Anim_Bon3_MucDich",
    # B. CANH KHUAY
    "HMI_Anim_Bon4_Frame", "HMI_Anim_Bon3_Frame",
    # C. VAN BON TRON Bon 4 & Bon 3
    "V3245_Nuoc_Bon4", "V3247_Xa_Bon4", "V3248_Xa_Bon4", "V3249_Xa_Bon4",
    "V3240_Nuoc_Bon3", "V3242_Xa_Bon3", "V3243_Xa_Bon3", "V3244_Xa_Bon3",
    # E. BOM
    "Pump3265_Chuyen_Nhanh2"
]

print("=== CHECKING PLC1 TAGS ===")
for tag in proposed_plc1:
    if tag in plc1_tags:
        print(f"  [FOUND] {tag}: {plc1_tags[tag]['DataType']} at {plc1_tags[tag]['LogicalAddress']}")
    else:
        print(f"  [MISSING] {tag} NOT FOUND IN PLC1!")

print("\n=== CHECKING PLC2 TAGS ===")
for tag in proposed_plc2:
    if tag in plc2_tags:
        print(f"  [FOUND] {tag}: {plc2_tags[tag]['DataType']} at {plc2_tags[tag]['LogicalAddress']}")
    else:
        print(f"  [MISSING] {tag} NOT FOUND IN PLC2!")
