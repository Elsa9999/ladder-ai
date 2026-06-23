import os
import xml.etree.ElementTree as ET

plc1_tags_file = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\post_import_export_manual\PLC_1\PLC_Tags.xml"
plc2_tags_file = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\post_import_export_manual\PLC_2\PLC_Tags.xml"

wt_configs = {
    "PLC1": {
        "WT_DAU_NOI_01_MODE_SAFETY": [
            "HMI_Che_Do_Thi", "Nut_EStop", "Nut_EStop_HMI", "Nut_EStop_Eff",
            "PLC1_EStop_Latch", "PLC1_Stop_Active", "HMI_VFD_Bon2_Comm_Enable",
            "HMI_VFD_Bon2_Real_Enable", "VFD_Bon2_Comm_Active", "VFD_Bon2_Comm_Ready",
            "VFD_Bon2_Real_Active", "VFD_Bon2_Mode_Invalid", "VFD_Bon2_Contactor", "VFD_Bon2_Contactor_Delay_Done"
        ],
        "WT_DAU_NOI_02_PID_VFD": [
            "HMI_PID_Bon2_Dau_Noi_Enable", "HMI_SP_PLC1_Toc_Do_Bon2_Main",
            "VFD_Bon2_Actual_Speed_Feedback", "PID_Bon2_SP", "PID_Bon2_PV_Eff",
            "PID_Bon2_Enable_Eff", "PID_Bon2_Err", "PID_Bon2_CV", "PID_Bon2_State",
            "PID_Bon2_Error", "PID_Bon2_ErrorBits", "VFD_Bon2_Should_Run",
            "VFD_Bon2_Run_Cmd", "VFD_Bon2_Dao_Chieu_Cmd", "VFD_Bon2_Toc_Do_Cmd",
            "VFD_Bon2_Run_Safe", "VFD_Bon2_Run", "VFD_Bon2_Dao_Chieu", "VFD_Bon2_Toc_Do_AO", "VFD_Bon2_Contactor"
        ],
        "WT_DAU_NOI_03_ATV12_MODBUS": [
            "VFD_Bon2_iStep", "VFD_Bon2_MB_ControlWord", "VFD_Bon2_MB_FreqSetpoint",
            "VFD_Bon2_MB_StatusWord", "VFD_Bon2_MB_FreqActual", "VFD_Bon2_MB_Req",
            "VFD_Bon2_MB_Mode", "VFD_Bon2_MB_DataAddr", "VFD_Bon2_MB_DataLen",
            "VFD_Bon2_MB_Busy", "VFD_Bon2_MB_Done", "VFD_Bon2_MB_Error",
            "VFD_Bon2_MB_Status", "VFD_Bon2_MBCL_Trigger", "VFD_Bon2_MBCL_Done",
            "VFD_Bon2_MBCL_Error", "VFD_Bon2_MBCL_Status", "VFD_Bon2_Comm_Ready"
        ],
        "WT_DAU_NOI_04_PLC_TO_PLC": [
            "PLC1_State", "PLC1_Auto_Enable", "PLC2_State_Recv", "MB_TCP_iStep",
            "MB_TCP_REQ", "MB_TCP_DONE", "MB_TCP_ERROR", "MB_TCP_BUSY",
            "MB_TCP_STATUS", "MB_TCP_Mode", "MB_TCP_DataAddr", "MB_TCP_DataLen",
            "PLC1_Heartbeat_Timeout"
        ]
    },
    "PLC2": {
        "WT_DAU_NOI_05_PLC2_SERVER": [
            "PLC2_State", "PLC2_Auto_Enable", "PLC2_Stop_Active", "MB_TCP_Server_Error",
            "MB_TCP_Server_Status", "MB_TCP_Server_NDR", "MB_TCP_Server_DR",
            "PLC1_Heartbeat_Last", "PLC1_Heartbeat_Changed", "PLC2_Heartbeat_Timeout"
        ]
    }
}

def load_tags_from_xml(xml_path):
    if not os.path.exists(xml_path):
        print(f"Error: {xml_path} does not exist!")
        return set()
    tree = ET.parse(xml_path)
    root = tree.getroot()
    tags = set()
    # TIA Openness XML namespace is ignored/handled by wildcards or tags
    # Find all PlcTag elements
    for elem in root.iter():
        if elem.tag.endswith("PlcTag"):
            # find Name attribute or element
            name_attr = elem.attrib.get("Name")
            if name_attr:
                tags.add(name_attr)
            else:
                name_elem = elem.find(".//Name")
                if name_elem is not None and name_elem.text:
                    tags.add(name_elem.text.strip())
    return tags

plc1_existing = load_tags_from_xml(plc1_tags_file)
plc2_existing = load_tags_from_xml(plc2_tags_file)

print(f"Loaded {len(plc1_existing)} tags from PLC1 tags file.")
print(f"Loaded {len(plc2_existing)} tags from PLC2 tags file.")

for plc_name, tables in wt_configs.items():
    print(f"\n=== Checking {plc_name} ===")
    existing_tags = plc1_existing if plc_name == "PLC1" else plc2_existing
    for table_name, tags in tables.items():
        print(f"\nWatch Table: {table_name} ({len(tags)} tags)")
        missing = []
        for tag in tags:
            if tag not in existing_tags:
                missing.append(tag)
        if missing:
            print(f"  [MISSING] {len(missing)} tag(s):")
            for m in missing:
                print(f"    - {m}")
        else:
            print(f"  [PASS] All {len(tags)} tags exist.")
