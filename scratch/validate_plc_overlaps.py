# -*- coding: utf-8 -*-
"""
Bộ kiểm tra trùng lấp địa chỉ (Overlap Validator) của PLC
Được làm cứng để kiểm tra tính toàn vẹn của tag, system memory, và phát hiện ghi đè trong LAD.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

# Đảm bảo hiển thị Tiếng Việt trên Windows Console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, "projects", "Mixing_Nuoc_Tuong_Maggi_2026", "output")
IMPORT_DIR = os.path.join(ROOT, "projects", "Mixing_Nuoc_Tuong_Maggi_2026", "tia_import")
BACKUP_DIR = os.path.join(ROOT, "scratch", "backup_tags")

DTYPE_BIT_WIDTH = {
    "Bool": 1,
    "Byte": 8, "SInt": 8, "USInt": 8,
    "Word": 16, "Int": 16, "UInt": 16,
    "DWord": 32, "DInt": 32, "UDInt": 32, "Real": 32, "Time": 32,
    "LWord": 64, "LInt": 64, "ULInt": 64, "LReal": 64
}

def normalize_tag_name(name):
    if name.startswith("AI_"):
        return name[3:]
    return name

def get_occupied_bits(name, address, dtype):
    # Kiểm tra kiểu dữ liệu có được hỗ trợ không (FAIL CLOSED)
    if dtype not in DTYPE_BIT_WIDTH:
        raise ValueError(f"LỖI: Tag '{name}' có kiểu dữ liệu '{dtype}' không được hỗ trợ!")
        
    # Kiểm tra định dạng địa chỉ có hợp lệ không (FAIL CLOSED)
    match = re.match(r"^%([IQM])(B|W|D|L)?(\d+)(?:\.(\d+))?$", address, re.IGNORECASE)
    if not match:
        raise ValueError(f"LỖI: Tag '{name}' có địa chỉ '{address}' không hợp lệ hoặc không parse được!")
        
    area = match.group(1).upper()
    byte_num = int(match.group(3))
    bit_group = match.group(4)
    
    width = DTYPE_BIT_WIDTH[dtype]
    
    if width == 1:
        # Kiểu Bool bắt buộc phải có bit cụ thể .0 -> .7
        if bit_group is None:
            raise ValueError(f"LỖI: Tag Bool '{name}' có địa chỉ '{address}' thiếu bit số (ví dụ: .0 -> .7)!")
        bit_num = int(bit_group)
        if bit_num < 0 or bit_num > 7:
            raise ValueError(f"LỖI: Tag Bool '{name}' có địa chỉ '{address}' với bit số ngoài khoảng 0..7!")
        return area, {byte_num * 8 + bit_num}
    else:
        # Kiểu phi-Bool không được chứa ký tự dấu chấm chỉ bit
        if bit_group is not None:
            raise ValueError(f"LỖI: Tag phi-Bool '{name}' có kiểu '{dtype}' nhưng lại khai báo bit số trong địa chỉ '{address}'!")
        return area, set(range(byte_num * 8, byte_num * 8 + width))

def parse_tags_xml(file_path):
    tags = []
    if not os.path.exists(file_path):
        return tags
    tree = ET.parse(file_path)
    root = tree.getroot()
    for tag_node in root.iter():
        tag_base = tag_node.tag.split('.')[-1]
        if tag_base == "PlcTag":
            name_node = tag_node.find(".//Name")
            addr_node = tag_node.find(".//LogicalAddress")
            type_node = tag_node.find(".//DataTypeName")
            if name_node is not None and addr_node is not None and type_node is not None:
                tags.append({
                    "name": name_node.text.strip(),
                    "address": addr_node.text.strip(),
                    "dtype": type_node.text.strip()
                })
    return tags

def check_overlaps_and_system_memory(tags, plc_name):
    occupied = {} # area -> {bit_idx -> [tag_info]}
    overlaps = []
    
    for tag in tags:
        name = tag["name"]
        addr = tag["address"]
        dtype = tag["dtype"]
        
        # 1. Lấy bit range (sẽ tự fail closed nếu địa chỉ/kiểu dữ liệu lỗi)
        area, bits = get_occupied_bits(name, addr, dtype)
        
        # 2. Kiểm tra bảo vệ System Memory (MB100 và MB101)
        norm_name = normalize_tag_name(name)
        if area == "M":
            # MB100: bits 800 -> 807
            has_mb100_overlap = any(800 <= b <= 807 for b in bits)
            if has_mb100_overlap:
                if norm_name != "Clock_1Hz" or addr != "%M100.5":
                    raise ValueError(
                        f"LỖI: Tag thông thường '{name}' ({addr}, {dtype}) trên {plc_name} "
                        f"đang sử dụng hoặc chồng lấn vào vùng nhớ Clock Memory Byte MB100 (chỉ cho phép Clock_1Hz tại %M100.5)!"
                    )
            
            # MB101: bits 808 -> 815
            has_mb101_overlap = any(808 <= b <= 815 for b in bits)
            if has_mb101_overlap:
                if norm_name != "FirstScan" or addr != "%M101.0":
                    raise ValueError(
                        f"LỖI: Tag thông thường '{name}' ({addr}, {dtype}) trên {plc_name} "
                        f"đang sử dụng hoặc chồng lấn vào vùng nhớ System Memory Byte MB101 (chỉ cho phép FirstScan tại %M101.0)!"
                    )
                    
        # 3. Điền vào bảng phân bổ và tìm trùng lấp
        if area not in occupied:
            occupied[area] = {}
        for bit in bits:
            if bit not in occupied[area]:
                occupied[area][bit] = []
            occupied[area][bit].append(tag)
            
    # Phát hiện các cặp trùng lấp
    already_reported = set()
    for area, bits_dict in occupied.items():
        for bit, tag_list in bits_dict.items():
            if len(tag_list) > 1:
                for i in range(len(tag_list)):
                    for j in range(i + 1, len(tag_list)):
                        t1 = tag_list[i]
                        t2 = tag_list[j]
                        pair_key = tuple(sorted([t1["name"], t2["name"]]))
                        if pair_key not in already_reported:
                            already_reported.add(pair_key)
                            _, bits1 = get_occupied_bits(t1["name"], t1["address"], t1["dtype"])
                            _, bits2 = get_occupied_bits(t2["name"], t2["address"], t2["dtype"])
                            common_bits = sorted(list(bits1.intersection(bits2)))
                            readable_bits = [f"%{area}{b//8}.{b%8}" for b in common_bits]
                            overlaps.append({
                                "tag1": t1,
                                "tag2": t2,
                                "area": area,
                                "common_bits": readable_bits
                            })
    return overlaps

def is_write_pin(part_name, pin_name):
    if part_name == "Contact":
        return False
    if part_name in ("Coil", "SCoil", "RCoil") and pin_name == "operand":
        return True
    if pin_name.lower() in ("out", "out1", "out2", "q", "qu", "qd", "cv", "done", "busy", "error", "status", "ndr", "dr", "in_out"):
        return True
    return False

def verify_no_writes_to_system_tags():
    print("[PHẦN 3] Xác thực LAD chỉ đọc Clock_1Hz/FirstScan (không ghi/MOVE)...")
    
    # Duyệt qua các thư mục import
    for plc_folder in ["PLC_1_Mixing_Import", "PLC_2_Mixing_Import"]:
        folder_path = os.path.join(IMPORT_DIR, plc_folder)
        if not os.path.exists(folder_path):
            continue
            
        for file_name in os.listdir(folder_path):
            if not file_name.endswith(".xml") or file_name == "PLC_Tags.xml":
                continue
                
            file_path = os.path.join(folder_path, file_name)
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                # Quét từng compile unit (network)
                for net in root.findall(".//{*}SW.Blocks.CompileUnit"):
                    title_node = net.find(".//{*}Title")
                    net_title = title_node.text.strip() if title_node is not None and title_node.text else "Không tiêu đề"
                    
                    # Ánh xạ UId phần tử sang Tên phần tử
                    part_map = {}
                    for part in net.findall(".//{*}Part"):
                        part_uid = part.attrib.get("UId")
                        part_name = part.attrib.get("Name")
                        if part_uid and part_name:
                            part_map[part_uid] = part_name
                            
                    # Ánh xạ UId Access sang Tên biến
                    access_map = {}
                    for access in net.findall(".//{*}Access"):
                        access_uid = access.attrib.get("UId")
                        if not access_uid:
                            continue
                        # Xem có phải hằng số không
                        const_val = access.find(".//{*}ConstantValue")
                        if const_val is not None:
                            access_map[access_uid] = const_val.text.strip()
                        else:
                            components = access.findall(".//{*}Component")
                            if components:
                                access_map[access_uid] = ".".join(c.attrib.get("Name", "") for c in components)
                                
                    # Kiểm tra các đường dây kết nối (Wire)
                    for wire in net.findall(".//{*}Wire"):
                        name_cons = wire.findall(".//{*}NameCon")
                        ident_cons = wire.findall(".//{*}IdentCon")
                        if not name_cons or not ident_cons:
                            continue
                            
                        for name_con in name_cons:
                            part_uid = name_con.attrib.get("UId")
                            pin_name = name_con.attrib.get("Name", "")
                            part_name = part_map.get(part_uid)
                            
                            # Nếu đây là chân ghi tín hiệu
                            if part_name and is_write_pin(part_name, pin_name):
                                for ident_con in ident_cons:
                                    access_uid = ident_con.attrib.get("UId")
                                    var_name = access_map.get(access_uid, "")
                                    norm_var = normalize_tag_name(var_name)
                                    
                                    # Nếu ghi vào Clock_1Hz hoặc FirstScan
                                    if norm_var in ("Clock_1Hz", "FirstScan"):
                                        raise ValueError(
                                            f"LỖI VI PHẠM AN TOÀN: Phát hiện lệnh ghi vào tag hệ thống '{var_name}' tại chân '{pin_name}' "
                                            f"của khối '{part_name}' (UId {part_uid}) trong Network '{net_title}' thuộc file: {file_name}!"
                                        )
            except ValueError as ve:
                raise ve
            except Exception as e:
                # Không được silently skip lỗi đọc file
                raise ValueError(f"LỖI: Không thể parse/phân tích tệp XML {file_name}: {str(e)}")
                
    print("  [PASS] Xác thực thành công: Không phát hiện bất kỳ lệnh ghi/MOVE nào tác động vào Clock_1Hz hoặc FirstScan.")

def run_overlap_validation():
    print("============================================================")
    print(" KHỞI CHẠY BỘ KIỂM TRA TRÙNG LẮP ĐỊA CHỈ PLC (OVERLAP CHECK) ")
    print("============================================================")

    # 1. Kiểm tra bản backup (Old Version)
    backup_plc1_path = os.path.join(BACKUP_DIR, "AI_Tags_PLC1.xml")
    backup_plc2_path = os.path.join(BACKUP_DIR, "AI_Tags_PLC2.xml")
    
    print("\n[PHẦN 1] Kiểm tra bản BACKUP cũ...")
    if not os.path.exists(backup_plc1_path):
        print(f"  [ERROR] Không tìm thấy file backup PLC1 tại {backup_plc1_path}")
        return False
        
    bk_tags_plc1 = parse_tags_xml(backup_plc1_path)
    bk_overlaps_plc1 = check_overlaps_and_system_memory(bk_tags_plc1, "PLC1 Backup")
    
    print(f"  PLC1 Backup: Tổng số tag = {len(bk_tags_plc1)}, phát hiện số lượng trùng lấp = {len(bk_overlaps_plc1)}")
    
    # Làm cứng khớp cặp trùng lấp backup
    expected_normalized_pairs = {
        tuple(sorted(["MB_TCP_STATUS", "Nut_Reset_Eff_Edge"])),
        tuple(sorted(["MB_TCP_STATUS", "Nut_EStop_Eff_Edge"])),
        tuple(sorted(["MB_TCP_STATUS", "Pump3265_Chuyen_Nhanh2_Cmd_Edge"])),
        tuple(sorted(["MB_TCP_STATUS", "PLC1_Load_Default_Cmd_Edge"])),
        tuple(sorted(["MB_TCP_STATUS", "MB_TCP_Any_Cmd_Edge"])),
    }
    
    actual_normalized_pairs = set()
    for o in bk_overlaps_plc1:
        n1 = normalize_tag_name(o['tag1']['name'])
        n2 = normalize_tag_name(o['tag2']['name'])
        actual_normalized_pairs.add(tuple(sorted([n1, n2])))
        print(f"    - TRÙNG LẮP: Tag '{o['tag1']['name']}' ({o['tag1']['address']}) "
              f"và Tag '{o['tag2']['name']}' ({o['tag2']['address']}) tại bits: {o['common_bits']}")
              
    if actual_normalized_pairs != expected_normalized_pairs:
        print("  [FAIL] Danh sách cặp trùng lấp thực tế khác với kỳ vọng!")
        print(f"  Kỳ vọng: {expected_normalized_pairs}")
        print(f"  Thực tế: {actual_normalized_pairs}")
        return False
    else:
        print("  [PASS] Xác nhận bản backup PLC1 phát hiện đúng và chính xác 5 cặp trùng lấp kỳ vọng tại %MW84.")

    if os.path.exists(backup_plc2_path):
        bk_tags_plc2 = parse_tags_xml(backup_plc2_path)
        bk_overlaps_plc2 = check_overlaps_and_system_memory(bk_tags_plc2, "PLC2 Backup")
        print(f"  PLC2 Backup: Tổng số tag = {len(bk_tags_plc2)}, phát hiện số lượng trùng lấp = {len(bk_overlaps_plc2)}")
        if len(bk_overlaps_plc2) != 0:
            print("  [FAIL] Bản backup PLC2 không được phép có trùng lấp địa chỉ!")
            return False
        else:
            print("  [PASS] Xác nhận bản backup PLC2 không có lỗi trùng lấp.")

    # 2. Kiểm tra bản mới sinh (New Output Version)
    new_plc1_path = os.path.join(OUTPUT_DIR, "PLC_Tags_PLC1.xml")
    new_plc2_path = os.path.join(OUTPUT_DIR, "PLC_Tags_PLC2.xml")
    
    print("\n[PHẦN 2] Kiểm tra bản OUTPUT mới sau khi sửa đổi...")
    if not os.path.exists(new_plc1_path) or not os.path.exists(new_plc2_path):
        print("  [ERROR] Không tìm thấy file tag PLC1 hoặc PLC2 mới sinh! Vui lòng generate trước.")
        return False
        
    tags_plc1 = parse_tags_xml(new_plc1_path)
    overlaps_plc1 = check_overlaps_and_system_memory(tags_plc1, "PLC1 Mới")
    print(f"  PLC1 Mới: Tổng số tag = {len(tags_plc1)}, phát hiện số lượng trùng lấp = {len(overlaps_plc1)}")
    
    tags_plc2 = parse_tags_xml(new_plc2_path)
    overlaps_plc2 = check_overlaps_and_system_memory(tags_plc2, "PLC2 Mới")
    print(f"  PLC2 Mới: Tổng số tag = {len(tags_plc2)}, phát hiện số lượng trùng lấp = {len(overlaps_plc2)}")

    # Xác nhận các tag cụ thể
    mb_tcp_status_tag = next((t for t in tags_plc1 if t["name"] == "MB_TCP_STATUS"), None)
    if not mb_tcp_status_tag:
        print("  [FAIL] Không tìm thấy tag MB_TCP_STATUS trong danh sách tag PLC1 mới sinh!")
        return False
        
    final_addr = mb_tcp_status_tag["address"]
    print(f"  Xác thực địa chỉ cuối cùng của MB_TCP_STATUS trên PLC1: {final_addr}")
    if final_addr != "%MW86":
        print(f"  [FAIL] Địa chỉ của MB_TCP_STATUS là {final_addr}, mong đợi phải là %MW86!")
        return False
        
    mb_tcp_mode_tag = next((t for t in tags_plc1 if t["name"] == "MB_TCP_Mode"), None)
    mb_tcp_dataaddr_tag = next((t for t in tags_plc1 if t["name"] == "MB_TCP_DataAddr"), None)
    
    if mb_tcp_mode_tag:
        print(f"  Xác thực địa chỉ MB_TCP_Mode: {mb_tcp_mode_tag['address']} (kỳ vọng %MB88)")
        if mb_tcp_mode_tag['address'] != "%MB88":
            print("  [FAIL] MB_TCP_Mode bị thay đổi địa chỉ ngoài ý muốn!")
            return False
    if mb_tcp_dataaddr_tag:
        print(f"  Xác thực địa chỉ MB_TCP_DataAddr: {mb_tcp_dataaddr_tag['address']} (kỳ vọng %MD90)")
        if mb_tcp_dataaddr_tag['address'] != "%MD90":
            print("  [FAIL] MB_TCP_DataAddr bị thay đổi địa chỉ ngoài ý muốn!")
            return False

    if len(overlaps_plc1) != 0 or len(overlaps_plc2) != 0:
        print("  [FAIL] Phát hiện trùng lấp địa chỉ ở chương trình đã sửa đổi!")
        return False
        
    print("  [PASS] Xác nhận bản mới sửa của cả hai PLC có 0 trùng lấp.")

    # 3. Kiểm tra ghi đè lên Clock_1Hz/FirstScan
    print("")
    verify_no_writes_to_system_tags()

    # 4. Kiểm tra trùng số khối PLC
    print("")
    from validate_block_numbers import run_block_validation
    if not run_block_validation():
        return False

    print("\n============================================================")
    print(" KẾT LUẬN: ĐẠT TIÊU CHUẨN CHẤT LƯỢNG OVERLAP QUALITY GATE!")
    print("============================================================")
    return True

if __name__ == "__main__":
    try:
        success = run_overlap_validation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Phát hiện lỗi nghiêm trọng: {str(e)}")
        sys.exit(1)
