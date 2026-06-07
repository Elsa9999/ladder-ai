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

print("\n============================================================")
if is_overall_success:
    print(" KẾT LUẬN CUỐI: TẤT CẢ IMPORT SETS ĐỀU PASS ĐẠT CHUẨN!")
    print("============================================================")
    sys.exit(0)
else:
    print(" KẾT LUẬN CUỐI: CÓ LỖI XẢY RA, CẦN KIỂM TRA LẠI!")
    print("============================================================")
    sys.exit(1)
