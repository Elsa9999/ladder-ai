# -*- coding: utf-8 -*-
"""
Quality Gate: Block Number Conflict Validator
Ensures that no two blocks in the same CPU share the same BlockType and Block Number.
"""
import os
import sys
import xml.etree.ElementTree as ET

# Ensure UTF-8 console output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, "projects", "Mixing_Nuoc_Tuong_Maggi_2026", "output")
IMPORT_DIR = os.path.join(ROOT, "projects", "Mixing_Nuoc_Tuong_Maggi_2026", "tia_import")

def get_block_info(xml_path):
    """
    Parses a TIA XML block file and extracts name, type, and number.
    """
    if not os.path.exists(xml_path):
        return None
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        block_element = None
        block_type = None
        
        # Iterate over all elements to find the block type element namespace-independently
        for elem in root.iter():
            local_tag = elem.tag.split('}')[-1]
            if local_tag.startswith("SW.Blocks."):
                block_element = elem
                block_type = local_tag.split('.')[-1]
                # Normalize InstanceDB/GlobalDB to DB for number space collision
                if block_type in ("InstanceDB", "GlobalDB"):
                    block_type = "DB"
                break
                
        if block_element is None:
            return None
            
        number_elem = block_element.find(".//{*}AttributeList/{*}Number")
        name_elem = block_element.find(".//{*}AttributeList/{*}Name")
        
        if number_elem is not None and name_elem is not None:
            return {
                "name": name_elem.text.strip(),
                "type": block_type,
                "number": int(number_elem.text.strip())
            }
    except Exception as e:
        print(f"  [ERROR] Lỗi parse XML file {os.path.basename(xml_path)}: {str(e)}")
    return None

def classify_output_file(filename):
    """
    Classifies a flat output XML file into PLC1 or PLC2.
    """
    fn = filename.lower()
    if "hmi" in fn and "textlist" in fn:
        return None # HMI text lists are not PLC blocks
    if fn == "io_map.json" or fn == "logic_analysis.md" or fn.endswith(".md"):
        return None
        
    # PLC1 indicators
    if "plc1" in fn or "plc_1" in fn or "bon1" in fn or "bon2" in fn or "bonchua" in fn or "filter" in fn:
        return "PLC1"
    # OB1_Main.xml in output represents PLC1's Main
    if fn == "ob1_main.xml":
        return "PLC1"
        
    # PLC2 indicators
    if "plc2" in fn or "plc_2" in fn or "bon3" in fn or "bon4" in fn or "holding_register" in fn:
        return "PLC2"
        
    return None

def validate_directory(dir_path, is_output=False):
    """
    Validates a directory for block number duplicates.
    """
    print(f"Validating block numbers in: {os.path.relpath(dir_path, ROOT)}")
    
    # cpu -> (block_type, number) -> list of block_info
    database = {
        "PLC1": {},
        "PLC2": {}
    }
    
    if is_output:
        for f in os.listdir(dir_path):
            if not f.endswith(".xml"):
                continue
            cpu = classify_output_file(f)
            if not cpu:
                continue
            
            info = get_block_info(os.path.join(dir_path, f))
            if not info:
                continue
                
            key = (info["type"], info["number"])
            if key not in database[cpu]:
                database[cpu][key] = []
            info["filename"] = f
            database[cpu][key].append(info)
    else:
        # For tia_import, we have CPU directories PLC_1_Mixing_Import and PLC_2_Mixing_Import
        for sub in os.listdir(dir_path):
            sub_path = os.path.join(dir_path, sub)
            if not os.path.isdir(sub_path):
                continue
            cpu = None
            if "plc_1" in sub.lower() or "plc1" in sub.lower():
                cpu = "PLC1"
            elif "plc_2" in sub.lower() or "plc2" in sub.lower():
                cpu = "PLC2"
                
            if not cpu:
                continue
                
            for f in os.listdir(sub_path):
                if not f.endswith(".xml") or f == "PLC_Tags.xml":
                    continue
                info = get_block_info(os.path.join(sub_path, f))
                if not info:
                    continue
                    
                key = (info["type"], info["number"])
                if key not in database[cpu]:
                    database[cpu][key] = []
                info["filename"] = f
                database[cpu][key].append(info)
                
    # Check for duplicates
    has_duplicates = False
    for cpu, cpu_blocks in database.items():
        for (block_type, number), blocks in cpu_blocks.items():
            if len(blocks) > 1:
                has_duplicates = True
                print(f"  [FAIL] XUNG ĐỘT SỐ KHỐI trên {cpu}:")
                print(f"    BlockType: {block_type}, Number: {number}")
                for b in blocks:
                    print(f"      - Block: '{b['name']}' (File: {b['filename']})")
                    
    return not has_duplicates

def run_block_validation():
    print("============================================================")
    print(" KHỞI CHẠY BỘ KIỂM TRA TRÙNG SỐ KHỐI PLC (BLOCK NUMBER CHECK)")
    print("============================================================")
    
    success = True
    
    # 1. Validate output directory
    if os.path.exists(OUTPUT_DIR):
        if not validate_directory(OUTPUT_DIR, is_output=True):
            success = False
    else:
        print(f"Warning: Output directory does not exist: {OUTPUT_DIR}")
        
    # 2. Validate tia_import directory
    if os.path.exists(IMPORT_DIR):
        if not validate_directory(IMPORT_DIR, is_output=False):
            success = False
    else:
        print(f"Warning: Import directory does not exist: {IMPORT_DIR}")
        
    print("============================================================")
    if success:
        print("  [PASS] Không phát hiện bất kỳ xung đột trùng BlockType + Number nào.")
        print("============================================================")
        return True
    else:
        print("  [FAIL] Phát hiện xung đột trùng số khối trên cùng CPU!")
        print("============================================================")
        return False

if __name__ == "__main__":
    if not run_block_validation():
        sys.exit(1)
    sys.exit(0)
