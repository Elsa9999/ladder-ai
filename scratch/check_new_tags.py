import os
import xml.etree.ElementTree as ET

plc1_tags_file = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\post_import_export_manual\PLC_1\PLC_Tags.xml"

new_tags = {
    "WT_DAU_NOI_01_MODE_SAFETY": [
        "HMI_Run_Enable", "PLC1_Loi_Tong", "PLC1_Loi_Truyen_Thong",
        "HMI_Reset_Alarm", "Nut_Reset_Eff", "HMI_Che_Do_Manual",
        "PLC1_Manual_Mode_Active"
    ],
    "WT_DAU_NOI_02_PID_VFD": [
        "VFD_Bon2_Run_Man", "VFD_Bon2_Dao_Chieu_Man", "VFD_Bon2_Toc_Do_AO_Man",
        "PID_Bon2_ManualEnable", "PID_Bon2_ManualValue"
    ]
}

def load_tags_from_xml(xml_path):
    if not os.path.exists(xml_path):
        print(f"Error: {xml_path} does not exist!")
        return set()
    tree = ET.parse(xml_path)
    root = tree.getroot()
    tags = set()
    for elem in root.iter():
        if elem.tag.endswith("PlcTag"):
            name_attr = elem.attrib.get("Name")
            if name_attr:
                tags.add(name_attr)
            else:
                name_elem = elem.find(".//Name")
                if name_elem is not None and name_elem.text:
                    tags.add(name_elem.text.strip())
    return tags

plc1_existing = load_tags_from_xml(plc1_tags_file)

print(f"Loaded {len(plc1_existing)} tags from PLC1.")

for table_name, tags in new_tags.items():
    print(f"\nChecking Table: {table_name}")
    missing = []
    for tag in tags:
        if tag not in plc1_existing:
            missing.append(tag)
    if missing:
        print(f"  [MISSING] {len(missing)} tag(s):")
        for m in missing:
            print(f"    - {m}")
    else:
        print("  [PASS] All new tags exist in PLC1.")
