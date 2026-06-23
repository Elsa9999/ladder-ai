# -*- coding: utf-8 -*-
import os
import sys
import shutil
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "Ladder"))

from Agent_QA_Validator import run_qa_validator  # noqa: E402

print("============================================================")
print(" KIỂM TRA ĐỘC LẬP TỪNG THƯ MỤC IMPORT CPU")
print("============================================================")

output_dir = os.path.join(ROOT, "projects", "Mixing_Nuoc_Tuong_Maggi_2026", "output")
import_dir = os.path.join(ROOT, "projects", "Mixing_Nuoc_Tuong_Maggi_2026", "tia_import")
plc1_dir = os.path.join(import_dir, "PLC_1_Mixing_Import")
plc2_dir = os.path.join(import_dir, "PLC_2_Mixing_Import")

is_overall_success = True

# 1. Parse XML và check Component Names
print("--- 1. PARSE XML & KIỂM TRA CHẤN ĐOÁN THAM SỐ TRUYỀN THÔNG ---")
illegal_components = ["W#16#0100", "P#DB", "P#DB1", "P#DB2", "P#DB10", "P#DB11"]

for folder in [plc1_dir, plc2_dir]:
    print(f"Kiểm tra XML trong: {os.path.basename(folder)}...")
    for f in os.listdir(folder):
        if f.endswith(".xml"):
            path = os.path.join(folder, f)
            try:
                tree = ET.parse(path)
                root = tree.getroot()
                
                # Check for Component tags containing illegal values
                for comp in root.findall(".//{*}Component"):
                    name = comp.attrib.get("Name", "")
                    for illegal in illegal_components:
                        if illegal in name:
                            print(f"  [ERROR] File {f} chứa Component Name trái phép: '{name}'")
                            is_overall_success = False
                            
            except Exception as e:
                print(f"  [ERROR] Lỗi parse XML file {f}: {str(e)}")
                is_overall_success = False

# Helper to setup and cleanup temporary validation files
def run_qa_with_assets(target_folder):
    # Copy IO_Map.json
    io_map_src = os.path.join(output_dir, "IO_Map.json")
    io_map_dst = os.path.join(target_folder, "IO_Map.json")
    shutil.copy2(io_map_src, io_map_dst)
    
    # Copy/rename Main.xml to OB1_Main.xml
    main_src = os.path.join(target_folder, "Main.xml")
    main_dst = os.path.join(target_folder, "OB1_Main.xml")
    shutil.copy2(main_src, main_dst)
    
    try:
        success = run_qa_validator(target_folder)
    finally:
        # Cleanup
        if os.path.exists(io_map_dst):
            os.remove(io_map_dst)
        if os.path.exists(main_dst):
            os.remove(main_dst)
            
    return success

# 2. Chạy QA Validator độc lập trên PLC1
print("\n--- 2. CHẠY QA VALIDATOR CHO PLC_1_Mixing_Import ---")
plc1_qa_success = run_qa_with_assets(plc1_dir)
if not plc1_qa_success:
    is_overall_success = False

# 3. Chạy QA Validator độc lập trên PLC2
print("\n--- 3. CHẠY QA VALIDATOR CHO PLC_2_Mixing_Import ---")
plc2_qa_success = run_qa_with_assets(plc2_dir)
if not plc2_qa_success:
    is_overall_success = False

# 4. Kiểm tra trùng số khối PLC
print("\n--- 4. KIỂM TRA TRÙNG SỐ KHỐI PLC ---")
from validate_block_numbers import run_block_validation
if not run_block_validation():
    is_overall_success = False

# 5. Static Verifier: Kiểm tra thứ tự mạng ADD trước, CMP_GE 4 + MOVE 0 sau trong Main.xml
print("\n--- 5. KIỂM TRA THỨ TỰ MẠNG CHUYỂN BƯỚC MODBUS TRONG Main.xml ---")
main_path = os.path.join(plc1_dir, "Main.xml")
if os.path.exists(main_path):
    try:
        tree = ET.parse(main_path)
        root = tree.getroot()
        compile_units = root.findall(".//{*}SW.Blocks.CompileUnit")
        add_idx = -1
        reset_idx = -1
        for idx, cu in enumerate(compile_units):
            titles = cu.findall(".//{*}MultilingualText[@CompositionName='Title']//{*}Text")
            for t in titles:
                title_text = t.text or ""
                if "Tang iStep khi Done" in title_text:
                    add_idx = idx
                elif "Reset iStep ve 0 khi vuot nguong" in title_text:
                    reset_idx = idx
        
        if add_idx == -1:
            print("  [ERROR] Không tìm thấy mạng 'Tang iStep khi Done' trong Main.xml")
            is_overall_success = False
        else:
            print(f"  [INFO] Tìm thấy mạng 'Tang iStep khi Done' tại vị trí index {add_idx}")
            
        if reset_idx == -1:
            print("  [ERROR] Không tìm thấy mạng 'Reset iStep ve 0 khi vuot nguong' trong Main.xml")
            is_overall_success = False
        else:
            print(f"  [INFO] Tìm thấy mạng 'Reset iStep ve 0 khi vuot nguong' tại vị trí index {reset_idx}")
            
        if add_idx != -1 and reset_idx != -1:
            if add_idx < reset_idx:
                print("  [PASS] Mạng ADD đứng trước mạng Reset iStep (đúng tuần tự).")
                
                # Check contents of ADD network
                add_cu = compile_units[add_idx]
                parts = add_cu.findall(".//{*}Part")
                part_names = [p.attrib.get("Name", "") for p in parts]
                has_add = "Add" in part_names
                
                # Check target tag in ADD network
                components = add_cu.findall(".//{*}Component")
                comp_names = [c.attrib.get("Name", "") for c in components]
                has_istep = "VFD_Bon2_iStep" in comp_names
                
                if not has_add:
                    print("  [ERROR] Mạng ADD không chứa lệnh Add.")
                    is_overall_success = False
                if not has_istep:
                    print("  [ERROR] Mạng ADD không tác động lên tag VFD_Bon2_iStep.")
                    is_overall_success = False
                if has_add and has_istep:
                    print("  [PASS] Cấu trúc mạng ADD hoàn chỉnh và chính xác.")

                # Check contents of Reset network
                reset_cu = compile_units[reset_idx]
                r_parts = reset_cu.findall(".//{*}Part")
                r_part_names = [p.attrib.get("Name", "") for p in r_parts]
                has_ge = "Ge" in r_part_names
                has_move = "Move" in r_part_names
                
                # Check target tag and limit in Reset network
                r_components = reset_cu.findall(".//{*}Component")
                r_comp_names = [c.attrib.get("Name", "") for c in r_components]
                r_has_istep = "VFD_Bon2_iStep" in r_comp_names
                
                # Check limit value in Reset network
                literals = reset_cu.findall(".//{*}Access[@Scope='LiteralConstant']//{*}ConstantValue")
                literal_values = [lit.text for lit in literals]
                has_limit_4 = "4" in literal_values
                has_move_val_0 = "0" in literal_values
                
                if not has_ge:
                    print("  [ERROR] Mạng Reset không chứa so sánh Ge (>=).")
                    is_overall_success = False
                if not has_move:
                    print("  [ERROR] Mạng Reset không chứa lệnh Move.")
                    is_overall_success = False
                if not r_has_istep:
                    print("  [ERROR] Mạng Reset không tác động lên tag VFD_Bon2_iStep.")
                    is_overall_success = False
                if not has_limit_4:
                    print("  [ERROR] Mạng Reset không so sánh với ngưỡng 4.")
                    is_overall_success = False
                if not has_move_val_0:
                    print("  [ERROR] Mạng Reset không MOVE giá trị 0.")
                    is_overall_success = False
                
                if has_ge and has_move and r_has_istep and has_limit_4 and has_move_val_0:
                    print("  [PASS] Cấu trúc mạng Reset hoàn chỉnh và chính xác (ngưỡng >= 4, MOVE 0).")
            else:
                print("  [ERROR] Mạng Reset đứng TRƯỚC mạng ADD (sai trình tự!).")
                is_overall_success = False
    except Exception as e:
        print(f"  [ERROR] Lỗi phân tích tĩnh Main.xml: {str(e)}")
        is_overall_success = False
else:
    print("  [ERROR] Không tồn tại file Main.xml để kiểm tra tĩnh.")
    is_overall_success = False

# 6. Static Verifier: Kiểm tra thứ tự và cấu trúc mạng MB_COMM_LOAD / MB_MASTER
print("\n--- 6. KIỂM TRA THỨ TỰ LOGIC MB_COMM_LOAD & GATING MB_MASTER ---")
if os.path.exists(main_path):
    try:
        # Re-parse Main.xml to ensure fresh look
        tree = ET.parse(main_path)
        root = tree.getroot()
        compile_units = root.findall(".//{*}SW.Blocks.CompileUnit")
        
        reset_trig_idx = -1
        set_trig_idx = -1
        mcl_idx = -1
        mbm_idx = -1
        
        for idx, cu in enumerate(compile_units):
            titles = cu.findall(".//{*}MultilingualText[@CompositionName='Title']//{*}Text")
            for t in titles:
                title_text = t.text or ""
                if "Reset MBCL_Trigger chu ky truoc" in title_text:
                    reset_trig_idx = idx
                elif "Trigger MB_COMM_LOAD khi delay contactor xong" in title_text:
                    set_trig_idx = idx
                elif "Khoi tao RS-485" in title_text:
                    mcl_idx = idx
                elif "Master Single Call" in title_text:
                    mbm_idx = idx
        
        # Verify existence
        if reset_trig_idx == -1:
            print("  [ERROR] Không tìm thấy mạng 'Reset MBCL_Trigger chu ky truoc' trong Main.xml")
            is_overall_success = False
        else:
            print(f"  [INFO] Tìm thấy mạng 'Reset MBCL_Trigger chu ky truoc' tại vị trí index {reset_trig_idx}")
            
        if set_trig_idx == -1:
            print("  [ERROR] Không tìm thấy mạng 'Trigger MB_COMM_LOAD khi delay contactor xong' trong Main.xml")
            is_overall_success = False
        else:
            print(f"  [INFO] Tìm thấy mạng 'Trigger MB_COMM_LOAD khi delay contactor xong' tại vị trí index {set_trig_idx}")
            
        if mcl_idx == -1:
            print("  [ERROR] Không tìm thấy mạng 'Khoi tao RS-485' (MB_COMM_LOAD call) trong Main.xml")
            is_overall_success = False
        else:
            print(f"  [INFO] Tìm thấy mạng 'Khoi tao RS-485' tại vị trí index {mcl_idx}")
            
        if mbm_idx == -1:
            print("  [ERROR] Không tìm thấy mạng 'Master Single Call' (MB_MASTER call) trong Main.xml")
            is_overall_success = False
        else:
            print(f"  [INFO] Tìm thấy mạng 'Master Single Call' tại vị trí index {mbm_idx}")
            
        # Verify order
        if reset_trig_idx != -1 and set_trig_idx != -1 and mcl_idx != -1:
            if reset_trig_idx < set_trig_idx and set_trig_idx < mcl_idx:
                print("  [PASS] Trình tự COMM_LOAD chính xác: Reset Trigger -> Set Trigger -> MB_COMM_LOAD Call.")
            else:
                print(f"  [ERROR] Trình tự COMM_LOAD sai! Reset={reset_trig_idx}, Set={set_trig_idx}, Call={mcl_idx}")
                is_overall_success = False
                
        # Verify gating of MB_MASTER by CommReady (and Comm_Active)
        if mbm_idx != -1:
            mbm_cu = compile_units[mbm_idx]
            components = mbm_cu.findall(".//{*}Component")
            comp_names = [c.attrib.get("Name", "") for c in components]
            if "VFD_Bon2_Comm_Ready" in comp_names and "VFD_Bon2_Comm_Active" in comp_names:
                print("  [PASS] Khối MB_MASTER được gate bởi Comm_Active và Comm_Ready thành công.")
            else:
                print("  [ERROR] Khối MB_MASTER không được gate bởi Comm_Active và Comm_Ready!")
                is_overall_success = False
                
    except Exception as e:
        print(f"  [ERROR] Lỗi phân tích tĩnh MB_COMM_LOAD/MB_MASTER trong Main.xml: {str(e)}")
        is_overall_success = False

# Kiểm tra trong FC_VFD_Bon2_Hybrid.xml (FC70)
hybrid_path = os.path.join(plc1_dir, "FC_VFD_Bon2_Hybrid.xml")
if os.path.exists(hybrid_path):
    try:
        tree = ET.parse(hybrid_path)
        root = tree.getroot()
        
        # Check that VFD_Bon2_MBCL_Trigger and VFD_Bon2_MBCL_Active are not referenced at all
        components = root.findall(".//{*}Component")
        comp_names = [c.attrib.get("Name", "") for c in components]
        
        if "VFD_Bon2_MBCL_Trigger" in comp_names:
            print("  [ERROR] FC70 vẫn tham chiếu VFD_Bon2_MBCL_Trigger!")
            is_overall_success = False
        else:
            print("  [PASS] FC70 không tham chiếu VFD_Bon2_MBCL_Trigger (đúng quy tắc).")
            
        if "VFD_Bon2_MBCL_Active" in comp_names:
            print("  [ERROR] FC70 vẫn tham chiếu VFD_Bon2_MBCL_Active!")
            is_overall_success = False
        else:
            print("  [PASS] FC70 không tham chiếu VFD_Bon2_MBCL_Active (đúng quy tắc).")
            
        # Check that VFD_Bon2_Comm_Ready is not written to in FC70
        has_ready_write = False
        ready_uids = []
        for access in root.findall(".//{*}Access[@Scope='GlobalVariable']"):
            comps = access.findall(".//{*}Component")
            if comps and comps[0].attrib.get("Name", "") == "VFD_Bon2_Comm_Ready":
                ready_uids.append(access.attrib.get("UId", ""))
                
        # Find wires where these uids are connected as operand to Coil/SCoil/RCoil
        coils = root.findall(".//{*}Part")
        coil_uids = [c.attrib.get("UId", "") for c in coils if c.attrib.get("Name", "") in ("Coil", "SCoil", "RCoil")]
        
        # Find Move block destinations
        moves = root.findall(".//{*}Part")
        move_uids = [m.attrib.get("UId", "") for m in moves if m.attrib.get("Name", "") == "Move"]
        
        for wire in root.findall(".//{*}Wire"):
            ident = wire.find(".//{*}IdentCon")
            name_con = wire.find(".//{*}NameCon")
            if ident is not None and name_con is not None:
                i_uid = ident.attrib.get("UId", "")
                n_uid = name_con.attrib.get("UId", "")
                n_name = name_con.attrib.get("Name", "")
                if i_uid in ready_uids:
                    # check if Coil operand
                    if n_uid in coil_uids and n_name == "operand":
                        has_ready_write = True
                    # check if Move destination
                    if n_uid in move_uids and n_name.startswith("out"):
                        has_ready_write = True
                    
        if has_ready_write:
            print("  [ERROR] FC70 có hành vi ghi (Coil/Set/Reset/Move) vào VFD_Bon2_Comm_Ready!")
            is_overall_success = False
        else:
            print("  [PASS] FC70 không ghi vào VFD_Bon2_Comm_Ready (đúng quy tắc).")
            
    except Exception as e:
        print(f"  [ERROR] Lỗi phân tích tĩnh FC_VFD_Bon2_Hybrid.xml: {str(e)}")
        is_overall_success = False
else:
    print("  [ERROR] Không tồn tại file FC_VFD_Bon2_Hybrid.xml để kiểm tra tĩnh.")
    is_overall_success = False

print("\n============================================================")
if is_overall_success:
    print(" KẾT LUẬN CUỐI: TẤT CẢ IMPORT SETS ĐỀU PASS ĐẠT CHUẨN!")
    print("============================================================")
    sys.exit(0)
else:
    print(" KẾT LUẬN CUỐI: CÓ LỖI XẢY RA, CẦN KIỂM TRA LẠI!")
    print("============================================================")
    sys.exit(1)
