import re

file_path = "projects/Mixing_Nuoc_Tuong_Maggi_2026/prepare_tia_import_sets.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Thay thế Modbus RTU bồn 2 bằng logic Single Call chuẩn
vfd_rtu_logic = """    # 2. Modbus RTU Sequencer (iStep 0..3)
    main.add_network("VFD Bon 2 Modbus - Reset MBCL_Trigger chu ky truoc", [
        ("ResetCoil", "VFD_Bon2_MBCL_Trigger")
    ])
    main.add_network("VFD Bon 2 Modbus - Trigger MB_COMM_LOAD khi delay contactor xong", [
        ("NO", "FirstScan"),
        ("SetCoil", "VFD_Bon2_MBCL_Trigger")
    ])
    main.add_network("VFD Bon 2 Modbus - Khoi tao RS-485", [
        ("GENERIC", "MB_COMM_LOAD", {
            "REQ": "VFD_Bon2_MBCL_Trigger",
            "PORT": "269",
            "BAUD": "9600",
            "PARITY": "2",
            "MB_DB": "MB_MASTER_DB"
        }, {
            "DONE": "VFD_Bon2_MBCL_Done",
            "ERROR": "VFD_Bon2_MBCL_Error",
            "STATUS": "VFD_Bon2_MBCL_Status"
        }, {"Version": "2.1"}, "MB_COMM_LOAD_DB")
    ])
    main.add_network("VFD Bon 2 Modbus - SET CommReady khi MBCL Done", [
        ("NO", "VFD_Bon2_MBCL_Done"),
        ("SetCoil", "VFD_Bon2_Comm_Ready"),
        ("SetCoil", "VFD_Bon2_Comm_Active")
    ])
    main.add_network("VFD Bon 2 Modbus - Reset Ready va Active khi loi MBCL", [
        ("NO", "VFD_Bon2_MBCL_Error"),
        ("ResetCoil", "VFD_Bon2_Comm_Ready"),
        ("ResetCoil", "VFD_Bon2_Comm_Active")
    ])
    main.add_network("VFD Bon 2 Modbus - Reset Ready va Active khi mat Comm_Active", [
        ("NC", "VFD_Bon2_Comm_Active"),
        ("ResetCoil", "VFD_Bon2_Comm_Ready")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 0 MODE", [
        ("CMP_EQ", "VFD_Bon2_iStep", "0"),
        ("MOVE", "1", "VFD_Bon2_MB_Mode")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 0 DATA_ADDR", [
        ("CMP_EQ", "VFD_Bon2_iStep", "0"),
        ("MOVE", "48502", "VFD_Bon2_MB_DataAddr")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 0 DATA_LEN", [
        ("CMP_EQ", "VFD_Bon2_iStep", "0"),
        ("MOVE", "1", "VFD_Bon2_MB_DataLen")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 0 Write Buffer", [
        ("CMP_EQ", "VFD_Bon2_iStep", "0"),
        ("MOVE", "VFD_Bon2_MB_ControlWord", "VFD_Bon2_MB_DataBuffer")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 1 MODE", [
        ("CMP_EQ", "VFD_Bon2_iStep", "1"),
        ("MOVE", "1", "VFD_Bon2_MB_Mode")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 1 DATA_ADDR", [
        ("CMP_EQ", "VFD_Bon2_iStep", "1"),
        ("MOVE", "48503", "VFD_Bon2_MB_DataAddr")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 1 DATA_LEN", [
        ("CMP_EQ", "VFD_Bon2_iStep", "1"),
        ("MOVE", "1", "VFD_Bon2_MB_DataLen")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 1 Write Buffer", [
        ("CMP_EQ", "VFD_Bon2_iStep", "1"),
        ("MOVE", "VFD_Bon2_MB_FreqSetpoint", "VFD_Bon2_MB_DataBuffer")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 2 MODE", [
        ("CMP_EQ", "VFD_Bon2_iStep", "2"),
        ("MOVE", "0", "VFD_Bon2_MB_Mode")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 2 DATA_ADDR", [
        ("CMP_EQ", "VFD_Bon2_iStep", "2"),
        ("MOVE", "38501", "VFD_Bon2_MB_DataAddr")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 2 DATA_LEN", [
        ("CMP_EQ", "VFD_Bon2_iStep", "2"),
        ("MOVE", "1", "VFD_Bon2_MB_DataLen")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 3 MODE", [
        ("CMP_EQ", "VFD_Bon2_iStep", "3"),
        ("MOVE", "0", "VFD_Bon2_MB_Mode")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 3 DATA_ADDR", [
        ("CMP_EQ", "VFD_Bon2_iStep", "3"),
        ("MOVE", "38502", "VFD_Bon2_MB_DataAddr")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 3 DATA_LEN", [
        ("CMP_EQ", "VFD_Bon2_iStep", "3"),
        ("MOVE", "1", "VFD_Bon2_MB_DataLen")
    ])
    main.add_network("VFD Bon 2 Modbus - Set REQ khi co trigger", [
        ("NC", "VFD_Bon2_MB_Busy"),
        ("SetCoil", "VFD_Bon2_MB_Req")
    ])
    main.add_network("VFD Bon 2 Modbus - Reset REQ khi Busy", [
        ("NO", "VFD_Bon2_MB_Busy"),
        ("ResetCoil", "VFD_Bon2_MB_Req")
    ])
    main.add_network("VFD Bon 2 Modbus - Master Single Call", [
        ("NO", "VFD_Bon2_Comm_Active"),
        ("NO", "VFD_Bon2_Comm_Ready"),
        ("GENERIC", "MB_MASTER", {
            "REQ": "VFD_Bon2_MB_Req",
            "MB_ADDR": "1",
            "MODE": "VFD_Bon2_MB_Mode",
            "DATA_ADDR": "VFD_Bon2_MB_DataAddr",
            "DATA_LEN": "VFD_Bon2_MB_DataLen",
            "DATA_PTR": "VFD_Bon2_MB_DataBuffer"
        }, {
            "DONE": "VFD_Bon2_MB_Done",
            "BUSY": "VFD_Bon2_MB_Busy",
            "ERROR": "VFD_Bon2_MB_Error",
            "STATUS": "VFD_Bon2_MB_Status"
        }, {"Version": "2.2"}, "MB_MASTER_DB")
    ])
    main.add_network("VFD Bon 2 Modbus - Read Step 2 Buffer Copy", [
        ("CMP_EQ", "VFD_Bon2_iStep", "2"),
        ("NO", "VFD_Bon2_MB_Done"),
        ("MOVE", "VFD_Bon2_MB_DataBuffer", "VFD_Bon2_MB_StatusWord")
    ])
    main.add_network("VFD Bon 2 Modbus - Read Step 3 Buffer Copy", [
        ("CMP_EQ", "VFD_Bon2_iStep", "3"),
        ("NO", "VFD_Bon2_MB_Done"),
        ("MOVE", "VFD_Bon2_MB_DataBuffer", "VFD_Bon2_MB_FreqActual")
    ])
    main.add_network("VFD Bon 2 Modbus - Tang iStep khi Done", [
        ("NO", "VFD_Bon2_MB_Done"),
        ("MATH_ADD", "VFD_Bon2_iStep", "1", "VFD_Bon2_iStep")
    ])
    main.add_network("VFD Bon 2 Modbus - Reset iStep ve 0 khi vuot nguong", [
        ("CMP_GE", "VFD_Bon2_iStep", "4"),
        ("MOVE", "0", "VFD_Bon2_iStep")
    ])"""

# Tìm điểm đầu và cuối của block Modbus RTU cũ để thay thế
pattern = r'# 2\. Modbus RTU Sequencer \(iStep 0\.\.3\).*?# 3\. Giao tiếp Modbus TCP PLC1 - PLC2'
content_new, count = re.subn(pattern, vfd_rtu_logic + "\n\n    # 3. Giao tiếp Modbus TCP PLC1 - PLC2", content, flags=re.DOTALL)
print(f"Substituted VFD Modbus logic: {count}")

# 2. Thêm logic gọi FC_VFD_Bon2_Hybrid trong build_main_for_plc1()
fc_call_logic = '    main.add_network("PLC1 - gọi logic VFD Bồn 2 Hybrid", [("CALL_FC", "FC_VFD_Bon2_Hybrid")])'
if "FC_VFD_Bon2_Hybrid" not in content_new:
    content_new = content_new.replace(
        'main.add_network("PLC1 - cập nhật mirror HMI", [("CALL_FC", "FC_HMI_Mirror_PLC1")])',
        fc_call_logic + '\n    main.add_network("PLC1 - cập nhật mirror HMI", [("CALL_FC", "FC_HMI_Mirror_PLC1")])'
    )
    print("Added call to FC_VFD_Bon2_Hybrid")

# 3. Thêm FC_VFD_Bon2_Hybrid.xml vào copy list của PLC1
if '"FC_VFD_Bon2_Hybrid.xml"' not in content_new:
    content_new = content_new.replace(
        '"FC_HMI_Animation_PLC1.xml",',
        '"FC_HMI_Animation_PLC1.xml",\n        "FC_VFD_Bon2_Hybrid.xml",'
    )
    print("Added FC_VFD_Bon2_Hybrid.xml to copy list")

# 4. Loại bỏ prefix AI_ khỏi các tag logic (trừ AI_Tags và AI_Tags.xml)
content_new = re.sub(r'"AI_(?!Tags\b)([^"]+)"', r'"\1"', content_new)
content_new = re.sub(r'\'AI_(?!Tags\b)([^\']+)\'', r'\'\1\'', content_new)
print("Stripped AI_ prefixes from tag names")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content_new)
print("Updated prepare_tia_import_sets.py successfully.")
