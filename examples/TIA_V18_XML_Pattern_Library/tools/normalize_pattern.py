# -*- coding: utf-8 -*-
"""
Công cụ chuẩn hóa XML mẫu: Thay thế các thẻ và biến thật thành placeholder.
Đồng thời có thể re-index UId/ID về dạng tuần tự bắt đầu từ 1 để XML gọn gàng.
Cách dùng:
  python normalize_pattern.py --src <path_to_xml> --out <output_path> --mapping "tag_cu=tag_moi,db_cu=db_moi"
"""
import re
import os
import sys
import argparse
import xml.etree.ElementTree as ET

# Đảm bảo hiển thị Tiếng Việt trên Windows Console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Placeholder tiêu chuẩn đề xuất
STANDARD_PLACEHOLDERS = {
    "{{BOOL_IN}}": "Tiếp điểm Bool đầu vào",
    "{{BOOL_OUT}}": "Cuộn dây Bool đầu ra",
    "{{INT_A}}": "Biến số nguyên làm tham số hoặc bộ đếm",
    "{{REAL_A}}": "Biến số thực làm tham số hoặc kết quả",
    "{{DB_INSTANCE}}": "Khối DB Instance (ví dụ: IEC_TIMER_DB)",
    "{{DATA_PTR_DB}}": "Khối DB dữ liệu truyền thông",
    "{{CONNECT_DB}}": "Khối DB lưu thông số kết nối (TCON_IP_v4)"
}

def clean_and_normalize(xml_str, mapping=None):
    # Áp dụng mapping tùy chọn trước
    if mapping:
        for old_val, new_val in mapping.items():
            # Thay thế chính xác từ hoặc cụm trong attribute Name hoặc text
            xml_str = re.sub(r'\b' + re.escape(old_val) + r'\b', new_val, xml_str)

    # Re-indexing UId và ID của các element để chuẩn hóa
    try:
        # Đăng ký namespace tránh prefix ns0 tự động
        ET.register_namespace('', "http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4")
        
        # Nhận diện namespace FlgNet hoặc Openness
        # ElementTree cần parse có root hoàn chỉnh
        # Để an toàn, chúng ta re-index bằng Regex
        # UId="[0-9]+" và ID="[0-9A-F]+"
        uid_map = {}
        id_map = {}
        
        def uid_repl(match):
            old_uid = match.group(1)
            if old_uid not in uid_map:
                uid_map[old_uid] = str(len(uid_map) + 21) # Bắt đầu từ 21 giống builder
            return f'UId="{uid_map[old_uid]}"'
            
        def id_repl(match):
            old_id = match.group(1)
            if old_id not in id_map:
                id_map[old_id] = str(len(id_map) + 1) # Bắt đầu từ 1
            return f'ID="{id_map[old_id]}"'

        # Thay thế UId
        xml_str = re.sub(r'UId="([0-9a-zA-Z_]+)"', uid_repl, xml_str)
        # Thay thế ID
        xml_str = re.sub(r'ID="([0-9a-zA-Z_]+)"', id_repl, xml_str)
        
    except Exception as e:
        print(f"[WARNING] Re-indexing UId thất bại: {e}")

    return xml_str

def main():
    parser = argparse.ArgumentParser(description="Chuẩn hóa XML và thay thế biến thành placeholder.")
    parser.add_argument("--src", required=True, help="Đường dẫn file XML nguồn")
    parser.add_argument("--out", required=True, help="Đường dẫn file XML đầu ra")
    parser.add_argument("--mapping", help="Chuỗi mapping, ví dụ: 'Clock_1Hz={{BOOL_IN}},IEC_Counter_0_DB={{DB_INSTANCE}}'")

    args = parser.parse_args()

    if not os.path.exists(args.src):
        print(f"[ERROR] File nguồn không tồn tại: {args.src}")
        sys.exit(1)

    mapping_dict = {}
    if args.mapping:
        pairs = args.mapping.split(",")
        for pair in pairs:
            if "=" in pair:
                k, v = pair.split("=", 1)
                mapping_dict[k.strip()] = v.strip()

    try:
        with open(args.src, "r", encoding="utf-8") as f:
            content = f.read()
            
        normalized = clean_and_normalize(content, mapping_dict)
        
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(normalized)
            
        print(f"[SUCCESS] Đã chuẩn hóa và lưu vào: {args.out}")
    except Exception as e:
        print(f"[ERROR] Quá trình chuẩn hóa thất bại: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
